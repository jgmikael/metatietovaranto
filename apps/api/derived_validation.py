"""Offline schema/example checks and explicit, deliberately limited SHACL coverage."""
import hashlib
import importlib.metadata
import json
import multiprocessing
import re
from datetime import datetime, timezone

from jsonschema import validators, FormatChecker
from jsonschema.exceptions import SchemaError
from openapi_schema_validator import OAS30Validator, OAS31Validator
from openapi_spec_validator import OpenAPIV30SpecValidator, OpenAPIV31SpecValidator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT4, DRAFT6, DRAFT7, DRAFT201909, DRAFT202012
from rdflib import RDF, SH, URIRef, Literal

from apps.api.profiles import checksum
from apps.api.semantic_validation import locked_graph

POLICY = 'derived-offline-direct-fields-v1'
ENGINE = ';'.join(name+'/'+importlib.metadata.version(name) for name in
                  ('jsonschema','openapi-schema-validator','openapi-spec-validator'))
MAX_RESULTS = 100
RESOURCE_URI = 'https://locked.invalid/derivative'
DIALECTS = {
    'http://json-schema.org/draft-04/schema#': (validators.Draft4Validator,DRAFT4),
    'http://json-schema.org/draft-06/schema#': (validators.Draft6Validator,DRAFT6),
    'http://json-schema.org/draft-07/schema#': (validators.Draft7Validator,DRAFT7),
    'https://json-schema.org/draft/2019-09/schema': (validators.Draft201909Validator,DRAFT201909),
    'https://json-schema.org/draft/2020-12/schema': (validators.Draft202012Validator,DRAFT202012),
}
for uri, pair in list(DIALECTS.items()):
    DIALECTS[uri.rstrip('#')] = pair


class Unsupported(ValueError):
    pass


def strict_json(content):
    def pairs(values):
        obj = {}
        for key,value in values:
            if key in obj:raise ValueError('Duplicate JSON key')
            obj[key] = value
        return obj
    def constant(value):raise ValueError('Non-JSON numeric constant')
    return json.loads(content,object_pairs_hook=pairs,parse_constant=constant)


def pointer(doc, path):
    if path=='':return doc
    if not path.startswith('/') or re.search(r'~(?![01])',path):raise ValueError('Invalid JSON Pointer')
    value=doc
    for part in path[1:].split('/'):
        key=part.replace('~1','/').replace('~0','~')
        if isinstance(value,list):
            if not re.fullmatch(r'0|[1-9][0-9]*',key):raise ValueError('Invalid array index')
            value=value[int(key)]
        else:value=value[key]
    return value


def local_schema(doc, schema):
    seen=set()
    while isinstance(schema,dict) and '$ref' in schema:
        ref=schema['$ref']
        if ref in seen:raise Unsupported('Syklinen rakenne ei sovellu suoraan kenttäkartoitukseen')
        seen.add(ref)
        if set(schema)-{'$ref','$comment','description','title'}:
            raise Unsupported('$ref-viitteen rinnakkaisia rajoitteita ei litistetä kartoituksessa')
        schema=pointer(doc,ref[1:])
    return schema


def preflight(doc):
    count=0
    def visit(value,depth=0,root=False):
        nonlocal count
        count+=1
        if depth>40 or count>20000:raise Unsupported('JSON-rakenteen syvyys- tai solmuraja ylittyi')
        if isinstance(value,dict):
            if '$dynamicRef' in value or '$recursiveRef' in value:
                raise Unsupported('Dynaamisia/rekursiivisia viitteitä ei tueta tässä validointiprofiilissa')
            if not root and '$id' in value:
                raise Unsupported('Sisäkkäinen $id edellyttää erillistä resurssirekisteriä')
            for key,item in value.items():
                if key=='$ref':
                    if not isinstance(item,str) or not item.startswith('#/'):
                        raise Unsupported('Vain saman lukitun tiedoston JSON Pointer -viitteet ovat sallittuja')
                    pointer(doc,item[1:])
                visit(item,depth+1)
        elif isinstance(value,list):
            for item in value:visit(item,depth+1)
    visit(doc,root=True)


def issue(rule,message,**extra):
    return {'ruleId':rule,'message':message,**extra}


def dialect(doc,kind):
    if kind=='jsonSchema':
        uri=doc.get('$schema')
        if uri not in DIALECTS:raise Unsupported('JSON Scheman alkuperäinen $schema-dialekti puuttuu tai sitä ei tueta')
        return (*DIALECTS[uri],uri,None)
    version=doc.get('openapi','')
    if re.fullmatch(r'3\.0\.\d+',version):return OAS30Validator,DRAFT4,version,OpenAPIV30SpecValidator
    if re.fullmatch(r'3\.1\.\d+',version):
        if doc.get('jsonSchemaDialect','https://spec.openapis.org/oas/3.1/dialect/base') not in (
            'https://spec.openapis.org/oas/3.1/dialect/base','https://json-schema.org/draft/2020-12/schema'):
            raise Unsupported('OpenAPI käyttää tukematonta schema-dialektia')
        return OAS31Validator,DRAFT202012,version,OpenAPIV31SpecValidator
    raise Unsupported('Tuetut OpenAPI-versiot ovat 3.0.x ja 3.1.x; versiota ei muuteta')


def no_retrieve(uri):raise Unsupported('Ulkoinen skeemaviite estetty')


def coverage(graph, doc, schema, mappings, instance):
    """Assess direct root properties only, never infer semantics from a field name."""
    rows=[];problems=[];index={};used=set()
    for mapping in mappings:
        key=(mapping['shapeUri'],mapping['semanticUri'])
        if key in index:problems.append(issue('MAPPING_DUPLICATE','Samalle muoto/termi-parille on useita kartoituksia'))
        index[key]=mapping
    try:schema=local_schema(doc,schema)
    except Unsupported as error:return [],[issue('MAPPING_UNASSESSED',str(error))]
    if not isinstance(schema,dict) or schema.get('type')!='object':
        return [],[issue('MAPPING_UNASSESSED','Kartoitus tukee yhtä suoraa JSON-objektia')]
    root_allowed={'type','properties','required','additionalProperties','$schema','$id','definitions','$defs',
                  'title','description','$comment','examples','example','deprecated'}
    if set(schema)-root_allowed:
        problems.append(issue('MAPPING_UNASSESSED','JSON-juuressa on rajoitteita, joita suora kenttävertailu ei käsittele'))
    if schema.get('additionalProperties') is not False:
        problems.append(issue('MAPPING_UNASSESSED','Suora kartoitus edellyttää additionalProperties:false-rajausta'))
    properties=schema.get('properties',{});required=schema.get('required',[])
    covered_fields=set()
    allowed_node={SH.property,SH.targetClass,SH.targetNode,SH.targetSubjectsOf,SH.targetObjectsOf,
                  SH.name,SH.description,SH.order,SH.group,SH.deactivated,SH.severity,SH.message}
    allowed_prop={SH.path,SH.datatype,SH.minCount,SH.maxCount,SH.name,SH.description,SH.order,SH.group,
                  SH.deactivated,SH.severity,SH.message,SH['in'],SH.defaultValue}
    type_map={'string':'string','boolean':'boolean','integer':'integer','int':'integer','long':'integer',
              'short':'integer','byte':'integer','decimal':'number','double':'number','float':'number'}
    for shape in sorted(set(graph.subjects(RDF.type,SH.NodeShape)),key=str):
        if graph.value(shape,SH.deactivated)==Literal(True):continue
        if any(str(p).startswith(str(SH)) and p not in allowed_node for p in graph.predicates(shape)):
            problems.append(issue('MAPPING_UNASSESSED','Luokkamuodon kaikkia rajoitteita ei voi verrata suorina JSON-kenttinä',shapeUri=str(shape)))
        for prop in sorted(graph.objects(shape,SH.property),key=str):
            if graph.value(prop,SH.deactivated)==Literal(True):continue
            path=graph.value(prop,SH.path);key=(str(shape),str(path))
            row={'shapeUri':str(shape),'propertyShapeUri':str(prop) if isinstance(prop,URIRef) else None,
                 'semanticUri':str(path) if isinstance(path,URIRef) else None,'status':'notAssessed','checks':[]}
            rows.append(row)
            mapping=index.get(key)
            if not isinstance(path,URIRef) or mapping is None:
                problems.append(issue('MAPPING_MISSING','Semanttinen kenttäkartoitus puuttuu tai SHACL-polku on monimutkainen',**{k:row[k] for k in ('shapeUri','semanticUri')}));continue
            used.add(key);field=mapping['propertyName'];row['propertyName']=field
            if field in covered_fields:
                problems.append(issue('MAPPING_DUPLICATE','Sama JSON-kenttä on kohdistettu useaan semanttiseen kohtaan',propertyName=field));continue
            covered_fields.add(field)
            try:field_schema=local_schema(doc,properties[field])
            except (KeyError,Unsupported):
                problems.append(issue('MAPPING_FIELD','Kartoituksen JSON-kenttää ei löydy tai sen viite ei ole suora',propertyName=field));continue
            if not isinstance(field_schema,dict):
                problems.append(issue('MAPPING_UNASSESSED','Boolean-skeemaa ei voi verrata kenttänä',propertyName=field));continue
            array=field_schema.get('type')=='array'
            value_schema=local_schema(doc,field_schema.get('items',{})) if array else field_schema
            allowed={'type','enum','title','description','$comment','default','example','examples','deprecated'}
            if array:allowed|={'items','minItems','maxItems'}
            unsupported=(any(str(p).startswith(str(SH)) and p not in allowed_prop for p in graph.predicates(prop))
                or bool(set(field_schema)-allowed) or not isinstance(value_schema,dict)
                or bool(set(value_schema)-{'type','enum','title','description','$comment','default','example','examples','deprecated'}))
            if unsupported:
                problems.append(issue('MAPPING_UNASSESSED','Kentässä on rajoitteita, joita tyyppi/kardinaliteetti/koodisto-vertailu ei käsittele',propertyName=field));continue
            datatype=graph.value(prop,SH.datatype)
            expected=type_map.get(str(datatype).removeprefix('http://www.w3.org/2001/XMLSchema#')) if datatype else None
            if not expected:
                problems.append(issue('MAPPING_UNASSESSED','SHACL-tietotyypin suoraa JSON-vastinetta ei tueta',propertyName=field));continue
            minimum=int(graph.value(prop,SH.minCount) or 0)
            maximum=graph.value(prop,SH.maxCount);maximum=int(maximum) if maximum is not None else None
            json_min=(field_schema.get('minItems',0) if array else 1) if field in required else 0
            json_max=field_schema.get('maxItems') if array else 1
            row['checks']=[{'kind':'datatype','shacl':str(datatype),'json':value_schema.get('type'),'matches':value_schema.get('type')==expected},
                {'kind':'cardinality','shacl':[minimum,maximum],'json':[json_min,json_max],'matches':(minimum,maximum)==(json_min,json_max)}]
            in_list=graph.value(prop,SH['in'])
            if in_list is not None:
                values=list(graph.items(in_list))
                if any(not isinstance(item,Literal) for item in values):
                    problems.append(issue('MAPPING_UNASSESSED','IRI-koodisto vaatii erillisen semanttisen kartoituksen',propertyName=field));continue
                left={json.dumps(item.toPython(),sort_keys=True) for item in values}
                right={json.dumps(item,sort_keys=True) for item in value_schema.get('enum',[])}
                row['checks'].append({'kind':'enum','matches':left==right})
            elif 'enum' in value_schema:
                row['checks'].append({'kind':'enum','matches':False})
            row['status']='direct' if all(check['matches'] for check in row['checks']) else 'conflict'
            if row['status']=='conflict':problems.append(issue('MAPPING_CONFLICT','JSON-skeeman tietotyyppi, kardinaliteetti tai koodisto poikkeaa SHACL-rajoitteesta',propertyName=field))
    if not rows:problems.append(issue('MAPPING_MISSING','Profiilissa ei ole vertailtavia ominaisuuksia'))
    if set(index)-used:problems.append(issue('MAPPING_UNKNOWN','Kartoitus viittaa profiilista puuttuvaan tai deaktivoituun semanttiseen kohtaan'))
    if (set(properties) | (set(instance) if isinstance(instance,dict) else set()))-covered_fields:
        problems.append(issue('MAPPING_MISSING','JSON-kenttiä jää semanttisen kartoituksen ulkopuolelle'))
    return rows,problems


def artifact_report(artifact,example,graph):
    report={'artifactId':artifact['id'],'sha256':artifact['sha256'],'kind':artifact['serialization'],
            'dialect':artifact.get('dialect'),'schemaPointer':artifact.get('schemaPointer',''),
            'status':'invalid','schemaValid':False,'exampleValid':False,'coverage':[],'results':[]}
    try:
        if hashlib.sha256(artifact['content'].encode()).hexdigest()!=artifact['sha256']:raise ValueError('Checksum mismatch')
        doc=strict_json(artifact['content'])
        if not isinstance(doc,dict):raise ValueError('Schema must be an object')
        preflight(doc)
        cls,specification,original,spec_validator=dialect(doc,artifact['serialization'])
        report['dialect']=original
        if spec_validator:
            errors=list(spec_validator(doc).iter_errors())
            if errors:
                report['results']=[issue('OPENAPI_STRUCTURE','OpenAPI-dokumentti ei läpäise alkuperäisen version rakennetta',schemaPath='/'+'/'.join(map(str,error.absolute_path))) for error in errors[:MAX_RESULTS]]
                return report
        selected=artifact.get('schemaPointer','')
        if artifact['serialization']=='openapi' and not selected:raise Unsupported('OpenAPI-johdannaiselle tarvitaan skeeman JSON Pointer')
        if artifact['serialization']=='openapi' and not re.fullmatch(r'/components/schemas/[^/]+',selected):
            raise Unsupported('Valitse yksi OpenAPI components/schemas -sisältöskeema')
        schema=pointer(doc,selected)
        if artifact['serialization']=='jsonSchema':cls.check_schema(doc)
        cls.check_schema(schema)
        report['schemaValid']=True
        if not example:
            report['results']=[issue('JSON_EXAMPLE_REQUIRED','Johdannaisen synteettinen JSON-esimerkki puuttuu')];return report
        instance=strict_json(example['content'])
        registry=Registry(retrieve=no_retrieve).with_resource(RESOURCE_URI,Resource(doc,specification))
        checker=cls.FORMAT_CHECKER if artifact['serialization']=='openapi' else FormatChecker()
        validator=cls({'$ref':RESOURCE_URI+'#'+selected},registry=registry,format_checker=checker)
        errors=[]
        for error in validator.iter_errors(instance):
            errors.append(issue('JSON_SCHEMA_'+str(error.validator),'JSON-esimerkki rikkoo skeeman sääntöä: '+str(error.validator),instancePath='/'+'/'.join(str(part).replace('~','~0').replace('/','~1') for part in error.absolute_path)))
            if len(errors)>=MAX_RESULTS:break
        report['exampleValid']=not errors
        report['coverage'],problems=coverage(graph,doc,schema,artifact.get('semanticMappings',[]),instance)
        findings=errors+problems
        report['resultCount']=len(findings);report['truncated']=len(findings)>MAX_RESULTS or len(report['coverage'])>MAX_RESULTS
        report['results']=findings[:MAX_RESULTS];report['coverage']=report['coverage'][:MAX_RESULTS]
        report['status']='conforms' if not findings else 'invalid'
    except Unsupported as error:report['results']=[issue('DERIVED_UNSUPPORTED',str(error))]
    except SchemaError as error:report['results']=[issue('JSON_SCHEMA_STRUCTURE','JSON Schema ei läpäise alkuperäisen dialektin rakennetarkistusta',schemaPath='/'+'/'.join(map(str,error.absolute_path)))]
    except Exception:report['results']=[issue('DERIVED_INVALID','Johdannaisen syntaksi, viite, kartoitus tai esimerkkisisältö on virheellinen')]
    return report


def reports(manifest,examples):
    artifacts=[item for item in manifest['derivedArtifacts'] if item['serialization'] in ('jsonSchema','openapi')]
    graph=locked_graph(manifest)
    by_id={item['artifactId']:item for item in examples}
    items=[artifact_report(artifact,by_id.get(artifact['id']),graph) for artifact in artifacts]
    errors=[]
    if set(by_id)-{item['id'] for item in artifacts}:errors.append(issue('DERIVED_UNKNOWN','Esimerkki viittaa valitusta snapshotista puuttuvaan johdannaiseen'))
    return {'status':'conforms' if not errors and all(item['status']=='conforms' for item in items) else 'invalid',
            'artifacts':items,'results':errors}


def _worker(manifest,examples,writer):
    try:
        import resource,socket
        resource.setrlimit(resource.RLIMIT_CPU,(5,5))
        resource.setrlimit(resource.RLIMIT_AS,(512*1024*1024,512*1024*1024))
        def offline(*args,**kwargs):raise Unsupported('Validointi on verkoton')
        socket.socket.connect=offline;socket.socket.connect_ex=offline;socket.getaddrinfo=offline
        writer.send(reports(manifest,examples))
    except Exception:
        writer.send({'status':'error','artifacts':[],'results':[issue('DERIVED_ERROR','Johdannaisten validointi epäonnistui')]})
    finally:writer.close()


def validate_derived(snapshot,examples):
    artifacts=[item for item in snapshot.manifest['derivedArtifacts'] if item['serialization'] in ('jsonSchema','openapi')]
    if not artifacts and not examples:return None
    context=multiprocessing.get_context('spawn');reader,writer=context.Pipe(duplex=False)
    process=context.Process(target=_worker,args=(snapshot.manifest,examples,writer));process.start();writer.close()
    try:
        if not reader.poll(15):raise ValueError('Timeout')
        try:report=reader.recv()
        except EOFError:raise ValueError('Resource limit') from None
    except ValueError:
        report={'status':'error','artifacts':[],'results':[issue('DERIVED_RESOURCE_LIMIT','Johdannaisten validoinnin aika- tai resurssiraja ylittyi')]}
    finally:
        reader.close();process.join(.2)
        if process.is_alive():process.terminate();process.join(1)
    return report|{'policy':POLICY,'engine':ENGINE,'profileSnapshotSha256':snapshot.checksum,
        'examplesHash':checksum(examples),'checkedAt':datetime.now(timezone.utc).isoformat()}


def derived_errors(snapshot,body):
    artifacts=[item for item in snapshot.manifest['derivedArtifacts'] if item['serialization'] in ('jsonSchema','openapi')]
    examples=body.get('derivedExamples',[])
    if not artifacts and not examples:return []
    report=body.get('derivedValidation')
    if not report or report.get('policy')!=POLICY or report.get('engine')!=ENGINE or report.get('profileSnapshotSha256')!=snapshot.checksum or report.get('examplesHash')!=checksum(examples):
        return [{'path':'/derivedExamples','ruleId':'DERIVED_REPORT_REQUIRED','message':'Ajantasainen johdannaisten raportti puuttuu. Täydennä JSON-esimerkit ja tallenna luonnos.'}]
    if report['status']=='conforms':return []
    issues=list(report.get('results',[]))
    for item in report.get('artifacts',[]):issues+=item.get('results',[])
    return [{'path':'/derivedExamples','ruleId':item['ruleId'],'message':item['message']} for item in issues[:MAX_RESULTS]] or [{'path':'/derivedExamples','ruleId':'DERIVED_FAILED','message':'Johdannaisten tarkistus ei läpäissyt'}]
