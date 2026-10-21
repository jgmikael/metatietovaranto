"""Count contract parity and read-only, aggregated diagnostics in the real worker."""
import copy,hashlib,json
from pathlib import Path
import pytest
from playwright.sync_api import expect
from rdflib import Graph,SH,URIRef
from apps.api.technical_packages import inspect_profile,GenerationError
from tests_static.test_browser_generation import worker,source,prepared,request_for
from tests_static.test_experiment import start,open_product,saved,stored
from scripts.browser_generation_reference import reference
ROOT=Path(__file__).resolve().parents[1]
P='https://example.org/shacl-diagnostics/'
PREFIX='''@prefix ex: <https://example.org/shacl-diagnostics/> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
ex:Root a sh:NodeShape; sh:targetClass ex:Subject; sh:property ex:Bound .
'''

def text_for(low='"0"^^xsd:int',high='"1"^^xsd:int',datatype='xsd:boolean'):
    return PREFIX+f'ex:Bound sh:path ex:flag; sh:datatype {datatype}; sh:minCount {low}; sh:maxCount {high} .'


def manifest(text):return {'sourceArtifacts':[source(text)|{'serialization':'turtle'}],'dependencies':[],'derivedArtifacts':[]}


def check(page,base,text,root=P+'Root',action='proposal'):
    profile=prepared(page,base,[source(text)])
    result=worker(page,base,{'action':action,'profile':profile,'settings':{'rootShapeUri':root,'names':[]}})
    return result,profile


@pytest.mark.parametrize('low,high,code',[
    ('"0"^^xsd:int','"1"^^xsd:int',None),('0','1',None),
    ('"+0000"^^xsd:integer','"+0001"^^xsd:integer',None),
    ('"-0"^^xsd:int','"1"^^xsd:positiveInteger',None),
    ('"0"^^xsd:unsignedByte','"1"^^xsd:unsignedLong',None),
    ('"0"^^xsd:nonNegativeInteger','"10000"^^xsd:long',None),
    ('"0"^^xsd:short','"1"^^xsd:byte',None),
    ('"-1"^^xsd:int','1','CARDINALITY_VALUE'),
    ('"0"^^xsd:positiveInteger','1','CARDINALITY_VALUE'),
    ('"256"^^xsd:unsignedByte','1000','CARDINALITY_VALUE'),
    ('"2147483648"^^xsd:int','1000','CARDINALITY_VALUE'),
    ('"0"','1','CARDINALITY_TERM'),('ex:Zero','1','CARDINALITY_TERM'),
    ('"0.0"^^xsd:decimal','1','CARDINALITY_TERM'),
    ('"0.1"^^xsd:integer','1','CARDINALITY_LEXICAL'),
    ('"1e0"^^xsd:int','1','CARDINALITY_LEXICAL'),
    ('"abc"^^xsd:int','1','CARDINALITY_LEXICAL'),
    ('2','1','CARDINALITY_CONFLICT'),
    ('0','10001','CARDINALITY_LIMIT'),
    ('"1_0"^^xsd:int','100','CARDINALITY_LEXICAL'),
    ('"١"^^xsd:int','1','CARDINALITY_LEXICAL'),
    ('"0"^^xsd:nonPositiveInteger','1',None),
    ('"-1"^^xsd:negativeInteger','1','CARDINALITY_VALUE'),
    ('"0"^^xsd:unsignedInt','"1"^^xsd:unsignedShort',None),
    ('0','9007199254740993','CARDINALITY_LIMIT'),
    ('0','"18446744073709551616"^^xsd:unsignedLong','CARDINALITY_VALUE'),
    ('0','"'+'9'*5000+'"^^xsd:integer','CARDINALITY_LIMIT'),
    ('"'+'0'*5000+'"^^xsd:integer','1',None),
])
def test_count_browser_server_parity(page,static_site,low,high,code):
    text=text_for(low,high);result,profile=check(page,static_site,text)
    if code:
        assert not result['ok'],result
        assert result['error']['ruleId']==code,result
        with pytest.raises(GenerationError) as error:inspect_profile(manifest(text),P+'Root',[])
        assert error.value.finding['ruleId']==code,error.value.finding
    else:
        assert result['ok'],result
        _,rows=inspect_profile(manifest(text),P+'Root',[])
        assert result['value']['rows'][0]['mapping']==rows[0]['mapping']
    assert profile['sources'][0]['content']==text and profile['sources'][0]['sha256']==hashlib.sha256(text.encode()).hexdigest()


def test_boolean_iri_literal_diagnostic_context_and_no_package(page,static_site):
    text=text_for(datatype='"http://www.w3.org/2001/XMLSchema#boolean"')
    result,profile=check(page,static_site,text)
    finding=next(f for f in result['findings'] if f['ruleId']=='DATATYPE_TERM')
    assert finding['category']=='sourceError' and finding['rootShapeUri']==P+'Root'
    assert finding['nodeShapeUri']==P+'Root' and finding['propertyShapes'][0]['uri']==P+'Bound'
    assert finding['propertyShapes'][0]['sources']==['source.ttl']
    assert finding['predicate']==str(SH.datatype) and finding['observed']['termType']=='Literal'
    assert finding['expected']=='IRI' and '<http://www.w3.org/2001/XMLSchema#boolean>' in finding['suggestion']
    with pytest.raises(GenerationError) as error:inspect_profile(manifest(text),P+'Root',[])
    assert error.value.finding['ruleId']=='DATATYPE_TERM'
    ref=reference();request=request_for(ref)|{'profile':profile,'settings':ref['settings']|{'profileId':profile['id'],'rootShapeUri':P+'Root'}}
    request['metadata']['profileSnapshotId']=profile['id']
    failure=worker(page,static_site,request)
    assert not failure['ok'] and failure['error']['ruleId']=='DATATYPE_TERM'
    assert 'value' not in failure


def combined():
    return PREFIX+'''ex:Root sh:property ex:P1,ex:P2,ex:P3,ex:P4,ex:P5 .
ex:Bound sh:path ex:flag; sh:datatype "http://www.w3.org/2001/XMLSchema#boolean"; sh:minCount "0"^^xsd:int;sh:maxCount "1"^^xsd:int .
'''+''.join(f'ex:P{i} sh:path owl:topObjectProperty; sh:class ex:Other; sh:name "Rooli {i}" .\n' for i in range(1,6))


def test_all_top_property_constraints_and_independent_errors(page,static_site):
    result,profile=check(page,static_site,combined())
    findings=result['findings'];assert {f['ruleId'] for f in findings}=={'DATATYPE_TERM','SEMANTIC_TOP_PROPERTY'}
    top=next(f for f in findings if f['ruleId']=='SEMANTIC_TOP_PROPERTY')
    assert top['category']=='generatorLimit' and len(top['propertyShapes'])==5
    assert [p['uri'] for p in top['propertyShapes']]==[P+'P'+str(i) for i in range(1,6)]
    assert all(p['labels']==['Rooli '+str(i)] for i,p in enumerate(top['propertyShapes'],1))
    assert profile['sources'][0]['content']==combined()


def test_compatible_repeated_paths_intersect_without_inventing_fields(page,static_site):
    text=text_for()+'''\nex:Root sh:property ex:Bound2 .
ex:Bound2 sh:path ex:flag; sh:datatype xsd:boolean; sh:minCount "1"^^xsd:int .'''
    result,_=check(page,static_site,text);assert result['ok'],result
    rows=result['value']['rows'];assert len(rows)==1 and rows[0]['mapping']['minCount']==1 and rows[0]['mapping']['maxCount']==1
    _,server_rows=inspect_profile(manifest(text),P+'Root',[])
    assert rows==server_rows
    assert len(rows[0]['shacl']['contributingConstraints'])==2
    assert result['value']['findings'][0]['category']=='warning'
    conflict=text.replace('sh:minCount "1"^^xsd:int .','sh:minCount "2"^^xsd:int .')
    response,_=check(page,static_site,conflict);assert response['error']['ruleId']=='CARDINALITY_CONFLICT'


def test_anonymous_property_shape_is_not_presented_as_uri(page,static_site):
    text=text_for(datatype='"http://www.w3.org/2001/XMLSchema#boolean"').replace('ex:Bound','_:anonymous')
    result,_=check(page,static_site,text);shape=result['findings'][0]['propertyShapes'][0]
    assert shape['uri'] is None and shape['kind']=='blankNode' and shape['sources']==['source.ttl']
    assert '_:anonymous' not in json.dumps(result)


def test_original_verovelka_export_is_unchanged_and_reports_all_blockers(page,static_site):
    file=ROOT/'fixtures/tietomallit/verovelka-2026-10-21/original.ttl';raw=file.read_bytes()
    assert hashlib.sha256(raw).hexdigest()=='576c4e7dbded346df0da2626eaac0b556ace059d36d6c8b2316416aced5969aa'
    result,profile=check(page,static_site,raw.decode(),'https://iri.suomi.fi/model/verovelka/Debtor')
    assert not result['ok']
    codes={f['ruleId'] for f in result['findings']};assert {'DATATYPE_TERM','SEMANTIC_TOP_PROPERTY'}<=codes
    assert not any(code.startswith('CARDINALITY') for code in codes)
    top=next(f for f in result['findings'] if f['ruleId']=='SEMANTIC_TOP_PROPERTY' and f['nodeShapeUri']=='https://iri.suomi.fi/model/verovelka/Debtor')
    assert len(top['propertyShapes'])==5
    assert profile['sources'][0]['content'].encode()==raw and profile['sources'][0]['sha256']==hashlib.sha256(raw).hexdigest()
    assert file.read_bytes()==raw


def test_pages_feedback_is_visible_near_proposal_button_and_source_is_preserved(page,static_site):
    start(page,static_site);open_product(page)
    text=combined();page.get_by_label('SHACL Turtle -tiedosto',exact=True).set_input_files({'name':'combined.ttl','mimeType':'text/turtle','buffer':text.encode()})
    expect(page.get_by_text('Turtle jäsennetty:',exact=False)).to_be_visible()
    page.get_by_label('Lähdeprofiilin tunniste',exact=True).fill(P)
    page.get_by_role('button',name='Liitä tuotu profiili tuotteeseen',exact=True).click()
    page.get_by_label('Generoinnin juurimuodon IRI',exact=True).fill(P+'Root')
    button=page.get_by_role('button',name='Tarkista tuki ja muodosta mapping-ehdotus',exact=True);button.click()
    expect(page.get_by_role('alert')).to_contain_text('2 estävää havaintoa')
    expect(page.locator('.generation-feedback')).to_be_focused()
    assert page.get_by_role('alert').bounding_box()['y']>=page.get_by_role('navigation',name='Ohjenavigaatio').bounding_box()['height']
    assert page.locator('.generation-feedback').evaluate('(e)=>e.previousElementSibling.textContent')=='Tarkista tuki ja muodosta mapping-ehdotus'
    report=page.get_by_role('region',name='Lähdeprofiilin havainnot')
    expect(report).to_contain_text('DATATYPE_TERM');expect(report).to_contain_text('SEMANTIC_TOP_PROPERTY')
    expect(report).to_contain_text('Rooli 5');expect(report).to_contain_text('RDF-termin tyyppi: Literal')
    expect(report).to_contain_text('Lomakkeen lisäkenttien täyttäminen ei korjaa')
    expect(page.get_by_role('button',name='Muodosta paikallinen tekninen paketti',exact=True)).to_be_disabled()
    saved(page);profile=stored(page)['localProfiles'][0]
    assert profile['sources'][0]['content']==text and profile['sources'][0]['sha256']==hashlib.sha256(text.encode()).hexdigest()
    assert not stored(page)['products'][-1]['generation'].get('package')


def test_repeated_literal_constraints_generate_one_schema_field_and_preserve_provenance(page,static_site):
    from pyld import jsonld
    from pyshacl import validate
    text=text_for('0','1')+'''\nex:Root sh:property ex:Required .
ex:Required sh:path ex:flag;sh:datatype xsd:boolean;sh:minCount 1 .'''
    _,profile=check(page,static_site,text)
    ref=reference();request=request_for(ref);request['profile']=profile
    request['metadata']['profileSnapshotId']=profile['id']
    for distribution in request['metadata']['distributions']:distribution['profileSnapshotId']=profile['id']
    request['settings']|={'profileId':profile['id'],'rootShapeUri':P+'Root','exampleContent':'{"flag":true}'}
    first=worker(page,static_site,request);assert first['ok'],first
    assert worker(page,static_site,request)==first
    artifacts=first['value']['artifacts'];schema=json.loads(artifacts['content.schema.json']['content'])
    assert list(schema['properties'])==['flag'] and schema['required']==['flag']
    refs=schema['properties']['flag']['x-mtv-shacl']['shacl']['contributingConstraints']
    assert {r['propertyShapeUri'] for r in refs}=={P+'Bound',P+'Required'}
    context=json.loads(artifacts['context.jsonld']['content'])
    example=json.loads(artifacts['unsigned-vc-example.jsonld']['content'])
    context_url=artifacts['context.jsonld']['url']
    def loader(url,options=None):
        assert url==context_url
        return {'documentUrl':url,'document':context,'contextUrl':None}
    nq=jsonld.to_rdf({'@context':context_url,**example['credentialSubject']},options={'format':'application/n-quads','documentLoader':loader})
    rdf=Graph().parse(data=nq,format='nt')
    assert len(list(rdf.triples((None,URIRef(P+'flag'),None))))==1
    assert validate(rdf,shacl_graph=Graph().parse(data=text,format='turtle'))[0]
    assert artifacts['source-0.ttl']['content']==text


def test_server_generator_preserves_turtle_spelling_without_global_normalization_change():
    import rdflib
    from apps.api.profiles import ArtifactInput,parse_artifact
    original=rdflib.NORMALIZE_LITERALS
    text=text_for('"1_0"^^xsd:int','100')
    graph,_=parse_artifact(ArtifactInput(serialization='turtle',content=text),preserve_turtle_lexical=True)
    assert str(graph.value(URIRef(P+'Bound'),SH.minCount))=='1_0'
    with pytest.raises(GenerationError) as error:inspect_profile(manifest(text),P+'Root',[])
    assert error.value.finding['ruleId']=='CARDINALITY_LEXICAL'
    assert rdflib.NORMALIZE_LITERALS==original



def test_contributing_source_iris_use_same_unicode_order_as_server(page,static_site):
    text=text_for().replace('ex:Bound','<'+P+'\ue000>')+f'\nex:Root sh:property <{P}\U00010000> . <{P}\U00010000> sh:path ex:flag;sh:datatype xsd:boolean;sh:minCount 1 .'
    result,_=check(page,static_site,text);assert result['ok'],result
    _,rows=inspect_profile(manifest(text),P+'Root',[])
    assert result['value']['rows']==rows
