"""Actual worker / server parity, independent JSON-LD+SHACL and source choices."""
import copy,json,hashlib
from pathlib import Path
import pytest
from rdflib import Graph,RDF,SH,URIRef,Literal
from rdflib.compare import isomorphic,to_isomorphic
from pyld import jsonld
from pyshacl import validate
from apps.api.conversion import ConversionError
from apps.api.technical_packages import proposal,generate,inspect_profile,normalize_rdf11
from scripts.browser_generation_reference import reference
from tests_static.test_browser_generation import worker,prepared,source
from playwright.sync_api import expect
from tests_static.test_experiment import start,open_product,saved,stored,export,open_import,upload,replace
ROOT=Path(__file__).resolve().parents[1];P='https://example.org/representation/'
LANG_TEXT=(ROOT/'fixtures/representations/language.ttl').read_text()
REF_TEXT=(ROOT/'fixtures/representations/reference.ttl').read_text()
LANG_EXAMPLE={'labels':[{'value':'Hei','language':'fi'},{'value':'Hej','language':'sv'}],'home':{'notes':{'value':'Synthetic','language':'en'}}}
REF_EXAMPLE={'label':'Synthetic','parent':['https://synthetic.example/entities/parent']}

def setup_case(page,base,text,content,choices=None):
    ref=reference();profile=prepared(page,base,[source(text)])
    metadata=copy.deepcopy(ref['metadata']);metadata['profileSnapshotId']=profile['id']
    for d in metadata['distributions']:d['profileSnapshotId']=profile['id'];d['mapping']['entries']=[]
    settings=ref['settings']|{'profileId':profile['id'],'rootShapeUri':P+'Root','exampleContent':json.dumps(content,ensure_ascii=False)}|(choices or {})
    manifest={'profileUri':profile['profileUri'],'sourceVersion':None,'sourceArtifacts':[source(text)|{'serialization':'turtle'}],'dependencies':[],'derivedArtifacts':[],'issues':[],'entryShapeUris':[P+'Root'],'vocabularyReferences':[],'graphHash':str(to_isomorphic(Graph().parse(data=text,format='turtle')).internal_hash())}
    return profile,metadata,settings,manifest


def both_proposals(page,base,profile,settings,manifest):
    return worker(page,base,{'action':'proposal','profile':profile,'settings':settings}),proposal(manifest,settings)


@pytest.mark.parametrize('kind',['language','reference'])
def test_package_parity_determinism_real_jsonld_graph_and_shacl(page,static_site,kind):
    text,content,choices=(LANG_TEXT,LANG_EXAMPLE,{'languageRepresentation':'valueLanguage-v1'}) if kind=='language' else (REF_TEXT,REF_EXAMPLE,{'references':[[P+'parent']]})
    profile,metadata,settings,manifest=setup_case(page,static_site,text,content,choices)
    b,s=both_proposals(page,static_site,profile,settings,manifest)
    assert b['ok'] and s['status']=='proposed',(b,s)
    assert b['value']['rows']==s['fields']
    request={'action':'generate','profile':profile,'metadata':metadata,'settings':settings}
    generated=worker(page,static_site,request);assert generated['ok'],generated
    assert worker(page,static_site,request)==generated
    package=generated['value'];server,_=generate(manifest,profile['sha256'],metadata,settings|{'replaceMappings':True},settings['publicationBase'])
    assert server['status']=='ready' and server['validation']['shacl']=='conforms'
    parsed=lambda pkg,name:json.loads(pkg['artifacts'][name]['content'])
    assert parsed(package,'context.jsonld')==parsed(server,'context.jsonld')
    bclaims=parsed(package,'sd-jwt-type-metadata.json')['claims'];sclaims=parsed(server,'sd-jwt-type-metadata.json')['claims']
    for c in sclaims:c['x-mtv-semantic']['sourceProfile']['snapshotUrl']=None
    assert bclaims==sclaims
    schema=parsed(package,'content.schema.json');sschema=parsed(server,'content.schema.json')
    def normalize(x):
        if isinstance(x,dict):
            if 'snapshotUrl' in x:x['snapshotUrl']=None
            for v in x.values():normalize(v)
        elif isinstance(x,list):
            for v in x:normalize(v)
    normalize(sschema);sschema.pop('x-mtv-profile');sschema.pop('x-mtv-mapping');plain=copy.deepcopy(schema);plain.pop('x-mtv-profile');plain.pop('x-mtv-mapping');assert plain==sschema
    context=parsed(package,'context.jsonld');url=package['artifacts']['context.jsonld']['url'];base=json.loads((ROOT/'fixtures/standards/credentials-v2.jsonld').read_text())
    def loader(uri,options=None):
        assert uri in {url,'https://www.w3.org/ns/credentials/v2'}
        return {'contextUrl':None,'documentUrl':uri,'document':context if uri==url else base}
    vc=parsed(package,'unsigned-vc-example.jsonld');subject=vc['credentialSubject']
    doc={'@context':url,'@graph':subject} if isinstance(subject,list) else {'@context':url,**subject}
    graph=Graph().parse(data=jsonld.to_rdf(doc,options={'documentLoader':loader,'format':'application/n-quads'}),format='nt')
    expected=Graph()
    if kind=='language':
        expected.parse(data='''@prefix ex:<https://example.org/representation/> . [] a ex:Record;ex:labels "Hei"@fi,"Hej"@sv;ex:home [a ex:AddressClass;ex:notes "Synthetic"@en] .''',format='turtle')
        assert schema['properties']['labels']['items']['properties']['language']['type']=='string'
        assert any(c['path']==['labels',None] and c['x-mtv-semantic']['term']==P+'labels' for c in bclaims)
    else:
        expected.parse(data='''@prefix ex:<https://example.org/representation/> . [] a ex:Entity;ex:label "Synthetic";ex:parent <https://synthetic.example/entities/parent> . <https://synthetic.example/entities/parent> a ex:Entity .''',format='turtle')
        assert context['@context']['parent']['@type']=='@id'
    assert isomorphic(normalize_rdf11(graph),normalize_rdf11(expected))
    conforms,_,report=validate(graph,shacl_graph=Graph().parse(data=text,format='turtle'));assert conforms,report
    jsonld.to_rdf(vc,options={'documentLoader':loader,'format':'application/n-quads'})
    assert package['validation']['shacl']=='not-run'
    assert profile['sources']==[source(text)]


@pytest.mark.parametrize('language',['','fi_FI','fi\n','FI','english','fi-u-ca-gregory',None])
def test_invalid_or_outside_profile_language_is_rejected(page,static_site,language):
    value={'value':'Hello'} if language is None else {'value':'Hello','language':language}
    profile,metadata,settings,manifest=setup_case(page,static_site,LANG_TEXT,{'labels':[value]},{'languageRepresentation':'valueLanguage-v1'})
    b=worker(page,static_site,{'action':'generate','profile':profile,'metadata':metadata,'settings':settings});assert not b['ok'],b
    with pytest.raises(ConversionError) as error:generate(manifest,profile['sha256'],metadata,settings|{'replaceMappings':True},settings['publicationBase'])
    assert error.value.finding['ruleId']=='JSON_LANGUAGE'


def test_language_choice_required_without_redefining_type(page,static_site):
    p,m,s,g=setup_case(page,static_site,LANG_TEXT,LANG_EXAMPLE)
    b,server=both_proposals(page,static_site,p,s,g)
    assert not b['ok'] and b['error']['ruleId']==server['results'][0]['ruleId']=='LANGUAGE_REPRESENTATION_REQUIRED'


@pytest.mark.parametrize('change',['required-target','sh-node','blank-node-kind','unsupported-constraint','unknown-reference'])
def test_insufficient_references_are_blocked_on_both_engines(page,static_site,change):
    text=REF_TEXT;choices={'references':[[P+'parent']]}
    if change=='required-target':text=text.replace('sh:path ex:label;', 'sh:path ex:label;sh:minCount 1;')
    if change=='sh-node':text=text.replace('sh:class ex:Entity;', 'sh:class ex:Entity;sh:node ex:Root;')
    if change=='blank-node-kind':text=text.replace('sh:class ex:Entity;', 'sh:class ex:Entity;sh:nodeKind sh:BlankNode;')
    if change=='unsupported-constraint':text=text.replace('sh:targetClass ex:Entity;', 'sh:targetClass ex:Record;')+'\nex:Target a sh:NodeShape;sh:targetClass ex:Entity;sh:closed true .'
    if change=='unknown-reference':choices={'references':[[P+'missing']]}
    p,m,s,g=setup_case(page,static_site,text,REF_EXAMPLE,choices);b,server=both_proposals(page,static_site,p,s,g)
    assert not b['ok'] and server['status']=='invalid',(b,server)
    assert b['error']['ruleId']==server['results'][0]['ruleId']


@pytest.mark.parametrize('iri',[P+'Entity','relative','https://example.org/value\n'])
def test_reference_value_is_instance_iri_not_class_or_relative(page,static_site,iri):
    p,m,s,g=setup_case(page,static_site,REF_TEXT,{'parent':[iri]},{'references':[[P+'parent']]})
    b=worker(page,static_site,{'action':'generate','profile':p,'metadata':m,'settings':s});assert not b['ok'],b
    with pytest.raises(ConversionError) as error:generate(g,p['sha256'],m,s|{'replaceMappings':True},s['publicationBase'])
    assert error.value.finding['ruleId']=='JSON_REFERENCE'


def test_general_literal_and_missing_path_are_not_guessed(page,static_site):
    for value,code in [('"http://www.w3.org/2000/01/rdf-schema#Literal"','DATATYPE_TERM'),('<http://www.w3.org/2000/01/rdf-schema#Literal>','DATATYPE_REPRESENTATION_REQUIRED')]:
        text=LANG_TEXT.replace('rdf:langString',value)
        p,m,s,g=setup_case(page,static_site,text,LANG_EXAMPLE,{'languageRepresentation':'valueLanguage-v1'});b,server=both_proposals(page,static_site,p,s,g)
        assert not b['ok'] and b['error']['ruleId']==server['results'][0]['ruleId']==code
    text=LANG_TEXT.replace('sh:path ex:labels;','')
    p,m,s,g=setup_case(page,static_site,text,LANG_EXAMPLE,{'languageRepresentation':'valueLanguage-v1'});b,server=both_proposals(page,static_site,p,s,g)
    assert b['error']['ruleId']==server['results'][0]['ruleId']=='PATH_REQUIRED'
    assert b['error']['propertyShapes'][0]['uri']==server['results'][0]['propertyShapes'][0]['uri']==P+'Labels'
    assert p['sources']==[source(text)]


@pytest.mark.parametrize('kind',['language','reference'])
def test_ui_choices_before_valid_proposal_save_reload_transfer_and_staleness(page,static_site,tmp_path,kind):
    text=LANG_TEXT if kind=='language' else REF_TEXT.replace('sh:path ex:label;','sh:path ex:id;')
    content=LANG_EXAMPLE if kind=='language' else {'entityId':'Synthetic','parent':['https://synthetic.example/entities/parent']}
    start(page,static_site);open_product(page)
    page.get_by_label('SHACL Turtle -tiedosto',exact=True).set_input_files({'name':kind+'.ttl','mimeType':'text/turtle','buffer':text.encode()})
    expect(page.get_by_text('Turtle jäsennetty:',exact=False)).to_be_visible()
    page.get_by_label('Lähdeprofiilin tunniste',exact=True).fill('urn:synthetic:'+kind)
    page.get_by_role('button',name='Liitä tuotu profiili tuotteeseen',exact=True).click()
    expect(page.get_by_text('Profiili liitetty paikalliseen tuotteeseen. Valitse juurimuoto.',exact=True)).to_be_visible()
    page.get_by_label('Generoinnin juurimuodon IRI',exact=True).fill(P+'Root')
    page.get_by_role('button',name='Tarkista tuki ja muodosta mapping-ehdotus',exact=True).click()
    expect(page.get_by_role('alert')).to_contain_text('LANGUAGE_REPRESENTATION_REQUIRED' if kind=='language' else 'RESERVED_NAME')
    choices=page.get_by_role('group',name='Esitysvalinnat ennen mapping-ehdotusta',exact=True)
    if kind=='language':choices.get_by_label('Hyväksyn kieliarvojen value/language-v1-esityksen',exact=True).check()
    else:
        choices.get_by_label('Esitysvalinnan semanttinen IRI-polku (yksi ominaisuus-IRI rivillä)',exact=True).fill(P+'parent')
        choices.get_by_role('button',name='Esitä assosiaatio IRI-viittauksena',exact=True).click()
        choices.get_by_label('Esitysvalinnan semanttinen IRI-polku (yksi ominaisuus-IRI rivillä)',exact=True).fill(P+'id')
        choices.get_by_label('Tarkastettu tekninen kenttänimi',exact=True).fill('entityId')
        choices.get_by_role('button',name='Lisää tarkastettu kenttänimi',exact=True).click()
    page.get_by_role('button',name='Tarkista tuki ja muodosta mapping-ehdotus',exact=True).click()
    expect(page.get_by_text('Generointituen tarkistus läpäisi selainversion rajauksen. Tämä ei ole SHACL-validointi.',exact=True)).to_be_visible()
    page.get_by_role('button',name='Muokkaa paikallista tuotetta',exact=True).click()
    page.get_by_label('SD-JWT VC 3: valikoiva paljastaminen',exact=True).select_option('always')
    page.get_by_role('button',name='Sulje muokkaus',exact=True).click()
    page.get_by_label('Suunniteltu HTTPS-julkaisemisen perusosoite',exact=True).fill('https://planned.example.org')
    page.get_by_label('Synteettinen yhteisen sisällön JSON-esimerkki',exact=True).fill(json.dumps(content,ensure_ascii=False))
    for label in ['Olen tarkastanut yhteiset kenttänimet ja hyväksyn paketin mapping-ehdotukset','Olen tarkastanut toimitustapojen vct-, suojaus-, algoritmi-, haltijasidonta- ja paljastamisvalinnat','Vahvistan JSON-esimerkin synteettiseksi']:
        page.get_by_label(label,exact=True).check()
    page.get_by_role('button',name='Muodosta paikallinen tekninen paketti',exact=True).click()
    expect(page.get_by_text('Paikallinen kokeilupaketti muodostettu. Ei julkaistu eikä SHACL-validoitu.',exact=True)).to_be_visible();saved(page)
    original=stored(page);assert original['localProfiles'][0]['sources'][0]['content']==text
    page.reload();saved(page);open_product(page)
    expect(page.get_by_text('Paketti vastaa tallennettuja generointisyötteitä',exact=True)).to_be_visible()
    payload=export(page,tmp_path);open_import(page);upload(page,payload)
    expect(page.get_by_role('button',name='Korvaa kokeilu tuodulla aineistolla',exact=True)).to_be_visible();replace(page);open_product(page)
    assert stored(page)['products'][-1]['generation']==original['products'][-1]['generation']
    choices=page.get_by_role('group',name='Esitysvalinnat ennen mapping-ehdotusta',exact=True)
    if kind=='language':choices.get_by_label('Hyväksyn kieliarvojen value/language-v1-esityksen',exact=True).uncheck()
    else:choices.get_by_role('button',name='Poista viittausvalinta 1',exact=True).click()
    expect(page.get_by_text('Paketti vanhentunut – muodosta uudelleen',exact=True)).to_be_visible();saved(page)
    assert not stored(page)['products'][-1]['generation']['acceptRepresentation']
    assert not stored(page)['products'][-1]['generation']['acceptFormatPolicies']
    if kind=='language':assert 'languageRepresentation' not in stored(page)['products'][-1]['generation']
    page.reload();saved(page)


def test_legacy_repair_report_survives_language_support_change(page,static_site):
    from tests_static.test_ryhti_profile import FIX,corrected_source
    report=json.loads((FIX/'repair-report.json').read_text())
    origin=worker(page,static_site,{'action':'prepare','sources':report['originalSources'],'profileUri':'https://iri.suomi.fi/model/ryhti-akr/','sourceVersion':'1.0.5'})
    assert origin['ok'] and origin['value']['sha256']==report['originalProfileSha256']
    result=worker(page,static_site,{'action':'apply-repairs','profile':origin['value'],'selected':[c['id'] for c in report['changes']]})
    assert result['ok'],result
    assert result['value']['repair']==report
    assert result['value']['sources'][0]['content']==corrected_source()
    assert worker(page,static_site,{'action':'verify','profiles':[result['value']]})['ok']


def test_reference_target_triples_share_the_server_rdf_resource_limit(page,static_site):
    text=REF_TEXT.replace('sh:maxCount 2','sh:maxCount 2000')
    p,m,s,g=setup_case(page,static_site,text,{'parent':['urn:synthetic:target:'+str(i) for i in range(1100)]},{'references':[[P+'parent']]})
    b=worker(page,static_site,{'action':'generate','profile':p,'metadata':m,'settings':s})
    assert not b['ok'] and b['error']['ruleId']=='RDF_RESOURCE_LIMIT',b
    with pytest.raises(ConversionError) as error:generate(g,p['sha256'],m,s|{'replaceMappings':True},s['publicationBase'])
    assert error.value.finding['ruleId']=='RDF_RESOURCE_LIMIT'


def test_implicit_class_target_cannot_bypass_required_content(page,static_site):
    text=REF_TEXT+'\nex:Entity a sh:NodeShape,<http://www.w3.org/2000/01/rdf-schema#Class>;sh:property [sh:path ex:required;sh:datatype xsd:string;sh:minCount 1] .'
    p,m,s,g=setup_case(page,static_site,text,REF_EXAMPLE,{'references':[[P+'parent']]})
    browser,server=both_proposals(page,static_site,p,s,g)
    assert not browser['ok'] and server['status']=='invalid'
    assert browser['error']['ruleId']==server['results'][0]['ruleId']=='REFERENCE_UNSUPPORTED'


@pytest.mark.parametrize('extra',[
    'ex:Target a sh:NodeShape;sh:targetClass ex:Entity;sh:property [sh:path <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>;sh:datatype xsd:string] .',
    'ex:Entity <http://www.w3.org/2000/01/rdf-schema#subClassOf> ex:Ancestor . ex:AncestorShape a sh:NodeShape;sh:targetClass ex:Ancestor;sh:property [sh:path ex:required;sh:minCount 1] .',
])
def test_populated_type_or_superclass_target_cannot_bypass_reference_proof(page,static_site,extra):
    text=REF_TEXT.replace('sh:targetClass ex:Entity;','sh:targetClass ex:Record;')+'\n'+extra
    p,m,s,g=setup_case(page,static_site,text,REF_EXAMPLE,{'references':[[P+'parent']]})
    browser,server=both_proposals(page,static_site,p,s,g)
    assert not browser['ok'] and server['status']=='invalid'
    assert browser['error']['ruleId']==server['results'][0]['ruleId']=='REFERENCE_UNSUPPORTED'
