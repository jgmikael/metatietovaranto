"""Opt-in source patches, full graph edit verification and offline UI workflow."""
import copy,hashlib,json
from pathlib import Path
import pytest
from playwright.sync_api import expect
from rdflib import Graph,SH,Literal,URIRef
from rdflib.compare import isomorphic
from tests_static.test_browser_generation import worker,prepared,source,request_for
from tests_static.test_experiment import start,open_product,saved,stored,export,open_import,upload,replace
from scripts.browser_generation_reference import reference
ROOT=Path(__file__).resolve().parents[1]
P='https://example.org/repair/'
X='http://www.w3.org/2001/XMLSchema#'
PREFIX='''@prefix ex:<https://example.org/repair/> .
@prefix sh:<http://www.w3.org/ns/shacl#> .
@prefix xsd:<http://www.w3.org/2001/XMLSchema#> .
ex:Root a sh:NodeShape;sh:targetClass ex:Subject;sh:property ex:Name,ex:Date .
'''
TEXT=PREFIX+'''# Keep this exact comment: sh:datatype "http://www.w3.org/2001/XMLSchema#string" .
ex:Name sh:path ex:label;sh:datatype "http://www.w3.org/2001/XMLSchema#string";sh:maxCount 1 .
ex:Date sh:path ex:date;sh:datatype "http://www.w3.org/2001/XMLSchema#date";sh:maxCount 1 .
ex:Other ex:note "http://www.w3.org/2001/XMLSchema#string";ex:label "päivä"@fi .
'''


def proposals(page,base,profile):
    r=worker(page,base,{'action':'repair-proposals','profile':profile});assert r['ok'],r;return r['value']


def apply(page,base,profile,ids):return worker(page,base,{'action':'apply-repairs','profile':profile,'selected':ids})


def test_selected_patches_only_original_bytes_graph_and_idempotence(page,static_site):
    profile=prepared(page,static_site,[source(TEXT)])
    report=proposals(page,static_site,profile);assert len(report['changes'])==2
    selected=next(c for c in report['changes'] if c['datatypeIri']==X+'string')
    r=apply(page,static_site,profile,[selected['id']]);assert r['ok'],r
    corrected=r['value'];assert corrected['repair']['originalSources']==profile['sources']
    assert profile['sources']==[source(TEXT)] and corrected['sha256']!=profile['sha256']
    content=corrected['sources'][0]['content']
    expected=TEXT[:selected['start']]+selected['after']+TEXT[selected['end']:]
    assert content==expected and hashlib.sha256(content.encode()).hexdigest()==corrected['sources'][0]['sha256']
    actual=Graph().parse(data=content,format='turtle');original=Graph().parse(data=TEXT,format='turtle')
    original.remove((URIRef(P+'Name'),SH.datatype,Literal(X+'string')));original.add((URIRef(P+'Name'),SH.datatype,URIRef(X+'string')))
    assert isomorphic(actual,original)
    assert 'ex:note "'+X+'string"' in content and '# Keep this exact comment:' in content
    assert corrected['repair']['changes']==[selected]
    assert worker(page,static_site,{'action':'verify','profiles':[corrected]})['ok']
    assert apply(page,static_site,profile,[selected['id']])==r  # Deterministic source/report/snapshot.
    fully=apply(page,static_site,profile,[c['id'] for c in report['changes']])['value']
    reimport=prepared(page,static_site,fully['sources'])
    assert proposals(page,static_site,reimport)['changes']==[]
    assert not apply(page,static_site,fully,[selected['id']])['ok']  # No chained repair model.


@pytest.mark.parametrize('value,eligible',[
    ('"'+X+'string"',True),('"'+X+'date"',True),
    ('"'+X+'string"^^xsd:string',True),
    ("'''"+X+"string'''",True),
    ('<'+X+'string>',False),('xsd:string',False),
    ('"'+X+'string"@fi',False),('"'+X+'string"^^xsd:anyURI',False),
    ('" '+X+'string"',False),('"xsd:string"',False),
    ('"https://unknown.example/type"',False),
    ('"http://www.w3.org/2000/01/rdf-schema#Literal"',False),
])
def test_allowlist_is_separate_from_rdf_parser_and_no_coercion(page,static_site,value,eligible):
    text=PREFIX+'ex:Name sh:path ex:label;sh:datatype '+value+' . ex:Date sh:path ex:date;sh:datatype xsd:date .'
    profile=prepared(page,static_site,[source(text)])
    report=proposals(page,static_site,profile)
    assert len(report['changes'])==int(eligible)
    if eligible:
        c=apply(page,static_site,profile,[report['changes'][0]['id']]);assert c['ok'],c
        assert '" '+X+'string"' not in c['value']['sources'][0]['content']
    assert profile['sources']==[source(text)]


def test_langstring_term_repair_retains_language_and_requires_representation(page,static_site):
    lang='http://www.w3.org/1999/02/22-rdf-syntax-ns#langString'
    text=PREFIX+f'ex:Name sh:path ex:label;sh:datatype "{lang}";sh:defaultValue "teksti"@fi . ex:Date sh:path ex:date;sh:datatype xsd:date .'
    profile=prepared(page,static_site,[source(text)]);c=proposals(page,static_site,profile)['changes'][0]
    result=apply(page,static_site,profile,[c['id']]);assert result['ok'],result
    fixed=result['value'];g=Graph().parse(data=fixed['sources'][0]['content'],format='turtle')
    assert next(g.objects(URIRef(P+'Name'),SH.defaultValue)).language=='fi'
    assert 'ei ole tuettu' in c['limitation']  # Historical repair-v1 report text must remain byte-compatible.
    response=worker(page,static_site,{'action':'proposal','profile':fixed,'settings':{'rootShapeUri':P+'Root','names':[]}})
    assert not response['ok'] and response['error']['ruleId']=='LANGUAGE_REPRESENTATION_REQUIRED'


@pytest.mark.parametrize('variant',['bom-crlf','blank-node','duplicate-triple','prefixed-redefinition','escaped-literal'])
def test_source_locations_and_graph_comparison_are_safe(page,static_site,variant):
    text=TEXT
    if variant=='bom-crlf':text='\ufeff'+TEXT.replace('\n','\r\n')
    if variant=='blank-node':text=text.replace('ex:Name','_:name').replace('ex:Date sh:path','[] sh:path')
    if variant=='duplicate-triple':text+='\nex:Name sh:datatype "'+X+'string" .'
    if variant=='prefixed-redefinition':text+='\n@prefix xsd:<urn:not-xsd:> . ex:Other sh:datatype "'+X+'string" .'
    if variant=='escaped-literal':text=text.replace('http://www.w3.org/2001/XMLSchema#string";',r'http:\u002f\u002fwww.w3.org/2001/XMLSchema#string";')
    profile=prepared(page,static_site,[source(text)]);items=proposals(page,static_site,profile)['changes']
    result=apply(page,static_site,profile,[c['id'] for c in items]);assert result['ok'],result
    assert result['value']['repair']['originalSources']==profile['sources']
    assert worker(page,static_site,{'action':'verify','profiles':[result['value']]})['ok']


@pytest.mark.parametrize('change',['source','before','after','line','policy','approved','hash','extra-triple'])
def test_forged_report_is_rejected_even_with_recomputed_snapshot_hash(page,static_site,change):
    profile=prepared(page,static_site,[source(TEXT)]);choices=proposals(page,static_site,profile)['changes']
    corrected=apply(page,static_site,profile,[choices[0]['id']])['value'];report=corrected['repair']
    if change=='source':report['originalSources'][0]['content']+='\n# tampered'
    if change in {'before','after'}:report['changes'][0][change]+=' '
    if change=='line':report['changes'][0]['line']+=1
    if change=='policy':report['version']='99.0.0'
    if change=='approved':report['approved']=False
    if change=='hash':report['correctedSourceHashes'][0]='0'*64
    if change=='extra-triple':
        corrected['sources'][0]=source(corrected['sources'][0]['content']+'\n<urn:extra> <urn:p> <urn:v> .')
    # Replay must reject semantic/source/report tampering before allowing a new profile hash.
    body={'profileUri':corrected['profileUri'],'sourceVersion':corrected['sourceVersion'],'sources':[{'sha256':s['sha256']} for s in corrected['sources']],
          'repair':report|{'originalSources':[{'name':s['name'],'sha256':s['sha256']} for s in report['originalSources']]}}
    corrected['sha256']=hashlib.sha256(json.dumps(body,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
    h=corrected['sha256'];corrected['id']=h[:8]+'-'+h[8:12]+'-5'+h[13:16]+'-a'+h[17:20]+'-'+h[20:32]
    verified=worker(page,static_site,{'action':'verify','profiles':[corrected]})
    assert not verified['ok'],verified
    assert verified['error']['ruleId'] in {'REPAIR_REPORT','SOURCE_HASH','PROFILE_HASH'}


def test_real_digione_original_two_errors_and_selected_correction_not_full_profile_claim(page,static_site):
    raw=(ROOT/'fixtures/tietomallit/digione-osad-2026-10-27/original.ttl').read_bytes()
    assert hashlib.sha256(raw).hexdigest()=='2ec18648da935748d2371d76885ee998279aa5b458e41d2cff12461bbb49cf75'
    ready=worker(page,static_site,{'action':'prepare','sources':[source(raw.decode(),'DigiOne - Oppijan opintotiedot (OSAD).ttl')],'profileUri':'https://iri.suomi.fi/model/digioneots/','sourceVersion':'1.0.0'})
    assert ready['ok'],ready
    profile=ready['value']
    settings={'rootShapeUri':'https://iri.suomi.fi/model/digioneots/Learner','names':[]}
    original=worker(page,static_site,{'action':'proposal','profile':profile,'settings':settings})
    assert len(original['findings'])==2 and {f['ruleId'] for f in original['findings']}=={'DATATYPE_TERM'}
    items=proposals(page,static_site,profile)['changes'];assert len(items)==51
    assert len(proposals(page,static_site,profile)['skipped'])==1  # Quoted rdfs:Literal remains manual.
    selected=[c['id'] for c in items if c['propertyShapeUri'] in {'https://iri.suomi.fi/model/digioneots/id-1','https://iri.suomi.fi/model/digioneots/rightToStudyId'}]
    result=apply(page,static_site,profile,selected);assert result['ok'],result
    remaining=worker(page,static_site,{'action':'proposal','profile':result['value'],'settings':settings})
    assert not remaining['ok'] and remaining['error']['ruleId']=='RESERVED_NAME',remaining
    reviewed=settings|{'names':[{'semanticPath':['https://iri.suomi.fi/model/digione/1.0.0/id'],'fieldName':'learnerId'}]}
    assert worker(page,static_site,{'action':'proposal','profile':result['value'],'settings':reviewed})['ok']
    assert len(proposals(page,static_site,prepared(page,static_site,result['value']['sources']))['changes'])==49
    assert result['value']['repair']['originalSources'][0]['content'].encode()==raw
    assert result['value']['sourceVersion']=='1.0.0' and result['value']['profileUri']==profile['profileUri']


def attach_bad_demo(page,base):
    text=(ROOT/'fixtures/semantic-profile-demo.ttl').read_text().replace('sh:datatype xsd:string','sh:datatype "'+X+'string"')
    start(page,base);open_product(page)
    page.get_by_label('SHACL Turtle -tiedosto',exact=True).set_input_files({'name':'bad-demo.ttl','mimeType':'text/turtle','buffer':text.encode()})
    expect(page.get_by_text('Turtle jäsennetty:',exact=False)).to_be_visible()
    page.get_by_role('button',name='Liitä tuotu profiili tuotteeseen',exact=True).click()
    expect(page.get_by_text('Profiili liitetty paikalliseen tuotteeseen. Valitse juurimuoto.',exact=True)).to_be_visible();saved(page)
    page.get_by_label('Generoinnin juurimuodon IRI',exact=True).fill('https://example.org/metatietovaranto/demo/ProductShape')
    page.get_by_role('button',name='Tarkista tuki ja muodosta mapping-ehdotus',exact=True).click()
    expect(page.get_by_role('region',name='Lähdeprofiilin havainnot')).to_contain_text('DATATYPE_TERM')
    return text


def choose_and_create(page):
    page.get_by_role('button',name='Tarkastele ehdotettuja tuontikorjauksia',exact=True).click()
    page.get_by_label('Hyväksyn korjauksen 1',exact=True).check()
    page.get_by_role('button',name='Luo korjattu paikallinen kopio',exact=True).click()
    expect(page.get_by_text('Korjattu kopio luotu ja tallennettu paikalliseen kokeiluun. Alkuperäinen on edelleen generoinnin aineistona.',exact=True)).to_be_visible()
    saved(page)


def test_ui_explicit_review_reject_selection_persistence_package_and_transfer(page,static_site,tmp_path):
    text=attach_bad_demo(page,static_site)
    before=stored(page)
    page.get_by_role('button',name='Tarkastele ehdotettuja tuontikorjauksia',exact=True).click()
    expect(page.get_by_label('Hyväksyn korjauksen 1',exact=True)).not_to_be_checked()
    assert stored(page)==before
    page.get_by_role('button',name='Hylkää korjausehdotukset',exact=True).click();saved(page)
    assert stored(page)['localProfiles']==before['localProfiles']
    page.get_by_role('button',name='Tarkista tuki ja muodosta mapping-ehdotus',exact=True).click()
    expect(page.get_by_role('region',name='Lähdeprofiilin havainnot')).to_contain_text('DATATYPE_TERM')
    choose_and_create(page)
    profiles=stored(page)['localProfiles'];assert len(profiles)==2
    assert profiles[0]['sources'][0]['content']==text
    assert stored(page)['products'][-1]['metadata']['profileSnapshotId']==profiles[0]['id']
    page.get_by_role('button',name='Käytä korjattua kopiota generoinnissa ja tarkista tuki',exact=True).click()
    expect(page.get_by_text('Valitun aineiston generointituki tarkistettu. Tämä ei ole SHACL-validointi.',exact=True)).to_be_visible()
    expect(page.get_by_role('region',name='SHACL-tuonnin paikallinen korjaus')).to_contain_text('Metatietovarannossa korjattu paikallinen kopio – ei alkuperäinen export')
    page.get_by_label('Suunniteltu HTTPS-julkaisemisen perusosoite',exact=True).fill('https://planned.example.org')
    page.get_by_label('Synteettinen yhteisen sisällön JSON-esimerkki',exact=True).fill('{"companyName":"Synteettinen Oy"}')
    for label in ['Olen tarkastanut yhteiset kenttänimet ja hyväksyn paketin mapping-ehdotukset','Olen tarkastanut toimitustapojen vct-, suojaus-, algoritmi-, haltijasidonta- ja paljastamisvalinnat','Vahvistan JSON-esimerkin synteettiseksi']:
        page.get_by_label(label,exact=True).check()
    page.get_by_role('button',name='Muodosta paikallinen tekninen paketti',exact=True).click()
    expect(page.get_by_text('Paikallinen kokeilupaketti muodostettu. Ei julkaistu eikä SHACL-validoitu.',exact=True)).to_be_visible();saved(page)
    data=stored(page);package=data['products'][-1]['generation']['package'];artifacts=package['artifacts']
    assert 'repair-report.json' in artifacts and 'original-source-0.ttl' in artifacts
    assert artifacts['original-source-0.ttl']['content']==text
    assert json.loads(artifacts['repair-report.json']['content'])==profiles[1]['repair']
    with page.expect_download() as event:page.get_by_role('button',name='Lataa korjattu Turtle 1',exact=True).click()
    event.value.save_as(tmp_path/'corrected.ttl')
    assert (tmp_path/'corrected.ttl').read_text()==profiles[1]['sources'][0]['content']
    with page.expect_download() as event:page.get_by_role('button',name='Lataa alkuperäinen Turtle 1',exact=True).click()
    event.value.save_as(tmp_path/'original.ttl');assert (tmp_path/'original.ttl').read_bytes()==text.encode()
    with page.expect_download() as event:page.get_by_role('button',name='Lataa korjausraportti',exact=True).click()
    event.value.save_as(tmp_path/'report.json');assert json.loads((tmp_path/'report.json').read_text())==profiles[1]['repair']

    page.reload();saved(page);open_product(page)
    expect(page.get_by_text('Paketti vastaa tallennettuja generointisyötteitä',exact=True)).to_be_visible()
    payload=export(page,tmp_path)
    open_import(page);upload(page,payload)
    expect(page.get_by_role('button',name='Korvaa kokeilu tuodulla aineistolla',exact=True)).to_be_visible();replace(page);open_product(page)
    assert stored(page)['localProfiles']==payload['localProfiles']
    page.get_by_role('button',name='Käytä alkuperäistä aineistoa generoinnissa',exact=True).click()
    expect(page.get_by_role('region',name='Lähdeprofiilin havainnot')).to_contain_text('DATATYPE_TERM')
    expect(page.get_by_text('Paketti vanhentunut – muodosta uudelleen',exact=True)).to_be_visible();saved(page)
    assert not stored(page)['products'][-1]['generation']['acceptRepresentation']
    assert not stored(page)['products'][-1]['generation']['acceptFormatPolicies']
    page.get_by_role('button',name='Tarkastele ehdotettuja tuontikorjauksia',exact=True).click()
    page.get_by_role('button',name='Tyhjennä korjausvalinnat',exact=True).click();saved(page)
    assert stored(page)['products'][-1]['generation']['repairSelection']==[]
    expect(page.get_by_text('Paketti vanhentunut – muodosta uudelleen',exact=True)).to_be_visible()


def test_ui_forged_report_import_keeps_existing_workspace(page,static_site,tmp_path):
    attach_bad_demo(page,static_site);choose_and_create(page)
    payload=export(page,tmp_path);before=stored(page)
    modified=copy.deepcopy(payload);modified['localProfiles'][1]['repair']['changes'][0]['after']='<urn:forged>'
    open_import(page);upload(page,modified)
    expect(page.get_by_role('alert')).to_contain_text('REPAIR_REPORT')
    assert stored(page)==before
    expect(page.get_by_role('button',name='Korvaa kokeilu tuodulla aineistolla',exact=True)).to_have_count(0)


def test_comments_inside_typed_literal_span_block_instead_of_being_removed(page,static_site):
    text=TEXT.replace('"'+X+'string";','"'+X+'string" # keep this comment\n ^^xsd:string;')
    profile=prepared(page,static_site,[source(text)])
    response=worker(page,static_site,{'action':'repair-proposals','profile':profile})
    assert not response['ok'] and response['error']['ruleId']=='REPAIR_LOCATION'
    assert profile['sources'][0]['content']==text


def test_repair_choices_are_part_of_package_binding_even_when_source_is_unchanged(page,static_site):
    ref=reference()
    text=ref['profile']['sources'][0]['content']+'\n<urn:unused:shape> <http://www.w3.org/ns/shacl#datatype> "'+X+'string" .'
    profile=prepared(page,static_site,[source(text)])
    request=request_for(ref)|{'profile':profile}
    request['settings']['profileId']=profile['id'];request['metadata']['profileSnapshotId']=profile['id']
    for d in request['metadata']['distributions']:d['profileSnapshotId']=profile['id']
    first=worker(page,static_site,request);assert first['ok'],first
    request['settings']['repairSelection']=[proposals(page,static_site,profile)['changes'][0]['id']]
    second=worker(page,static_site,request);assert second['ok'],second
    assert first['value']['binding']!=second['value']['binding']
    assert first['value']['packageId']!=second['value']['packageId']
    assert profile['sources']==[source(text)]


def test_forged_package_report_breaks_replay_even_with_recomputed_artifact_hashes(page,static_site):
    ref=reference();text=ref['profile']['sources'][0]['content'].replace('sh:datatype xsd:boolean','sh:datatype "'+X+'boolean"')
    profile=prepared(page,static_site,[source(text)]);items=proposals(page,static_site,profile)['changes']
    fixed=apply(page,static_site,profile,[c['id'] for c in items])['value']
    request=request_for(ref)|{'profile':fixed};request['settings']['profileId']=fixed['id'];request['metadata']['profileSnapshotId']=fixed['id']
    for d in request['metadata']['distributions']:d['profileSnapshotId']=fixed['id']
    result=worker(page,static_site,request);assert result['ok'],result
    package=result['value']
    assert worker(page,static_site,{'action':'verify','profiles':[fixed],'packages':[package]})['ok']
    report=json.loads(package['artifacts']['repair-report.json']['content']);report['changes'][0]['line']+=10
    report_content=json.dumps(report,separators=(',',':'),sort_keys=True,ensure_ascii=False)
    artifact=package['artifacts']['repair-report.json'];artifact['content']=report_content;artifact['sha256']=hashlib.sha256(report_content.encode()).hexdigest()
    manifest_artifact=package['artifacts']['manifest.json'];manifest=json.loads(manifest_artifact['content'])
    manifest['artifacts']['repair-report.json']['sha256']=artifact['sha256']
    manifest_artifact['content']=json.dumps(manifest,separators=(',',':'),sort_keys=True,ensure_ascii=False)
    manifest_artifact['sha256']=hashlib.sha256(manifest_artifact['content'].encode()).hexdigest()
    response=worker(page,static_site,{'action':'verify','profiles':[fixed],'packages':[package]})
    assert not response['ok'] and response['error']['ruleId']=='REPAIR_REPORT',response
