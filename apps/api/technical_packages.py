from apps.api.representations import LANGUAGE_PROFILE,REFERENCE_PROFILE,LANG_SCHEMA,LANG_CONTEXT,IRI_PATTERN,reference_class,reference_nodes,RepresentationError
"""Deterministic, bounded SHACL-derived description packages. No credential issuance."""
import copy
import hashlib
import json
import multiprocessing
import re
from pathlib import Path
from typing import Literal as Choice

from pydantic import Field
from rdflib import Graph, Literal, RDF, SH, URIRef, XSD
from apps.api.semantic_extension import attach_references, enrich, source_pins, VERSION as EXTENSION_VERSION
from rdflib.compare import isomorphic, to_canonical_graph
from jsonschema import Draft202012Validator
from pyld import jsonld

from apps.api.datatype_policy import datatype_issue, assess_range, term_info, RANGE_POLICY
from apps.api.shacl_cardinality import read_count, CardinalityError
from apps.api.contracts import Contract
from apps.api.profiles import checksum, canonical, Iri
from apps.api.semantic_validation import locked_graph, validation_report, ENGINE as SHACL_ENGINE
from apps.api.conversion import bounded_json, convert, tokens

GENERATOR = 'technical-package/1.2.0'
POLICY = 'shacl-tree-json-v1'
SD_STANDARD = 'draft-ietf-oauth-sd-jwt-vc-19'
STANDARDS = {'sdJwtVc': SD_STANDARD, 'vcdm': '2.0', 'jsonLd': '1.1', 'jsonSchema': '2020-12', 'mtvSemanticExtension': EXTENSION_VERSION}
BASE_CONTEXT = 'https://www.w3.org/ns/credentials/v2'
FIXTURES = Path(__file__).resolve().parents[2] / 'fixtures' / 'standards'
DATATYPES = {'string','boolean','integer','nonNegativeInteger','positiveInteger','decimal','double','date','dateTime','anyURI'}
RESERVED = {'id','type','issuer','credentialSubject','credentialStatus','validFrom','validUntil','proof',
            'iss','sub','aud','jti','iat','exp','nbf','vct','aka_vcts','cnf','status','_sd','_sd_alg','...', '__proto__','constructor','prototype'}
# Reject protected VCDM terms before JSON-LD processing, including name/description/mediaType.
RESERVED |= {term for term in json.loads((FIXTURES/'credentials-v2.jsonld').read_text())['@context'] if not term.startswith('@')}
ANNOTATIONS = {'name','description','order','group','message','severity','defaultValue'}
NODE_ALLOWED = ANNOTATIONS | {'property','targetClass','closed','ignoredProperties'}
PROP_ALLOWED = ANNOTATIONS | {'path','datatype','node','class','nodeKind','minCount','maxCount'}


class RepresentationName(Contract):
    semanticPath: list[Iri] = Field(min_length=1, max_length=10)
    fieldName: str = Field(min_length=1, max_length=100, pattern=r'^[A-Za-z][A-Za-z0-9_]*$')


class ProposalRequest(Contract):
    rootShapeUri: Iri = Field(min_length=1, max_length=2048)
    names: list[RepresentationName] = Field(default_factory=list, max_length=200)
    languageRepresentation: Choice['valueLanguage-v1']|None=None
    references: list[list[Iri]] = Field(default_factory=list,max_length=200)


class PackageRequest(ProposalRequest):
    acceptRepresentation: Choice[True]
    replaceMappings: bool = False
    mappingVersion: str = Field(default='1.0.0', pattern=r'^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$')
    exampleContent: str = Field(min_length=1, max_length=100000)
    synthetic: Choice[True]
    # No default acknowledgement: these choices are explicitly reviewed, never inferred from SHACL.
    acceptFormatPolicies: Choice[True]


class GenerationError(ValueError):
    def __init__(self, rule, path, message):
        self.finding = {'ruleId':rule, 'path':path, 'message':message}


def fail(rule, path, message):raise GenerationError(rule, path, message)


def technical_name(iri):
    local = re.split(r'[/#:]', iri.rstrip('/#'))[-1]
    # ASCII technical local names only; translated labels never determine names.
    if re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*', local):return local
    return 'field_' + hashlib.sha256(iri.encode()).hexdigest()[:12]


def inspect_profile(manifest, root_uri, names, diagnostics=None, choices=None):
    source_locations={}
    graph = locked_graph(manifest,preserve_turtle_lexical=True,source_locations=source_locations)
    root = URIRef(root_uri)
    if (root, RDF.type, SH.NodeShape) not in graph:fail('ROOT_SHAPE', root_uri, 'Valitse lähteessä oleva IRI-luokkamuoto')
    overrides = {tuple(row['semanticPath']):row['fieldName'] for row in names}
    if len(overrides) != len(names):fail('NAME_DUPLICATE', root_uri, 'Saman semanttisen polun valinta on annettu kahdesti')
    choices=choices or {}; references={tuple(p) for p in choices.get('references',[])};used_references=set()
    if any(not p or len(p)>8 for p in references):fail('REFERENCE_UNKNOWN',root_uri,'Viittaus tarvitsee 1–8 semanttista ominaisuus-IRI:tä')
    fields = []; used_overrides = set()
    def one(node, predicate, required=False):
        values = list(graph.objects(node, predicate))
        if len(values)>1 or required and len(values)!=1:fail('SHACL_AMBIGUOUS', str(node), 'Tarvitaan yksi '+str(predicate))
        return values[0] if values else None
    def supported(node, allowed):
        for p in sorted(set(graph.predicates(node)), key=str):
            if str(p).startswith(str(SH)) and str(p)[len(str(SH)):] not in allowed:
                fail('SHACL_UNSUPPORTED', str(node), 'Generointiprofiilin ulkopuolinen rajoite: '+str(p))
    def visit(shape, path, field_path, ancestors, declared_class=None, constraint_path=None):
        if shape in ancestors or len(path)>8:fail('RECURSION', '/'.join(path), 'Rekursio tai yli kahdeksan tason rakenne ei ole tuettu')
        supported(shape, NODE_ALLOWED)
        cls = one(shape, SH.targetClass, required=(not path)) or declared_class
        if not isinstance(cls, URIRef):fail('CLASS_REQUIRED', str(shape), 'Oliolle tarvitaan yksiselitteinen luokka-IRI')
        if declared_class and cls != declared_class:fail('CLASS_CONFLICT', str(shape), 'sh:class ja sisäkkäisen muodon kohdeluokka eroavat')
        # Closed shapes are retained for SHACL; emitted rdf:type must be allowed explicitly.
        if one(shape, SH.closed) == Literal(True):
            ignored = one(shape, SH.ignoredProperties)
            if not ignored or RDF.type not in list(graph.items(ignored)):
                fail('CLOSED_TYPE', str(shape), 'Suljetun muodon on sallittava generoitu rdf:type ignoredProperties-listassa')
        result = {'shapeUri':str(shape), 'classUri':str(cls), 'fields':[]}
        properties = {}
        for prop in graph.objects(shape, SH.property):
            if not list(graph.objects(prop,SH.path)):
                error=GenerationError('PATH_REQUIRED',str(prop),'sh:path puuttuu. Sisältöominaisuutta ei päätellä nimestä tai ylaluokkaviitteestä; korjaa lähdeprofiili.')
                error.finding.update(category='sourceError',rootShapeUri=root_uri,nodeShapeUri=str(shape),predicate=str(SH.path),propertyShapes=[{'uri':str(prop) if isinstance(prop,URIRef) else None,'kind':'iri' if isinstance(prop,URIRef) else 'blankNode','localIndex':1,'sources':sorted(source_locations.get(prop,set())),'labels':[]}]);raise error
            predicate = one(prop, SH.path, True)
            properties.setdefault(predicate, []).append(prop)
        if not properties:fail('EMPTY_SHAPE', str(shape), 'Tyhjä sisältömuoto ei riitä valmiiksi kuvaukseksi')
        siblings = set(); paths = set()
        # Order cannot depend on blank node IDs or Turtle statement order.
        for predicate, group in sorted(properties.items(), key=lambda item:str(item[0])):
            group.sort(key=str); prop=group[0]
            for member in group:supported(member, PROP_ALLOWED)
            def group_values(predicate):
                return set(value for member in group for value in graph.objects(member,predicate))
            def read(predicate):
                values=group_values(predicate)
                if len(values)>1:fail('PROPERTY_CONSTRAINT_UNSUPPORTED',str(predicate),'Saman polun rajoitteille ei voida johtaa yhtä arvotyyppiä; generaattorin tukirajoite, ei SHACL-syntaksivirhe')
                return next(iter(values),None)
            if len(group)>1:
                if str(predicate)=='http://www.w3.org/2002/07/owl#topObjectProperty':
                    fail('SEMANTIC_TOP_PROPERTY',str(predicate),'Useat rajoitteet käyttävät owl:topObjectProperty-polkua: '+', '.join(str(p) for p in group)+'. Generaattori ei voi päätellä niistä eri sisältöominaisuuksia; korjaa lähdemallin tarkoitetut polut. Ei itsessään SHACL-syntaksivirhe.')
                if any(not isinstance(member,URIRef) for member in group) or not group_values(SH.datatype):fail('PROPERTY_CONSTRAINT_UNSUPPORTED',str(predicate),'Saman polun yhdistäminen tarvitsee yksiselitteiset nimetyt PropertyShapet ja yhden literaalityypin; generaattorin tukirajoite')
            predicate = one(prop, SH.path, True)
            if not isinstance(predicate, URIRef):fail('COMPLEX_PATH', str(shape), 'Vain suora ominaisuus-IRI-polku tuetaan')
            paths.add(predicate); semantic = path+[str(predicate)]
            try:
                low=max(read_count(one(member,SH.minCount),0) for member in group)
                maxima=[read_count(one(member,SH.maxCount),None) for member in group]
                high=min((value for value in maxima if value is not None),default=None)
            except CardinalityError as error:fail(error.code,str(predicate),str(error))
            if high is not None and high<low:fail('CARDINALITY_CONFLICT',str(predicate),'Samalle polulle kohdistuvien määrärajoitteiden leikkaus on tyhjä: maxCount on minCountia pienempi.')
            datatype = read(SH.datatype); node = read(SH.node); obj_class = read(SH['class'])
            node_kind = read(SH.nodeKind)
            is_reference=tuple(semantic) in references
            ranges = sorted(set(graph.objects(predicate,URIRef(RANGE_POLICY['range']))),key=str)
            def diagnostic(rule,category,message,suggestion=None,observed=datatype,predicate_uri=SH.datatype,owl_ranges=None):
                finding={'ruleId':rule,'path':str(predicate),'message':message,'category':category,
                         'rootShapeUri':root_uri,'nodeShapeUri':str(shape) if isinstance(shape,URIRef) else None,
                         'predicate':str(predicate_uri),'observed':term_info(observed) if observed is not None else None,
                         'expected':('IRI' if rule=='DATATYPE_TERM' else 'Hyväksytty valueLanguage-v1-esitys' if rule=='LANGUAGE_REPRESENTATION_REQUIRED' else 'Lähderajoitteet täyttävä kohde-esitys' if rule in ('REFERENCE_UNSUPPORTED','RECURSION') else 'Yksiselitteinen tuettu SHACL-literaalityyppi'),
                         'propertyShapes':[{'uri':str(p) if isinstance(p,URIRef) else None,'kind':'iri' if isinstance(p,URIRef) else 'blankNode','localIndex':i+1,'sources':sorted(source_locations.get(p,set())),'labels':sorted(str(v) for pred in (SH.name,URIRef('http://www.w3.org/2000/01/rdf-schema#label')) for v in graph.objects(p,pred) if isinstance(v,Literal))} for i,p in enumerate(group)],
                         'owlRanges':[term_info(r)|{'sources':sorted(source_locations.get(predicate,set()))} for r in (ranges if owl_ranges is None else owl_ranges)]}
                if suggestion:finding['suggestion']=suggestion
                if category!='warning':
                    error=GenerationError(rule,str(predicate),message);error.finding=finding;raise error
                if diagnostics is not None:diagnostics.append(finding)
            issue=datatype_issue(datatype,node_kind,{str(XSD)+value for value in DATATYPES}|{str(RDF.langString)})
            if issue:diagnostic(*issue,observed=datatype if datatype is not None else node_kind,predicate_uri=SH.datatype if datatype is not None else SH.nodeKind)
            if datatype==RDF.langString and choices.get('languageRepresentation')!=LANGUAGE_PROFILE:diagnostic('LANGUAGE_REPRESENTATION_REQUIRED','decisionRequired','Hyväksy value/language-v1-kieliesitys ennen ehdotusta. Lähteen kielitietoa ei poisteta.')
            if not is_reference and node_kind is not None and (node_kind != SH.Literal or datatype is None):
                fail('NODE_KIND_UNSUPPORTED',str(predicate),'Vain konkreettista literaalityyppiä täydentävä sh:nodeKind sh:Literal on tuettu')
            if datatype and (node or obj_class):fail('VALUE_AMBIGUOUS', str(predicate), 'Kenttä ei voi olla sekä literaali että olio')
            if datatype is not None:
                for owl_range in ranges:diagnostic(*assess_range(graph,datatype,owl_range),owl_ranges=[owl_range])
            if is_reference:
                try:obj_class=reference_class(graph,prop)
                except (RepresentationError,ValueError) as error:diagnostic('REFERENCE_UNSUPPORTED','generatorLimit',str(error),observed=obj_class,predicate_uri=SH['class'])
                used_references.add(tuple(semantic))
            if not is_reference and not datatype and node is None and obj_class:
                candidates = list(graph.subjects(SH.targetClass,obj_class))
                if len(candidates)==1:node=candidates[0]
            if not is_reference and not datatype and node is None:fail('OBJECT_AMBIGUOUS', str(predicate), 'Oliolle tarvitaan yksi lukittu sisäkkäinen muoto')
            explicit = list(group_values(URIRef('http://uri.suomi.fi/datamodel/ns/iow#localName')))
            explicit += [Literal(m['propertyName']) for a in manifest.get('derivedArtifacts',[]) for m in a.get('semanticMappings',[])
                         if m['shapeUri']==str(shape) and m['semanticUri']==str(predicate)]
            explicit = {str(value) for value in explicit}
            if len(explicit)>1:fail('TECHNICAL_NAME_AMBIGUOUS', str(predicate), 'Lähteen eksplisiittiset tekniset nimet eroavat')
            name = next(iter(explicit)) if explicit else technical_name(str(predicate))
            origin = 'explicitSource' if explicit else 'iriLocalNameOrHash'
            if tuple(semantic) in overrides:
                name = overrides[tuple(semantic)];used_overrides.add(tuple(semantic));origin='reviewedChoice'
            if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*',name) or name in RESERVED or name.startswith('Class_'):
                fail('RESERVED_NAME', str(predicate), 'Varattu tai virheellinen tekninen nimi: '+name)
            if name in siblings:fail('NAME_COLLISION', str(predicate), 'Nimi törmää samassa oliossa: '+name)
            siblings.add(name)
            multi = high != 1
            pointer = field_path+'/'+name+('/*' if multi else '')
            labels = sorted((str(v.language or 'und'),str(v)) for v in group_values(SH.name))
            entry = {'shapeUri':root_uri,'semanticPath':semantic,'fieldPath':pointer,'valueKind':'literal' if datatype else 'object',
                     'datatype':str(datatype) if datatype else None,'classUri':str(obj_class) if is_reference else None,**({'representation':'iriReference'} if is_reference else {}),'minCount':low,'maxCount':high,'disclosure':None}
            locator=(constraint_path or [])+[{'nodeShapeUri':str(shape) if isinstance(shape,URIRef) else None,'propertyPath':str(predicate),'propertyShapeUri':str(prop) if isinstance(prop,URIRef) else None}]
            row = {'shacl':{'nodeShapeUri':str(shape) if isinstance(shape,URIRef) else None,'propertyShapeUri':str(prop) if isinstance(prop,URIRef) else None,'propertyShapeKind':'iri' if isinstance(prop,URIRef) else 'blankNode','constraintPath':locator},'name':name,'nameOrigin':origin,'labels':[{'locale':lang,'label':label} for lang,label in labels],
                   'mapping':entry,'multi':multi}
            if not is_reference and node is not None:
                try:child=visit(node,semantic,pointer,ancestors|{shape},obj_class,locator)
                except GenerationError as error:
                    if error.finding['ruleId']=='RECURSION' and not error.finding.get('propertyShapes'):diagnostic('RECURSION','generatorLimit','Rekursio ei kuulu sisäkkäiseen esitykseen. Tarkasta IRI-viittauksen mahdollisuus ennen ehdotusta; pakollista kohdesisältöä tai sh:node-rajoitetta ei voi ohittaa.',observed=node,predicate_uri=SH.node if read(SH.node) else SH['class'])
                    raise
                entry['classUri']=child['classUri'];row['child']=child
            if len(group)>1:
                row['shacl']['contributingConstraints']=[{'nodeShapeUri':str(shape) if isinstance(shape,URIRef) else None,'propertyPath':str(predicate),'propertyShapeUri':str(member)} for member in group]
            fields.append(row);result['fields'].append(row)
            if len(fields)>200:fail('FIELD_LIMIT', root_uri, 'Enintään 200 kenttää')
        return result
    tree = visit(root,[], '',set())
    if references-used_references:fail('REFERENCE_UNKNOWN',root_uri,'Viittausvalinta ei kohdistu käsiteltyyn ominaisuuspolkuun')
    if set(overrides)-used_overrides:fail('NAME_UNKNOWN', root_uri, 'Nimivalinta viittaa puuttuvaan semanttiseen polkuun')
    # Flatten in parent-first semantic order, independently of graph iteration.
    def flatten(node):
        out=[]
        for row in node['fields']:
            out.append(row)
            if 'child' in row:out.extend(flatten(row['child']))
        return out
    return tree, flatten(tree)


def proposal(manifest, data):
    try:
        diagnostics=[]
        tree, rows=inspect_profile(manifest,data['rootShapeUri'],data.get('names',[]),diagnostics,data)
        return {'status':'proposed','rootClassUri':tree['classUri'],'fields':rows,'results':diagnostics,
                'policy':POLICY,'scope':'Esitysehdotus; SHACL-tyypit ja kardinaliteetit ovat vain luettavia'}
    except GenerationError as error:return {'status':'invalid','fields':[],'results':[error.finding],'policy':POLICY}


def bindings(body, profile_hash):
    extra={'catalogueReferences':body['catalogueReferences']} if body.get('catalogueReferences') else {}
    return checksum(extra|{'profileSnapshotId':body.get('profileSnapshotId'),'profileSha256':profile_hash,
                     'distributions':body.get('distributions'),'title':body['title'],'description':body['description']})


def context_for(tree):
    ctx={'@version':1.1,'@protected':True}
    cls='Class_'+hashlib.sha256(tree['classUri'].encode()).hexdigest()[:12]
    ctx[cls]=tree['classUri']
    for row in tree['fields']:
        entry=row['mapping'];term={'@id':entry['semanticPath'][-1]}
        if row['multi']:term['@container']='@set'
        if 'child' in row:term['@context']=context_for(row['child'])
        elif entry.get('representation')=='iriReference':term['@type']='@id'
        elif entry['datatype']==str(RDF.langString):term['@context']=LANG_CONTEXT
        else:term['@type']=entry['datatype']
        ctx[row['name']]=term
    return ctx


def with_types(tree, content):
    result=copy.deepcopy(content)
    result['@type']='Class_'+hashlib.sha256(tree['classUri'].encode()).hexdigest()[:12]
    for row in tree['fields']:
        if 'child' not in row or row['name'] not in result:continue
        value=result[row['name']]
        result[row['name']]=[with_types(row['child'],v) for v in value] if row['multi'] else with_types(row['child'],value)
    return result


def schema_for(tree):
    schema={'type':'object','properties':{},'additionalProperties':False,'required':[]}
    for row in tree['fields']:
        entry=row['mapping']; dt=(entry['datatype'] or '').removeprefix(str(XSD))
        if entry.get('representation')=='iriReference':value={'type':'string','pattern':IRI_PATTERN}
        elif entry['datatype']==str(RDF.langString):value=copy.deepcopy(LANG_SCHEMA)
        elif 'child' in row:value=schema_for(row['child'])
        else:
            value={'type':{'boolean':'boolean','integer':'integer','nonNegativeInteger':'integer','positiveInteger':'integer','double':'number'}.get(dt,'string')}
            if dt in ('nonNegativeInteger','positiveInteger'):value['minimum']=1 if dt=='positiveInteger' else 0
            if dt=='decimal':value['pattern']=r'^[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)$'
            # Dates/URI exact lexical validation additionally uses the existing conversion profile.
        if row['multi']:
            value={'type':'array','items':value,'minItems':entry['minCount']}
            if entry['maxCount'] is not None:value['maxItems']=entry['maxCount']
            if entry['valueKind']=='literal' or entry.get('representation')=='iriReference':value['uniqueItems']=True
        if 'semantic' in row:value.update({'x-term':row['semantic']['term'],'x-mtv-shacl':copy.deepcopy(row['semantic'])})
        schema['properties'][row['name']]=value
        if entry['minCount']>0:schema['required'].append(row['name'])
    return schema


def local_loader(documents):
    def load(url, options=None):
        if url not in documents:raise ValueError('Konteksti ei kuulu lukittuun paikalliseen dokumenttijoukkoon')
        return {'contextUrl':None,'documentUrl':url,'document':copy.deepcopy(documents[url])}
    return load


def normalize_rdf11(graph):
    result=Graph()
    for s,p,o in graph:
        if isinstance(o,Literal) and not o.datatype and not o.language:o=Literal(str(o),datatype=XSD.string)
        result.add((s,p,o))
    return result


def graph_hash(graph):
    return checksum(sorted((s.n3(),p.n3(),o.n3()) for s,p,o in to_canonical_graph(graph)))


def generate(manifest, profile_hash, body, data, base_url, *, snapshot_url=None):
    if manifest.get('issues'):
        fail('SOURCE_NOT_READY','/profileSnapshotId','Lähdeprofiilissa on ratkaisemattomia puutteita: '+'; '.join(manifest['issues'])[:1500])
    if len(data['exampleContent'].encode())>100000:fail('EXAMPLE_LIMIT','/exampleContent','JSON-esimerkin UTF-8-raja on 100 kB')
    tree, rows=inspect_profile(manifest,data['rootShapeUri'],data.get('names',[]),choices=data)
    refs=attach_references(tree,body['profileSnapshotId'],profile_hash,manifest,base_url,snapshot_url=snapshot_url)
    items=copy.deepcopy(body.get('distributions') or [])
    if len(items)!=3 or {item['type'] for item in items}!={'jsonApi','w3cVc','sdJwtVc'}:
        fail('THREE_DISTRIBUTIONS','/distributions','Paketti tarvitsee yhden kunkin kolmen toimitustyypin kuvauksen')
    if any(item['mapping']['entries'] for item in items) and not data['replaceMappings']:
        fail('MAPPING_REPLACEMENT','/distributions','Hyväksy nykyisten mappingien eksplisiittinen korvaaminen')
    sd=next(item for item in items if item['type']=='sdJwtVc')
    w3c=next(item for item in items if item['type']=='w3cVc')
    if w3c['w3c']['contentPath']!='/credentialSubject':fail('CONTENT_PATH','/distributions','Ensimmäinen generaattori tukee credentialSubject-juurta')
    if not w3c['security']['profileUri'] or (w3c['security']['mechanism']=='jose' and not w3c['security']['algorithms']):
        fail('FORMAT_POLICY_REQUIRED','/distributions','Täydennä W3C-toimitustavan hyväksytty suojausprofiili ja tarvittaessa algoritmit')
    if not sd['sdJwt']['vct'] or not sd['security']['algorithms'] or not sd['security']['profileUri']:
        fail('FORMAT_POLICY_REQUIRED','/distributions','Täydennä vct sekä hyväksytyt suojausprofiili ja algoritmit')
    old_sd={tuple(entry['semanticPath']):entry.get('disclosure') for entry in sd['mapping']['entries']}
    mode=sd['sdJwt']['selectiveDisclosure']
    disclosure={}
    for row in rows:
        path=tuple(row['mapping']['semanticPath'])
        choice='selective' if mode=='always' else 'always' if mode=='never' else old_sd.get(path)
        if choice not in ('selective','always'):fail('DISCLOSURE_REQUIRED',row['mapping']['fieldPath'],'Hyväksy kenttäkohtainen paljastamispäätös toimitustavan mappingissa tai valitse yhteinen aina/ei koskaan -käytäntö')
        disclosure[path]=choice
    for item in items:
        entries=[]
        for row in rows:
            entry=copy.deepcopy(row['mapping'])
            if item['type']=='w3cVc':entry['fieldPath']='/credentialSubject'+entry['fieldPath']
            if item['type']=='sdJwtVc':entry['disclosure']=disclosure[tuple(entry['semanticPath'])]
            entries.append(entry)
        if item['mapping']['entries']!=entries and item['mapping']['entries'] and tuple(map(int,data['mappingVersion'].split('.'))) <= tuple(map(int,item['mapping']['version'].split('.'))):
            fail('MAPPING_VERSION','/distributions','Muuttunut mapping tarvitsee suuremman version')
        item['mapping']={'version':data['mappingVersion'],'entries':entries}
    sd_item=next(item for item in items if item['type']=='sdJwtVc')
    known_paths={entry['fieldPath'] for entry in sd_item['mapping']['entries']}
    known_paths|={path[:-2] for path in known_paths if path.endswith('/*')}
    envelope_paths={'/iss','/sub','/aud','/jti','/iat','/exp','/nbf','/vct','/cnf','/status'}
    if set(sd_item['sdJwt']['nonDisclosableClaims'])-known_paths-envelope_paths:
        fail('DISCLOSURE_PATH_REVIEW','/distributions','Tarkasta aina näkyvien väitteiden polut hyväksyttyjä yhteisiä kenttänimiä vasten')
    selected=copy.deepcopy(manifest);selected['entryShapeUris']=[data['rootShapeUri']]
    from apps.api.distributions import assess
    metadata=assess(selected,items)
    if metadata['status']!='conforms':fail('MAPPING_INVALID','/distributions',canonical(metadata['results'])[:2000])
    example=bounded_json(data['exampleContent'])
    api=next(item for item in items if item['type']=='jsonApi')
    expected=convert(selected,api,example)
    schema={'$schema':'https://json-schema.org/draft/2020-12/schema',**schema_for(tree)}
    Draft202012Validator.check_schema(schema);Draft202012Validator(schema).validate(example)
    bound_body=body|{'distributions':items}
    inputs={'representationProfiles':{'language':LANGUAGE_PROFILE,'reference':REFERENCE_PROFILE},'sourceSnapshotId':body['profileSnapshotId'],'sourceSnapshotSha256':profile_hash,
            'sourceGraphHash':manifest['graphHash'],'rootShapeUri':data['rootShapeUri'],
            'representation':[{k:row[k] for k in ('name','nameOrigin','mapping')} for row in rows],
            'choices':data,'distributions':items,'title':body['title'],'description':body['description'],
            'generator':GENERATOR,'policy':POLICY,'standards':STANDARDS,'publicationBase':base_url,'engines':{'shacl':SHACL_ENGINE,'jsonLd':'PyLD/2.0.4'},
            'catalogueReferences':body.get('catalogueReferences') or [],'catalogueSourcePins':source_pins(),
            'baseContextSha256':hashlib.sha256((FIXTURES/'credentials-v2.jsonld').read_bytes()).hexdigest(),
            'sdSpecificationSha256':hashlib.sha256((FIXTURES/(SD_STANDARD+'.md')).read_bytes()).hexdigest()}
    if snapshot_url is not None:inputs['sourceSnapshotUrl']=snapshot_url
    package_id=checksum(inputs)
    prefix=base_url+'/id/technical-packages/'+package_id+'/'
    context={'@context':context_for(tree)}
    context_url=prefix+'context.jsonld'
    subject=with_types(tree,example)
    targets=reference_nodes(tree,example)
    subjects=[subject]+targets if targets else subject
    documents={context_url:context,BASE_CONTEXT:json.loads((FIXTURES/'credentials-v2.jsonld').read_text())}
    loader=local_loader(documents)
    rdf=jsonld.to_rdf(({'@context':context_url,'@graph':subjects} if targets else {'@context':context_url,**subject}),options={'documentLoader':loader,'format':'application/n-quads','processingMode':'json-ld-1.1'})
    actual=Graph().parse(data=rdf,format='nt')
    # RDFLib canonicalizes numeric lexical forms on parsing; compare like with like.
    expected=Graph().parse(data=expected.serialize(format='nt'),format='nt')
    if not isomorphic(normalize_rdf11(actual),normalize_rdf11(expected)):fail('JSONLD_GRAPH_MISMATCH','/context','JSON-LD-prosessorin RDF poikkeaa odotetusta graafista')
    report=validation_report(selected,profile_hash,{'serialization':'turtle','content':actual.serialize(format='turtle'),'synthetic':True})
    if report['status']!='conforms':fail('GENERATED_SHACL','/example',canonical(report['results'])[:2000])
    vc={'@context':[BASE_CONTEXT,context_url],'type':['VerifiableCredential']+[v for v in w3c['w3c']['vcTypes'] if v!='VerifiableCredential'],
        'issuer':'https://issuer.example.org/synthetic-unissued','description':'SYNTHETIC UNSIGNED STRUCTURE EXAMPLE — NOT ISSUED',
        'credentialSubject':subjects}
    # Expand the whole VCDM envelope too, using only the same two locked documents.
    full_rdf=jsonld.to_rdf(vc,options={'documentLoader':loader,'format':'application/n-quads'})
    full_report=validation_report(selected,profile_hash,{'serialization':'turtle','content':Graph().parse(data=full_rdf,format='nt').serialize(format='turtle'),'synthetic':True})
    if full_report['status']!='conforms':fail('VC_SHACL','/example','VC-rakenne-esimerkin sisältö ei läpäise lähde-SHACLia')
    claims=[]
    row_by_semantic={tuple(row['mapping']['semanticPath']):row for row in rows}
    for row in rows:
        entry=row['mapping'];path=[None if token=='*' else token for token in tokens(entry['fieldPath'])]
        claims.append({'path':path,'sd':'always' if disclosure[tuple(entry['semanticPath'])]=='selective' else 'never',
                       'mandatory':all(row_by_semantic[tuple(entry['semanticPath'][:i])]['mapping']['minCount']>0 for i in range(1,len(entry['semanticPath'])+1)),'display':row['labels'] or [{'locale':'und','label':row['name']}]})
        if row['multi']:
            # Array container and each element have distinct disclosure meanings in the IETF profile.
            claims.append({'path':path[:-1],'sd':'never','mandatory':claims[-1]['mandatory']})
    type_metadata={'vct':sd['sdJwt']['vct'],'name':body['title'],'description':body['description'],'claims':claims}
    check_type_metadata(type_metadata)
    validation={'status':'conforms','jsonSchema':'conforms','jsonLdProcessor':'PyLD/2.0.4',
                'jsonLdGraphComparison':'isomorphic','exampleGraphSha256':graph_hash(actual),
                'shacl':'conforms','shaclEngine':SHACL_ENGINE,'fullVcContentShacl':'conforms','typeMetadata':'checked-supported-subset',
                'scope':'synthetic content + JSON-LD expansion + offline SHACL; no issuance, signatures, disclosures, holder binding execution or wallet test'}
    semantic={'sourceSnapshotId':body['profileSnapshotId'],'sourceSnapshotSha256':profile_hash,
              'rootShapeUri':data['rootShapeUri'],'rootClassUri':tree['classUri'],'distributions':items,
              'formatPolicies':{'sdJwt':sd['sdJwt'],'security':sd['security']},'sourceVocabularyReferences':manifest['vocabularyReferences'],
              'dependencyChecksums':[{'uri':d['uri'],'sha256':d['artifact']['sha256']} for d in manifest['dependencies'] if 'artifact' in d]}
    profile,issuer_binding,catalog_report=enrich(prefix,tree,refs,schema,type_metadata,semantic,body.get('catalogueReferences') or [])
    values={'context.jsonld':('application/ld+json',context),'content.schema.json':('application/schema+json',schema),
            'sd-jwt-type-metadata.json':('application/json',type_metadata),'semantic-mapping.json':('application/json',semantic),
            'semantic-extension-profile.json':('application/json',profile),'issuer-metadata-binding.json':('application/json',issuer_binding),'catalogue-coverage.json':('application/json',catalog_report),
            'content-example.json':('application/json',example),'sd-jwt-claims-example.json':('application/json',example),
            'unsigned-vc-example.jsonld':('application/ld+json',vc),'validation.json':('application/json',validation)}
    artifacts={name:{'mediaType':media,'content':canonical(value),'sha256':hashlib.sha256(canonical(value).encode()).hexdigest(),'url':prefix+name}
               for name,(media,value) in values.items()}
    manifest_doc={'packageId':package_id,'generator':GENERATOR,'policy':POLICY,'standards':STANDARDS,'inputs':inputs,
                  'artifacts':{name:{k:v for k,v in artifact.items() if k!='content'} for name,artifact in artifacts.items()},'validation':validation,
                  'transport':'https' if base_url.startswith('https://') else 'local-demo-http; configure HTTPS PUBLIC_BASE_URL for external use'}
    content=canonical(manifest_doc)
    artifacts['manifest.json']={'mediaType':'application/json','content':content,'sha256':hashlib.sha256(content.encode()).hexdigest(),'url':prefix+'manifest.json'}
    return {'status':'ready','packageId':package_id,'sha256':checksum(manifest_doc),'generator':GENERATOR,'policy':POLICY,
            'standards':STANDARDS,'rootShapeUri':data['rootShapeUri'],'sourceSnapshotSha256':profile_hash,'bindingHash':bindings(bound_body,profile_hash),
            'representation':inputs['representation'],'validation':validation,'artifacts':artifacts},items


def check_type_metadata(doc):
    # IETF fields remain unchanged; x-mtv-* members are explicitly a local extension.
    if not set(doc)<= {'vct','name','description','claims','x-mtv-profile','x-mtv-mapping','x-mtv-schema'} or not isinstance(doc.get('vct'),str) or not doc['vct']:
        fail('TYPE_METADATA','/vct','Virheellinen Type Metadata -tunniste tai ylimääräinen kenttä')
    seen=set()
    for claim in doc['claims']:
        path=claim['path']
        if not isinstance(path,list) or not path or not all(isinstance(p,str) or p is None for p in path):
            fail('TYPE_METADATA_PATH','/claims','Väitepolun on oltava epätyhjä merkkijono/null-taulukko')
        key=canonical(path)
        if key in seen:fail('TYPE_METADATA_PATH','/claims','Väitepolku esiintyy useasti')
        seen.add(key)
        if claim['sd'] not in ('always','never') or type(claim['mandatory']) is not bool:
            fail('TYPE_METADATA_POLICY','/claims','Virheellinen paljastamis- tai pakollisuusmääritys')
        for display in claim.get('display',[]):
            if set(display)!={'locale','label'} or any(not isinstance(value,str) for value in display.values()):
                fail('TYPE_METADATA_DISPLAY','/claims','Näyttömääritys tarvitsee locale- ja label-merkkijonot')


def _worker(mode, manifest, profile_hash, body, data, base_url, writer):
    try:
        import resource, socket
        resource.setrlimit(resource.RLIMIT_CPU,(8,8));resource.setrlimit(resource.RLIMIT_AS,(768*1024*1024,768*1024*1024))
        def offline(*args,**kwargs):raise ValueError('Offline generation')
        socket.socket.connect=offline;socket.socket.connect_ex=offline;socket.getaddrinfo=offline
        writer.send(proposal(manifest,data) if mode=='proposal' else generate(manifest,profile_hash,body,data,base_url))
    except GenerationError as error:writer.send({'status':'invalid','results':[error.finding]})
    except Exception:writer.send({'status':'invalid','results':[{'ruleId':'GENERATION_ERROR','path':'/technicalPackage','message':'Generointi epäonnistui; tarkista synteettinen JSON, lähdeprofiili ja esitysvalinnat'}]})
    finally:writer.close()


def bounded(mode, snapshot, body, data, base_url):
    ctx=multiprocessing.get_context('spawn');reader,writer=ctx.Pipe(duplex=False)
    process=ctx.Process(target=_worker,args=(mode,snapshot.manifest,snapshot.checksum,body,data,base_url,writer))
    process.start();writer.close()
    try:
        if not reader.poll(20):raise ValueError('Timeout')
        try:return reader.recv()
        except EOFError:raise ValueError('Resource limit') from None
    except ValueError:return {'status':'invalid','results':[{'ruleId':'GENERATION_RESOURCE_LIMIT','path':'/technicalPackage','message':'Generoinnin resurssiraja ylittyi'}]}
    finally:
        reader.close();process.join(.2)
        if process.is_alive():process.terminate();process.join(1)


def package_errors(body,snapshot):
    package=body.get('technicalPackage')
    if package is None:return []
    if not snapshot or package.get('status')!='ready' or package.get('bindingHash')!=bindings(body,snapshot.checksum):
        return [{'path':'/technicalPackage','ruleId':'PACKAGE_NOT_READY','message':'Muodosta ajantasainen tekninen kuvauspaketti ennen hyväksyntää'}]
    return []
