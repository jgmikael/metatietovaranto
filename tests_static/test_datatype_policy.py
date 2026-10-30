"""RDF term provenance, OWL/SHACL separation and actual worker/server parity."""
import copy, hashlib, json
from pathlib import Path
import pytest
from playwright.sync_api import expect
from rdflib import Graph, SH, RDF, RDFS, XSD, URIRef
from rdflib.compare import isomorphic
from pyld import jsonld
from apps.api.technical_packages import inspect_profile, proposal, GenerationError, context_for, schema_for, normalize_rdf11
from scripts.browser_generation_reference import reference
from tests_static.test_browser_generation import worker, source, prepared, request_for
from tests_static.test_experiment import start, open_product, saved, stored, export, open_import, upload, replace

ROOT=Path(__file__).resolve().parents[1]
P='https://example.org/literal-refinements/'
TEXT=(ROOT/'fixtures/browser-generation/literal-refinements.ttl').read_text()
X=str(XSD)


def manifest(text):return {'sourceArtifacts':[source(text)|{'serialization':'turtle'}],'dependencies':[],'derivedArtifacts':[]}


def check(page,base,text):
    profile=prepared(page,base,[source(text)])
    return worker(page,base,{'action':'proposal','profile':profile,'settings':{'rootShapeUri':P+'Root','names':[]}}),profile


def test_refinements_preserve_shacl_types_in_all_artifacts_and_real_jsonld(page,static_site):
    result,profile=check(page,static_site,TEXT);assert result['ok'],result
    server_report=proposal(manifest(TEXT),{'rootShapeUri':P+'Root'})
    assert {r['ruleId'] for r in server_report['results']}=={'OWL_RANGE_REFINEMENT'}
    assert {r['ruleId'] for r in result['value']['findings']}=={'OWL_RANGE_REFINEMENT'}
    tree,rows=inspect_profile(manifest(TEXT),P+'Root',[])
    assert rows==result['value']['rows']
    assert {r['mapping']['datatype'] for r in rows}=={X+'date',X+'string',X+'positiveInteger'}
    ref=reference();settings=ref['settings']|{'profileId':profile['id'],'rootShapeUri':P+'Root','exampleContent':'{"label":"Synthetic","sequence":2}'}
    metadata=copy.deepcopy(ref['metadata']);metadata['profileSnapshotId']=profile['id']
    for d in metadata['distributions']:d['profileSnapshotId']=profile['id']
    request={'action':'generate','profile':profile,'settings':settings,'metadata':metadata}
    first=worker(page,static_site,request);assert first['ok'],first
    assert worker(page,static_site,request)==first
    artifacts=first['value']['artifacts'];parsed=lambda name:json.loads(artifacts[name]['content'])
    context=parsed('context.jsonld');assert context=={'@context':context_for(tree)}
    schema=parsed('content.schema.json');plain=copy.deepcopy(schema);plain.pop('x-mtv-profile');plain.pop('x-mtv-mapping')
    from apps.api.semantic_extension import attach_references
    refs=attach_references(tree,profile['id'],profile['sha256'],manifest(TEXT)|{'profileUri':profile['profileUri'],'sourceVersion':profile['sourceVersion']},settings['publicationBase'])
    for r in refs:r['sourceProfile']['snapshotUrl']=None
    assert plain=={'$schema':'https://json-schema.org/draft/2020-12/schema',**schema_for(tree)}
    assert context['@context']['dateOfIssue']['@type']==X+'date'
    assert context['@context']['sequence']['@type']==X+'positiveInteger'
    assert schema['properties']['sequence']['type']=='integer'
    assert schema['properties']['dateOfIssue']['type']=='string'  # Existing contract has no JSON Schema format assertion.
    claims=parsed('sd-jwt-type-metadata.json')['claims']
    assert any(c['path']==['sequence'] and c['x-mtv-semantic']['term']==P+'sequence' for c in claims)
    mapping=parsed('semantic-mapping.json')
    assert 'positiveInteger' in json.dumps(mapping) and 'rdfs:Literal' not in json.dumps(mapping)
    assert all(hashlib.sha256(a['content'].encode()).hexdigest()==a['sha256'] for a in artifacts.values())
    def loader(url,options=None):
        assert url==artifacts['context.jsonld']['url']
        return {'contextUrl':None,'documentUrl':url,'document':context}
    vc=parsed('unsigned-vc-example.jsonld')
    nq=jsonld.to_rdf({'@context':artifacts['context.jsonld']['url'],**vc['credentialSubject']},options={'documentLoader':loader,'format':'application/n-quads'})
    expected=Graph().parse(data='''@prefix ex:<https://example.org/literal-refinements/> . @prefix xsd:<http://www.w3.org/2001/XMLSchema#> . [] a ex:Subject;ex:label "Synthetic";ex:sequence "2"^^xsd:positiveInteger .''',format='turtle')
    assert isomorphic(normalize_rdf11(Graph().parse(data=nq,format='nt')),normalize_rdf11(expected))
    # Exercise the real server generator too, including its independent SHACL check.
    from apps.api.technical_packages import generate
    from rdflib.compare import to_isomorphic
    server_source=manifest(TEXT)|{'profileUri':profile['profileUri'],'sourceVersion':None,
        'entryShapeUris':[P+'Root'],'vocabularyReferences':[],'issues':[],
        'graphHash':str(to_isomorphic(Graph().parse(data=TEXT,format='turtle')).internal_hash())}
    server_package,_=generate(server_source,profile['sha256'],metadata,settings|{'replaceMappings':True},settings['publicationBase'])
    assert server_package['status']=='ready' and server_package['validation']['shacl']=='conforms'
    assert json.loads(server_package['artifacts']['context.jsonld']['content'])==context
    server_schema=json.loads(server_package['artifacts']['content.schema.json']['content'])
    for prop in server_schema['properties'].values():prop['x-mtv-shacl']['sourceProfile']['snapshotUrl']=None  # Local browser snapshot has no published endpoint.
    assert server_schema['properties']==schema['properties']
    assert profile['sources']==[source(TEXT)]


@pytest.mark.parametrize('replacement,rule,category',[
    ('sh:datatype "http://www.w3.org/2001/XMLSchema#date"','DATATYPE_TERM','sourceError'),
    ('sh:datatype rdfs:Literal','DATATYPE_REPRESENTATION_REQUIRED','generatorLimit'),
    ('sh:nodeKind sh:Literal','DATATYPE_REPRESENTATION_REQUIRED','generatorLimit'),
    ('sh:datatype <http://www.w3.org/1999/02/22-rdf-syntax-ns#langString>','LANGUAGE_REPRESENTATION_REQUIRED','decisionRequired'),
    ('sh:datatype xsd:duration','DATATYPE_UNSUPPORTED','generatorLimit'),
])
def test_term_support_and_representation_errors_are_distinct(page,static_site,replacement,rule,category):
    text=TEXT.replace('sh:datatype xsd:date',replacement)+ '\nex:Date sh:defaultValue "päivä"@fi .'
    response,profile=check(page,static_site,text);assert not response['ok'],response
    finding=next(f for f in response['findings'] if f['ruleId']==rule)
    report=proposal(manifest(text),{'rootShapeUri':P+'Root'});server=report['results'][0]
    assert server['ruleId']==rule and server['category']==category==finding['category']
    assert server['observed']==finding['observed']
    assert finding['propertyShapes'][0]['sources']==server['propertyShapes'][0]['sources']==['source.ttl']
    assert finding['owlRanges'][0]['value']==str(RDFS.Literal)
    assert finding['path']==P+'dateOfIssue' and finding['predicate'] in {str(SH.datatype),str(SH.nodeKind)}
    if rule=='DATATYPE_TERM':
        assert finding['observed']['datatype']==X+'string'
        assert '<'+X+'date>' in finding['suggestion'] and 'boolean' not in finding['suggestion']
        assert '<'+X+'date>' in server['suggestion'] and 'boolean' not in server['suggestion']
    else:
        assert finding['observed']['termType']=='NamedNode'
        assert 'datatype' not in finding['observed']
    graph=Graph().parse(data=profile['sources'][0]['content'],format='turtle')
    literal=next(graph.objects(URIRef(P+'Date'),SH.defaultValue));assert literal.language=='fi'
    assert profile['sources'][0]==source(text)
    assert 'fields' not in response.get('value',{})  # No fallback string mapping.


@pytest.mark.parametrize('extra,rule,ok',[
    ('ex:dateOfIssue rdfs:range xsd:string .','OWL_RANGE_UNASSESSED',True),
    ('ex:dateOfIssue rdfs:range xsd:date .','OWL_RANGE_COMPATIBLE',True),
    ('ex:dateOfIssue rdfs:range xsd:string . xsd:date <http://www.w3.org/2002/07/owl#disjointWith> xsd:string .','OWL_SHACL_CONFLICT',False),
    ('ex:dateOfIssue rdfs:range xsd:string . xsd:string <http://www.w3.org/2002/07/owl#disjointWith> xsd:date .','OWL_SHACL_CONFLICT',False),
])
def test_only_proven_range_conflicts_block(page,static_site,extra,rule,ok):
    text=TEXT+'\n'+extra
    result,_=check(page,static_site,text);assert result['ok']==ok,result
    findings=result['value']['findings'] if ok else result['findings']
    assert any(f['ruleId']==rule for f in findings)
    report=proposal(manifest(text),{'rootShapeUri':P+'Root'})
    assert report['status']==('proposed' if ok else 'invalid')
    assert any(f['ruleId']==rule for f in report['results'])


def test_worker_storage_export_reload_keeps_named_terms_and_original_source(page,static_site,tmp_path):
    start(page,static_site);open_product(page)
    page.get_by_label('SHACL Turtle -tiedosto',exact=True).set_input_files({'name':'refinements.ttl','mimeType':'text/turtle','buffer':TEXT.encode()})
    expect(page.get_by_text('Turtle jäsennetty:',exact=False)).to_be_visible()
    expect(page.get_by_text('sh:datatype: '+X+'date'+' · NamedNode',exact=True)).to_be_visible()
    page.get_by_label('Lähdeprofiilin tunniste',exact=True).fill('urn:synthetic:refinements')
    page.get_by_role('button',name='Liitä tuotu profiili tuotteeseen',exact=True).click()
    expect(page.get_by_text('Profiili liitetty paikalliseen tuotteeseen. Valitse juurimuoto.',exact=True)).to_be_visible();saved(page)
    payload=export(page,tmp_path)
    before=stored(page)['localProfiles'][0]
    assert before['sources'][0]==source(TEXT,'refinements.ttl')
    page.reload();saved(page)
    assert stored(page)['localProfiles'][0]==before
    open_import(page);upload(page,payload);replace(page)
    after=stored(page)['localProfiles'][0];assert after==before
    info=worker(page,static_site,{'action':'inspect','sources':after['sources']})['value']
    for shape in info['shapes']:
        for prop in shape['properties']:
            assert prop['datatypes'][0]['termType']=='NamedNode'
            assert 'datatype' not in prop['datatypes'][0]
    response=worker(page,static_site,{'action':'proposal','profile':after,'settings':{'rootShapeUri':P+'Root','names':[]}})
    assert response['ok'],response


@pytest.mark.parametrize('uri',[X+'date',str(RDF.langString),X+'positiveInteger',str(RDFS.Literal),X+'string'])
def test_quoted_datatype_uses_observed_uri_not_literal_datatype(page,static_site,uri):
    text=TEXT.replace('sh:datatype xsd:date','sh:datatype '+json.dumps(uri))
    result,_=check(page,static_site,text)
    finding=next(f for f in result['findings'] if f['ruleId']=='DATATYPE_TERM')
    assert finding['observed']=={'termType':'Literal','value':uri,'datatype':X+'string','language':''}
    assert '<'+uri+'>' in finding['suggestion']
    server=proposal(manifest(text),{'rootShapeUri':P+'Root'})['results'][0]
    assert server['observed']==finding['observed'] and '<'+uri+'>' in server['suggestion']


def test_local_owl_dependency_and_anonymous_property_provenance(page,static_site):
    text=TEXT.replace('sh:property ex:Date, ex:Text, ex:Sequence','sh:property _:date, ex:Text, ex:Sequence').replace('ex:Date sh:path','_:date sh:path')
    text=text[:text.index('ex:dateOfIssue rdfs:range')]
    dependency='''@prefix ex:<https://example.org/literal-refinements/> .
@prefix rdfs:<http://www.w3.org/2000/01/rdf-schema#> .
ex:dateOfIssue rdfs:range rdfs:Literal .'''
    files=[source(text,'main.ttl'),source(dependency,'vocabulary.ttl')]
    profile=prepared(page,static_site,files)
    response=worker(page,static_site,{'action':'proposal','profile':profile,'settings':{'rootShapeUri':P+'Root','names':[]}})
    assert response['ok'],response
    finding=response['value']['findings'][0]
    assert finding['ruleId']=='OWL_RANGE_REFINEMENT'
    assert finding['propertyShapes'][0]['uri'] is None
    assert finding['propertyShapes'][0]['sources']==['main.ttl']
    assert finding['owlRanges'][0]['sources']==['vocabulary.ttl']
    data=manifest(text);data['sourceArtifacts'][0]['name']='main.ttl'
    data['dependencies']=[{'artifact':files[1]|{'serialization':'turtle'}}]
    report=proposal(data,{'rootShapeUri':P+'Root'})
    assert report['status']=='proposed'
    assert report['results'][0]['propertyShapes'][0]['uri'] is None
    assert report['results'][0]['owlRanges']==finding['owlRanges']
    assert profile['sources']==files


@pytest.mark.parametrize('datatype,code,source_error',[
    ('"http://www.w3.org/2001/XMLSchema#date"','DATATYPE_TERM',True),
    ('<http://www.w3.org/1999/02/22-rdf-syntax-ns#langString>','LANGUAGE_REPRESENTATION_REQUIRED',False),
])
def test_ui_datatype_diagnostic_separates_source_error_and_support_limit(page,static_site,datatype,code,source_error):
    text=TEXT.replace('sh:datatype xsd:date','sh:datatype '+datatype)
    start(page,static_site);open_product(page)
    page.get_by_label('SHACL Turtle -tiedosto',exact=True).set_input_files({'name':'types.ttl','mimeType':'text/turtle','buffer':text.encode()})
    expect(page.get_by_text('Turtle jäsennetty:',exact=False)).to_be_visible()
    page.get_by_label('Lähdeprofiilin tunniste',exact=True).fill('urn:synthetic:diagnostic')
    page.get_by_role('button',name='Liitä tuotu profiili tuotteeseen',exact=True).click()
    expect(page.get_by_text('Profiili liitetty paikalliseen tuotteeseen. Valitse juurimuoto.',exact=True)).to_be_visible()
    page.get_by_label('Generoinnin juurimuodon IRI',exact=True).fill(P+'Root')
    page.get_by_role('button',name='Tarkista tuki ja muodosta mapping-ehdotus',exact=True).click()
    region=page.get_by_role('region',name='Lähdeprofiilin havainnot')
    expect(region).to_contain_text(code)
    expect(region).to_contain_text('OWL-arvoalue (rdfs:range), erillinen SHACL-rajoitteesta:')
    expect(region).to_contain_text('types.ttl')
    expect(page.get_by_role('button',name='Muodosta paikallinen tekninen paketti',exact=True)).to_be_disabled()
    if source_error:
        expect(region).to_contain_text('sh:datatype <'+X+'date> .')
        expect(region).to_contain_text('literaalitermin oma tietotyyppi: '+X+'string')
    else:
        expect(region).not_to_contain_text('Korjaa lähde ja tuo uusi Turtle-export.')
        expect(region).to_contain_text('Puuttuva esityspäätös')


def test_literal_nodekind_uri_does_not_become_a_namednode(page,static_site):
    text=TEXT.replace('sh:datatype xsd:date','sh:nodeKind "http://www.w3.org/ns/shacl#Literal"')
    response,_=check(page,static_site,text)
    assert not response['ok'] and response['error']['ruleId']=='NODE_KIND_UNSUPPORTED'
    server=proposal(manifest(text),{'rootShapeUri':P+'Root'})
    assert server['status']=='invalid' and server['results'][0]['ruleId']=='NODE_KIND_UNSUPPORTED'
