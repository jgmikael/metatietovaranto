"""Distribution mapping metadata checks; never parse JWTs or issue credentials."""
import multiprocessing
from datetime import datetime,timezone
from rdflib import RDF,SH,URIRef,Literal
from apps.api.profiles import checksum
from apps.api.semantic_validation import locked_graph

POLICY='distribution-mapping-metadata-v1'


def normalize_distributions(body,snapshot):
    items=body.get('distributions')
    if items is None:return
    ids=[item['id'] for item in items]
    if len(set(ids))!=len(ids):raise ValueError('Toimitustapojen tunnisteiden on oltava yksilöllisiä tuotteessa')
    selected=body.get('primaryDistributionId')
    if selected and selected not in ids:raise ValueError('Ensisijaista toimitustapaa ei löydy')
    body['primaryDistributionId']=selected or next((item['id'] for item in items if item['type']=='w3cVc'),ids[0])
    for item in items:
        if item['profileSnapshotId'] and (not snapshot or item['profileSnapshotId']!=str(snapshot.id)):
            raise ValueError('Kaikkien toimitustapojen on viitattava tuotteen samaan profiilisnapshotiin')
        item['profileSnapshotId']=str(snapshot.id) if snapshot else None


def expected_fields(graph,manifest):
    declared=manifest.get('entryShapeUris',[])
    roots=[URIRef(uri) for uri in declared] if declared else [node for node in graph.subjects(RDF.type,SH.NodeShape)
        if any(graph.objects(node,SH.targetClass)) or any(graph.objects(node,SH.targetNode))
        or any(graph.objects(node,SH.targetSubjectsOf)) or any(graph.objects(node,SH.targetObjectsOf))]
    result=[];problems=[]
    def visit(root,shape,path,ancestors):
        if shape in ancestors or len(path)>=10:
            problems.append('Rekursiivinen tai liian syvä semanttinen mapping vaatii jatkoprofiilin');return
        if graph.value(shape,SH.deactivated)==Literal(True):return
        for prop in graph.objects(shape,SH.property):
            if graph.value(prop,SH.deactivated)==Literal(True):continue
            semantic=graph.value(prop,SH.path)
            if not isinstance(semantic,URIRef):problems.append('Monimutkaista SHACL-polkulauseketta ei tueta kenttäpolun mappingissa');continue
            chain=path+[str(semantic)];datatype=graph.value(prop,SH.datatype)
            if len(list(graph.objects(prop,SH.node)))>1:
                problems.append('Usean sisäkkäisen muodon leikkaus vaatii erillisen mapping-profiilin')
            node=graph.value(prop,SH.node);object_class=graph.value(prop,SH['class'])
            if node is None and object_class:
                candidates=set(graph.subjects(SH.targetClass,object_class))
                if len(candidates)==1:node=next(iter(candidates))
            if not datatype and not node and not object_class:
                problems.append('Kentän literaali-/oliorakennetta ei voida päätellä SHACL-profiilista');continue
            minimum=graph.value(prop,SH.minCount);maximum=graph.value(prop,SH.maxCount)
            result.append({'shapeUri':str(root),'semanticPath':chain,'valueKind':'literal' if datatype else 'object',
                'datatype':str(datatype) if datatype else None,'classUri':str(object_class or graph.value(node,SH.targetClass)) if (object_class or node and graph.value(node,SH.targetClass)) else None,
                'minCount':int(minimum) if minimum is not None else 0,'maxCount':int(maximum) if maximum is not None else None})
            if node is not None:visit(root,node,chain,ancestors|{shape})
    for root in set(roots):visit(root,root,[],set())
    return result,problems


def schema_mapping_paths(artifact,entries):
    """Validate declared JSON field paths against a referenced, locked technical schema."""
    from apps.api.derived_validation import strict_json,pointer,local_schema
    doc=strict_json(artifact['content']);root=pointer(doc,artifact.get('schemaPointer',''))
    for entry in entries:
        schema=root
        for encoded in entry['fieldPath'][1:].split('/'):
            token=encoded.replace('~1','/').replace('~0','~')
            schema=local_schema(doc,schema)
            if not isinstance(schema,dict):raise ValueError('Unsupported schema')
            if token=='*':
                if schema.get('type')!='array':raise ValueError('Expected array')
                schema=schema['items']
            else:
                if schema.get('type')!='object':raise ValueError('Expected object')
                schema=schema['properties'][token]
        schema=local_schema(doc,schema)
        if entry['valueKind']=='object' and schema.get('type')!='object':raise ValueError('Expected object value')


def assess(manifest,items):
    graph=locked_graph(manifest);expected,unsupported=expected_fields(graph,manifest)
    results=[];assessments=[]
    def problem(index,rule,message):results.append({'path':f'/distributions/{index}','ruleId':rule,'message':message})
    services={}
    artifact_records={item['id']:item for item in manifest.get('derivedArtifacts',[])}
    artifacts={key:value['serialization'] for key,value in artifact_records.items()}
    for index,item in enumerate(items):
        entries=item['mapping']['entries'];mapped={};paths=set();start=len(results)
        for message in unsupported:problem(index,'MAPPING_UNASSESSED',message)
        for entry in entries:
            key=(entry['shapeUri'],tuple(entry['semanticPath']))
            if key in mapped or entry['fieldPath'] in paths:problem(index,'MAPPING_DUPLICATE','Semanttinen kohta tai toimitusmuodon kenttäpolku on kuvattu useammin kuin kerran')
            mapped[key]=entry;paths.add(entry['fieldPath'])
            multi=entry['maxCount'] is None or entry['maxCount']>1
            if entry['fieldPath'].endswith('/*')!=multi:problem(index,'MAPPING_MULTIPLICITY','Moniarvoinen kenttä kuvataan polun lopun /*-alkiolla; yksiarvoinen ilman sitä')
            if len(entry['semanticPath'])>1:
                parent=mapped.get((entry['shapeUri'],tuple(entry['semanticPath'][:-1])))
                # Ordering of mapping entries is irrelevant.
                parent=parent or next((candidate for candidate in entries if candidate['shapeUri']==entry['shapeUri'] and candidate['semanticPath']==entry['semanticPath'][:-1]),None)
                if not parent or parent['valueKind']!='object' or not entry['fieldPath'].startswith(parent['fieldPath']+'/'):
                    problem(index,'MAPPING_NESTING','Sisäkkäinen kenttä tarvitsee oliovanhemman ja sen alle sijoittuvan kenttäpolun')
            if item['type']=='w3cVc' and not entry['fieldPath'].startswith(item['w3c']['contentPath']+'/'):
                problem(index,'W3C_CONTENT_PATH','W3C VC:n sisältökentät kuuluvat ilmoitettuun credentialSubject-sisältöpolkuun')
            if item['type']=='sdJwtVc':
                if entry['fieldPath'].split('/')[1] in ('iss','iat','exp','nbf','vct','cnf','_sd','_sd_alg','...'):
                    problem(index,'SDJWT_RESERVED_CLAIM','Sisältömapping ei saa korvata SD-JWT VC:n varattuja kuoriväitteitä')
                disclosure=entry.get('disclosure')
                mode=item['sdJwt']['selectiveDisclosure']
                if disclosure is None or (mode=='always' and disclosure!='selective') or (mode=='never' and disclosure!='always'):
                    problem(index,'SDJWT_DISCLOSURE','Valikoivan paljastamisen käytäntö ja kenttäkohtainen ilmoitus eivät vastaa toisiaan')
                if disclosure=='always' and any(candidate['disclosure']=='selective' and entry['fieldPath'].startswith(candidate['fieldPath']+'/') for candidate in entries):
                    problem(index,'SDJWT_DISCLOSURE','Aina näkyvää väitettä ei voi sijoittaa valikoivasti paljastettavan olion alle')
                if disclosure=='selective' and entry['fieldPath'] in item['sdJwt']['nonDisclosableClaims']:
                    problem(index,'SDJWT_DISCLOSURE','Pakollisesti näkyväksi ilmoitettua väitettä ei voi kuvata valikoivasti paljastettavaksi')
            elif entry.get('disclosure') is not None:problem(index,'DISCLOSURE_FORMAT','SD-JWT-paljastamiskäytäntö kuuluu vain SD-JWT VC -mappingiin')
        expected_keys=set()
        for field in expected:
            key=(field['shapeUri'],tuple(field['semanticPath']));expected_keys.add(key)
            entry=mapped.get(key)
            if not entry:problem(index,'MAPPING_MISSING','Profiilin kentän mapping puuttuu: '+' / '.join(field['semanticPath']));continue
            if any(entry.get(key)!=field[key] for key in ('valueKind','datatype','classUri','minCount','maxCount')):
                problem(index,'MAPPING_CONFLICT','Mappingin tietotyyppi, luokka tai kardinaliteetti poikkeaa jäädytetystä SHACL-profiilista')
        if not expected:problem(index,'MAPPING_MISSING','Profiilissa ei ole kohdistuvia kartoitettavia kenttiä')
        if set(mapped)-expected_keys:problem(index,'MAPPING_UNKNOWN','Mapping sisältää SHACL-profiilista puuttuvan semanttisen kenttäpolun')
        if item['type']=='jsonApi':
            api=item['api']
            for name,kind in [('openApiArtifactId','openapi'),('jsonSchemaArtifactId','jsonSchema')]:
                if api[name] and artifacts.get(api[name])!=kind:problem(index,'API_SCHEMA_REFERENCE','JSON API:n skeemaviite ei vastaa saman snapshotin oikeaa artefaktityyppiä')
            for reference in (api['openApiArtifactId'],api['jsonSchemaArtifactId']):
                if reference in artifact_records:
                    try:schema_mapping_paths(artifact_records[reference],entries)
                    except Exception:problem(index,'API_SCHEMA_MAPPING','JSON API:n mapping-polku ei vastaa viitatun teknisen skeeman objektia, kenttää tai taulukkoa')
            if item['availability'] in ('sandbox','production'):
                if not all((api['serviceUrl'],api['openApiArtifactId'],api['jsonSchemaArtifactId'],api['freshness'])):
                    problem(index,'API_METADATA_REQUIRED','Käytettävä JSON API tarvitsee HTTPS-osoitteen, OpenAPI- ja JSON Schema -viitteet sekä ajantasaisuuden kuvauksen')
                if api['authentication']!='none' and not api['requiredRights']:problem(index,'API_RIGHTS_REQUIRED','Käyttöoikeudet on kuvattava tunnistautuvalle JSON API:lle')
        else:
            credential=item['credential']
            if credential['legalCategory']=='QEAA':problem(index,'QEAA_UNVERIFIED','Demo ei vahvista QEAA-asemaa')
            issuer=credential['credentialIssuer']
            if issuer:
                key=issuer
                existing=services.setdefault(key,set())
                if existing & set(credential['configurationIds']):problem(index,'CONFIGURATION_AMBIGUOUS','Saman myöntäjäpalvelun toimitusmuodoilla on oltava erilliset credential configuration -tunnisteet')
                existing.update(credential['configurationIds'])
            if item['type']=='w3cVc':
                if 'VerifiableCredential' not in item['w3c']['vcTypes'] or 'https://www.w3.org/ns/credentials/v2' not in item['w3c']['contexts']:
                    problem(index,'W3C_PROFILE_REQUIRED','W3C VCDM 2.0 edellyttää perustyyppiä ja v2-kontekstia')
            elif not item['sdJwt']['vct'] or not item['sdJwt']['profileVersion']:
                problem(index,'SDJWT_PROFILE_REQUIRED','SD-JWT VC tarvitsee vct-tunnisteen ja nimetyn profiiliversion; JSON-LD-kontekstia ei vaadita')
            if item['availability'] in ('sandbox','production'):
                required=('issuerOrganizationId','credentialIssuer','initiationUrl','configurationIds','validityProfile','statusProfile','subjectTypes','representationRequirements','support')
                if not all(credential[key] for key in required) or not item['security']['profileUri']:
                    problem(index,'CREDENTIAL_METADATA_REQUIRED','Käytettävän todistustoimituksen myöntämis-, oikeus-, suojaus-, voimassaolo- ja tilatietoprofiilit puuttuvat')
                if item['security']['mechanism'] in ('jose','sdJwt') and not item['security']['algorithms']:
                    problem(index,'SECURITY_PROFILE_REQUIRED','JOSE-/SD-JWT-profiilissa on nimettävä sallitut allekirjoitusalgoritmit')
        assessments.append({'distributionId':item['id'],'type':item['type'],'mappingVersion':item['mapping']['version'],
            'fieldCount':len(entries),'status':'conforms' if start==len(results) else 'invalid'})
    return {'status':'conforms' if not results else 'invalid','distributions':assessments,
        'resultCount':len(results),'truncated':len(results)>100,'results':results[:100],
        'scope':'metadata and mapping declarations only; no JSON-to-RDF conversion, JWT parsing, cryptography or wallet interoperability'}


def _worker(manifest,items,writer,root_shape=None):
    try:
        import resource,socket
        resource.setrlimit(resource.RLIMIT_CPU,(5,5));resource.setrlimit(resource.RLIMIT_AS,(512*1024*1024,512*1024*1024))
        def offline(*args,**kwargs):raise ValueError('Offline')
        socket.socket.connect=offline;socket.socket.connect_ex=offline;socket.getaddrinfo=offline
        if root_shape:manifest={**manifest,'entryShapeUris':[root_shape]}
        writer.send(assess(manifest,items))
    except Exception:writer.send({'status':'error','results':[{'path':'/distributions','ruleId':'DISTRIBUTION_ERROR','message':'Toimitustapojen metadataa ei voitu tarkistaa'}]})
    finally:writer.close()


def validate_distributions(snapshot,items,root_shape=None):
    if items is None:return None
    context=multiprocessing.get_context('spawn');reader,writer=context.Pipe(duplex=False)
    process=context.Process(target=_worker,args=(snapshot.manifest,items,writer,root_shape));process.start();writer.close()
    try:
        if not reader.poll(15):raise ValueError('Timeout')
        try:report=reader.recv()
        except EOFError:raise ValueError('Resource limit') from None
    except ValueError:report={'status':'error','results':[{'path':'/distributions','ruleId':'DISTRIBUTION_RESOURCE_LIMIT','message':'Toimitustapojen tarkistuksen resurssiraja ylittyi'}]}
    finally:
        reader.close();process.join(.2)
        if process.is_alive():process.terminate();process.join(1)
    return report|({'selectedRootShapeUri':root_shape} if root_shape else {})|{'policy':POLICY,'profileSnapshotSha256':snapshot.checksum,'distributionsHash':checksum(items),'checkedAt':datetime.now(timezone.utc).isoformat()}


def distribution_errors(snapshot,body):
    items=body.get('distributions')
    if items is None:return []
    report=body.get('distributionValidation')
    root=(body.get('technicalPackage') or {}).get('rootShapeUri')
    if not report or report.get('selectedRootShapeUri')!=root or report.get('policy')!=POLICY or report.get('profileSnapshotSha256')!=snapshot.checksum or report.get('distributionsHash')!=checksum(items):
        return [{'path':'/distributions','ruleId':'DISTRIBUTION_REPORT_REQUIRED','message':'Ajantasainen toimitustapojen metadata- ja mapping-raportti puuttuu. Tallenna luonnos.'}]
    return [] if report['status']=='conforms' else report['results']
