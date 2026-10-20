"""Actual compiled worker, server parity, real JSON-LD/RDF and local-only UI."""
import copy,hashlib,json,re,urllib.request
from functools import lru_cache
from urllib.parse import urljoin
from pathlib import Path
import pytest
from playwright.sync_api import expect
from rdflib import Graph,Literal,URIRef,XSD
from rdflib.compare import isomorphic
from pyld import jsonld
from scripts.browser_generation_contract import contract,TARGET
from scripts.browser_generation_reference import reference
from tests_static.test_experiment import start,saved,stored,open_product,open_import,upload,replace,export,KEY
ROOT=Path(__file__).resolve().parents[1]

@lru_cache(maxsize=16)
def served_worker(base):
    # Use the served build snapshot, even if a developer rebuilds dist meanwhile.
    html=urllib.request.urlopen(base).read().decode()
    entry=re.search(r'<script[^>]+src="([^"]+)"',html).group(1)
    script=urllib.request.urlopen(urljoin(base,entry)).read().decode()
    return re.search(r'worker-[A-Za-z0-9_-]+\.js',script).group(0)


def worker(page,base,request,timeout=25000):
    page.goto(base) if page.url=='about:blank' else None
    path=served_worker(base)
    return page.evaluate('''({url,request,timeout})=>new Promise((resolve,reject)=>{const worker=new Worker(url,{type:'module'});const timer=setTimeout(()=>{worker.terminate();reject(new Error('Test worker deadline'));},timeout);worker.onmessage=e=>{clearTimeout(timer);worker.terminate();resolve(e.data);};worker.onerror=e=>{clearTimeout(timer);worker.terminate();reject(new Error(e.message));};worker.postMessage(request);})''',{'url':base+'assets/'+path,'request':request,'timeout':timeout})

def request_for(ref,action='generate'):
    return {'action':action,'profile':ref['profile'],'settings':ref['settings'],'metadata':ref['metadata']}

def source(content,name='source.ttl'):
    return {'name':name,'content':content,'sha256':hashlib.sha256(content.encode()).hexdigest()}

def prepared(page,base,files):
    result=worker(page,base,{'action':'prepare','sources':files,'profileUri':'urn:synthetic:profile','sourceVersion':None})
    assert result['ok'],result
    return result['value']

def test_shared_contract_has_not_drifted():assert json.loads(TARGET.read_text())==contract()


def test_actual_worker_determinism_server_parity_integrity_and_real_jsonld(page,static_site):
    ref=reference()
    proposal=worker(page,static_site,request_for(ref,'proposal'));assert proposal['ok'],proposal
    assert [{key:row[key] for key in ref['expected']['rows'][0]} for row in proposal['value']['rows']]==ref['expected']['rows']
    first=worker(page,static_site,request_for(ref));assert first['ok'],first
    package=first['value'];assert worker(page,static_site,request_for(ref))['value']==package
    artifacts=package['artifacts'];parsed=lambda name:json.loads(artifacts[name]['content'])
    assert parsed('context.jsonld')==ref['expected']['context']
    schema=parsed('content.schema.json');schema.pop('x-mtv-profile');schema.pop('x-mtv-mapping')
    assert schema==ref['expected']['schema']
    assert parsed('sd-jwt-type-metadata.json')['claims']==ref['expected']['claims']
    assert all(hashlib.sha256(a['content'].encode()).hexdigest()==a['sha256'] for a in artifacts.values())
    from apps.semantic_reader import verify_bundle,resolve_claim,integrity
    documents={a['url']:a['content'].encode() for a in artifacts.values()}
    metadata=artifacts['sd-jwt-type-metadata.json']['content'].encode()
    assert verify_bundle(metadata,integrity(metadata),documents.__getitem__)
    semantic=resolve_claim(metadata,integrity(metadata),['home',None,'city'],documents.__getitem__)
    assert semantic['propertyIri']=='https://external.example.org/vocab/city'
    home=next(c for c in parsed('sd-jwt-type-metadata.json')['claims'] if c['path']==['home',None,'city'])
    work=next(c for c in parsed('sd-jwt-type-metadata.json')['claims'] if c['path']==['work','city'])
    assert home['x-mtv-semantic']['shacl']['constraintPath']!=work['x-mtv-semantic']['shacl']['constraintPath']
    assert home['x-mtv-semantic']['shacl']['propertyShapeUri'] is None
    # Independent PyLD processor + manually authored expected RDF, no HTTP loader.
    context=parsed('context.jsonld');context_url=artifacts['context.jsonld']['url']
    base=json.loads((ROOT/'fixtures/standards/credentials-v2.jsonld').read_text())
    allowed={context_url:context,'https://www.w3.org/ns/credentials/v2':base}
    def loader(url,options=None):
        assert url in allowed,'Unexpected network context: '+url
        return {'contextUrl':None,'documentUrl':url,'document':allowed[url]}
    vc=parsed('unsigned-vc-example.jsonld')
    doc={'@context':context_url,**vc['credentialSubject']}
    nq=jsonld.to_rdf(doc,options={'documentLoader':loader,'format':'application/n-quads'})
    actual=Graph().parse(data=nq,format='nt')
    expected=Graph().parse(data='''@prefix ex: <https://iri.suomi.fi/model/mtv-browser-test/> . @prefix ext: <https://external.example.org/vocab/> . @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
    [] a ex:Person ; ext:registeredName "Synteettinen Oy" ; ex:home [a ext:Address;ext:city "Helsinki";ext:tags "synteettinen"];ex:work [a ext:Address;ext:city "Turku"];ex:active true;ex:amount "12.25"^^xsd:decimal;ex:count "2"^^xsd:nonNegativeInteger .''',format='turtle')
    from apps.api.technical_packages import normalize_rdf11
    assert isomorphic(normalize_rdf11(actual),normalize_rdf11(expected))
    assert isomorphic(actual,Graph().parse(data=artifacts['example.nq']['content'],format='nt'))
    from pyshacl import validate
    conforms,_,report=validate(actual,shacl_graph=Graph().parse(data=ref['profile']['sources'][0]['content'],format='turtle'))
    assert conforms,report
    assert package['validation']['shacl']=='not-run'  # Test-time SHACL is not a claimed browser feature.
    jsonld.to_rdf(vc,options={'documentLoader':loader,'format':'application/n-quads'})
    # Expected integrity does not validate modified bytes.
    bad=dict(documents);bad[artifacts['semantic-mapping.json']['url']]+=b' '
    with pytest.raises(ValueError):verify_bundle(metadata,integrity(metadata),bad.__getitem__)


@pytest.mark.parametrize('change,rule',[
    ('syntax','TURTLE_SYNTAX'),('complex','COMPLEX_PATH'),('recursive','RECURSION'),('collision','NAME_COLLISION'),('pattern','SHACL_UNSUPPORTED'),('closed','BROWSER_CLOSED_UNSUPPORTED'),('source-hash','SOURCE_HASH'),('profile-hash','PROFILE_HASH')])
def test_invalid_profiles_are_explicit(page,static_site,change,rule):
    ref=reference();text=ref['profile']['sources'][0]['content']
    if change=='syntax':text+='\n :broken [ '
    if change=='complex':text=text.replace('sh:path ex:active','sh:path [ sh:inversePath ex:active ]')
    if change=='recursive':text=text.replace('sh:node ex:AddressShape','sh:node ex:PersonShape')
    if change=='collision':text=text.replace('iow:localName "companyName"','iow:localName "active"')
    if change=='pattern':text=text.replace('sh:datatype xsd:string','sh:pattern ".*" ; sh:datatype xsd:string')
    if change=='closed':text=text.replace('ex:PersonShape a sh:NodeShape','ex:PersonShape a sh:NodeShape ; sh:closed true')
    if change in ('source-hash','profile-hash'):
        if change=='source-hash':ref['profile']['sources'][0]['content']+='\n# tampered'
        else:ref['profile']['sha256']='f'*64
        response=worker(page,static_site,request_for(ref,'proposal'))
    elif change=='syntax':response=worker(page,static_site,{'action':'inspect','sources':[source(text)]})
    else:
        profile=prepared(page,static_site,[source(text)])
        response=worker(page,static_site,request_for(ref,'proposal')|{'profile':profile})
    assert not response['ok'] and response['error']['ruleId']==rule,response


def test_local_shape_dependency_and_owl_reference_are_distinct(page,static_site):
    ref=reference();text=ref['profile']['sources'][0]['content'];index=text.index('ex:AddressShape a sh:NodeShape')
    prefix=text[:text.index('ex:PersonShape a sh:NodeShape')]
    main=source(text[:index]+'\nex:profile owl:imports <https://external.example.org/ontology> .','main.ttl')
    dependency=source(prefix+text[index:],'dependency.ttl')
    profile=prepared(page,static_site,[main]);response=worker(page,static_site,request_for(ref,'proposal')|{'profile':profile})
    assert response['error']['ruleId']=='UNRESOLVED_SHAPE'
    profile=prepared(page,static_site,[main,dependency]);response=worker(page,static_site,request_for(ref,'proposal')|{'profile':profile})
    assert response['ok'],response
    info=worker(page,static_site,{'action':'inspect','sources':[main,dependency]})['value']
    assert info['imports'][0]['resolved'] is False
    assert 'https://external.example.org/vocab/' in info['namespaces']


def test_limits_and_real_unmodified_tietomallit_export(page,static_site):
    over=worker(page,static_site,{'action':'inspect','sources':[source(' '* (256*1024+1))]})
    assert over['error']['ruleId']=='FILE_LIMIT'
    triples='@prefix ex:<urn:test:> .\n'+'\n'.join(f'ex:s{i} ex:p ex:o .' for i in range(10001))
    over=worker(page,static_site,{'action':'inspect','sources':[source(triples)]})
    assert over['error']['ruleId']=='TRIPLE_LIMIT'
    original=(ROOT/'fixtures/tietomallit/webcor-0.0.2/original.ttl').read_bytes()
    assert hashlib.sha256(original).hexdigest()=='2ad4331272558bb541b7804f194a74e261d8313985554015ccc4e23785286133'
    files=[source(original.decode())];info=worker(page,static_site,{'action':'inspect','sources':files})
    assert info['ok'] and len(info['value']['shapes'])>1
    profile=prepared(page,static_site,files)
    for root in [s['iri'] for s in info['value']['shapes'] if s['iri']]:
        result=worker(page,static_site,{'action':'proposal','profile':profile,'settings':{'rootShapeUri':root,'names':[]}})
        assert not result['ok']  # Do not repair or advertise this complete export as supported.
        assert result['error']['ruleId'] in {'OBJECT_AMBIGUOUS','SHACL_UNSUPPORTED','UNRESOLVED_SHAPE','CLASS_REQUIRED','EMPTY_SHAPE','DATATYPE_UNSUPPORTED'}
    projection=(ROOT/'fixtures/tietomallit/webcor-0.0.2/family-name-test-projection.ttl').read_text()
    profile=prepared(page,static_site,[source(projection)])
    result=worker(page,static_site,{'action':'proposal','profile':profile,'settings':{'rootShapeUri':'https://iri.suomi.fi/model/webcor/Person','names':[]}})
    assert result['ok'] and result['value']['rows'][0]['mapping']['semanticPath']==['https://iri.suomi.fi/model/eu-core/familyName']


def attach_demo(page,static_site):
    start(page,static_site);open_product(page)
    page.get_by_label('SHACL Turtle -tiedosto',exact=True).set_input_files(ROOT/'fixtures/semantic-profile-demo.ttl')
    expect(page.get_by_text('Turtle jäsennetty:',exact=False)).to_be_visible()
    page.get_by_role('button',name='Liitä tuotu profiili tuotteeseen',exact=True).click()
    expect(page.get_by_text('Profiili liitetty paikalliseen tuotteeseen. Valitse juurimuoto.',exact=True)).to_be_visible();saved(page)
    page.get_by_label('Generoinnin juurimuodon IRI',exact=True).fill('https://example.org/metatietovaranto/demo/ProductShape')
    page.get_by_role('button',name='Tarkista tuki ja muodosta mapping-ehdotus',exact=True).click()
    expect(page.get_by_text('Generointituen tarkistus läpäisi selainversion rajauksen. Tämä ei ole SHACL-validointi.',exact=True)).to_be_visible()
    page.get_by_label('Suunniteltu HTTPS-julkaisemisen perusosoite',exact=True).fill('https://planned.example.org')
    page.get_by_label('Synteettinen yhteisen sisällön JSON-esimerkki',exact=True).fill('{"companyName":"Synteettinen selain Oy"}')
    for label in ['Olen tarkastanut yhteiset kenttänimet ja hyväksyn paketin mapping-ehdotukset','Olen tarkastanut toimitustapojen vct-, suojaus-, algoritmi-, haltijasidonta- ja paljastamisvalinnat','Vahvistan JSON-esimerkin synteettiseksi']:
        page.get_by_label(label,exact=True).check()


def test_ui_import_generate_persistence_staleness_transfer_and_download(page,static_site,tmp_path):
    attach_demo(page,static_site)
    before_distributions=stored(page)['products'][-1]['metadata']['distributions']
    page.get_by_role('button',name='Muodosta paikallinen tekninen paketti',exact=True).click()
    expect(page.get_by_role('region',name='Paikallinen kokeilupaketti')).to_be_visible()
    expect(page.get_by_text('Paketti vastaa tallennettuja generointisyötteitä',exact=True)).to_be_visible();saved(page)
    before=stored(page);item=before['products'][-1];package=item['generation']['package']
    assert before['localProfiles'][0]['sources'][0]['content']==(ROOT/'fixtures/semantic-profile-demo.ttl').read_text()
    assert package['validation']['shacl']=='not-run'
    assert before['products'][-1]['metadata']['distributions']==before_distributions # Original product mappings not overwritten.
    with page.expect_download() as event:page.get_by_role('button',name='Lataa context.jsonld',exact=True).click()
    event.value.save_as(tmp_path/'local-context.jsonld')
    assert hashlib.sha256((tmp_path/'local-context.jsonld').read_bytes()).hexdigest()==package['artifacts']['context.jsonld']['sha256']
    page.reload();saved(page);open_product(page)
    expect(page.get_by_text('Paketti vastaa tallennettuja generointisyötteitä',exact=True)).to_be_visible()
    page.get_by_label('Suunniteltu HTTPS-julkaisemisen perusosoite',exact=True).fill('https://changed.example.org')
    expect(page.get_by_text('Paketti vanhentunut – muodosta uudelleen',exact=True)).to_be_visible();saved(page)
    payload=export(page,tmp_path);assert payload['localProfiles'] and payload['products'][-1]['generation']['package']==package
    # Source checksum failure must not mutate the existing whole workspace.
    open_import(page);bad=copy.deepcopy(payload);bad['localProfiles'][0]['sources'][0]['content']+='\n# tampered'
    upload(page,bad);expect(page.get_by_role('alert')).to_contain_text('SOURCE_HASH');assert stored(page)==payload_without_date(payload)
    bad=copy.deepcopy(payload);bad['products'][-1]['generation']['package']['artifacts']['context.jsonld']['content']+=' '
    upload(page,bad);expect(page.get_by_role('alert')).to_contain_text('ARTIFACT_HASH')
    # Confirmed reset and complete import restore original sources AND the stale package.
    page.once('dialog',lambda dialog:dialog.accept());page.get_by_role('button',name='Palauta alkuperäiset esimerkit',exact=True).click();saved(page)
    upload(page,payload)
    expect(page.get_by_role('button',name='Korvaa kokeilu tuodulla aineistolla',exact=True)).to_be_visible();replace(page)
    open_product(page);expect(page.get_by_text('Paketti vanhentunut – muodosta uudelleen',exact=True)).to_be_visible()
    assert stored(page)['localProfiles']==payload['localProfiles']
    # Importing a modified source as a new immutable snapshot keeps, but invalidates, the old package.
    page.get_by_label('SHACL Turtle -tiedosto',exact=True).set_input_files({'name':'changed.ttl','mimeType':'text/turtle','buffer':((ROOT/'fixtures/semantic-profile-demo.ttl').read_text()+'\n# new snapshot').encode()})
    expect(page.get_by_role('button',name='Liitä tuotu profiili tuotteeseen',exact=True)).to_be_visible()
    page.get_by_role('button',name='Liitä tuotu profiili tuotteeseen',exact=True).click()
    expect(page.get_by_text('Profiili liitetty paikalliseen tuotteeseen. Valitse juurimuoto.',exact=True)).to_be_visible();saved(page)
    expect(page.get_by_text('Paketti vanhentunut – muodosta uudelleen',exact=True)).to_be_visible()
    assert len(stored(page)['localProfiles'])==2
    assert stored(page)['products'][-1]['generation']['package']==package


def payload_without_date(payload):return {k:v for k,v in payload.items() if k!='exportedAt'}


def test_ui_syntax_size_cancel_deadline_and_no_mutation(page,static_site):
    start(page,static_site);open_product(page);before=stored(page)
    control=page.get_by_label('SHACL Turtle -tiedosto',exact=True)
    control.set_input_files({'name':'invalid.ttl','mimeType':'text/turtle','buffer':b'@prefix : BROKEN'})
    expect(page.get_by_role('alert')).to_contain_text('TURTLE_SYNTAX')
    control.set_input_files({'name':'large.ttl','mimeType':'text/turtle','buffer':b' '*(256*1024+1)})
    expect(page.get_by_role('alert')).to_contain_text('256 KiB')
    # A deliberately stalled worker proves the actual UI deadline and terminate/cancel path.
    page.context.route('**/assets/worker-*.js',lambda route:route.fulfill(status=200,content_type='text/javascript',body='self.onmessage=()=>{};'))
    control.set_input_files(ROOT/'fixtures/semantic-profile-demo.ttl')
    page.get_by_role('button',name='Keskeytä generointi',exact=True).click()
    expect(page.get_by_role('alert')).to_contain_text('keskeytetty')
    control.set_input_files(ROOT/'fixtures/semantic-profile-demo.ttl')
    expect(page.get_by_role('alert')).to_contain_text('Aikaraja 15 s ylittyi',timeout=20000)
    assert stored(page)==before


@pytest.mark.parametrize('case,rule',[('depth','RECURSION'),('fields','FIELD_LIMIT')])
def test_tree_resource_bounds(page,static_site,case,rule):
    prefix='@prefix ex:<urn:test:> . @prefix sh:<http://www.w3.org/ns/shacl#> . @prefix xsd:<http://www.w3.org/2001/XMLSchema#> .\n'
    if case=='depth':
        text=prefix+'\n'.join(f'ex:S{i} a sh:NodeShape;sh:targetClass ex:C{i};sh:property [sh:path ex:p{i};sh:node ex:S{i+1};sh:maxCount 1].' for i in range(10))+ '\nex:S10 a sh:NodeShape;sh:targetClass ex:C10;sh:property [sh:path ex:last;sh:datatype xsd:string].'
    else:text=prefix+'ex:S0 a sh:NodeShape;sh:targetClass ex:C0;sh:property '+','.join(f'[sh:path ex:p{i};sh:datatype xsd:string]' for i in range(201))+'.'
    profile=prepared(page,static_site,[source(text)])
    result=worker(page,static_site,{'action':'proposal','profile':profile,'settings':{'rootShapeUri':'urn:test:S0','names':[]}})
    assert result['error']['ruleId']==rule


@pytest.mark.parametrize('case,rule',[('schema','EXAMPLE_SCHEMA'),('non-finite','EXAMPLE_NUMBER'),('policy','FORMAT_POLICY_REQUIRED'),('disclosure','DISCLOSURE_REQUIRED'),('visible','SDJWT_DISCLOSURE'),('unknown-visible','DISCLOSURE_PATH_REVIEW'),('service','BROWSER_SERVICE_SCOPE'),('qeaa','QEAA_UNVERIFIED'),('base','PUBLICATION_BASE')])
def test_incomplete_or_conflicting_decisions_do_not_generate(page,static_site,case,rule):
    ref=reference();sd=next(d for d in ref['metadata']['distributions'] if d['type']=='sdJwtVc')
    if case=='schema':ref['settings']['exampleContent']='{}'
    if case=='non-finite':ref['settings']['exampleContent']='{"count":1e400}'
    if case=='policy':sd['security']['algorithms']=[]
    if case=='disclosure':sd['sdJwt']['selectiveDisclosure']='perClaim'
    if case=='visible':sd['sdJwt']['nonDisclosableClaims'].append('/companyName')
    if case=='unknown-visible':sd['sdJwt']['nonDisclosableClaims'].append('/noSuchField')
    if case=='service':sd['availability']='production'
    if case=='qeaa':sd['credential']['legalCategory']='QEAA'
    if case=='base':ref['settings']['publicationBase']='https://jgmikael.github.io/metatietovaranto/'
    result=worker(page,static_site,request_for(ref));assert not result['ok'] and result['error']['ruleId']==rule,result


def test_utf8_bom_crlf_and_blank_node_document_scoping(page,static_site):
    original='\ufeff'+(ROOT/'fixtures/semantic-profile-demo.ttl').read_text().replace('\n','\r\n')
    profile=prepared(page,static_site,[source(original)])
    assert profile['sources'][0]['content'].encode()==original.encode()
    # Same named blank-node labels in two files must not merge their PropertyShapes.
    prefix='@prefix ex:<urn:test:> . @prefix sh:<http://www.w3.org/ns/shacl#> . @prefix xsd:<http://www.w3.org/2001/XMLSchema#> .\n'
    main=prefix+'ex:S a sh:NodeShape;sh:targetClass ex:C;sh:property _:p . _:p sh:path ex:child;sh:node ex:T;sh:maxCount 1 .'
    child=prefix+'ex:T a sh:NodeShape;sh:targetClass ex:D;sh:property _:p . _:p sh:path ex:labelValue;sh:datatype xsd:string;sh:maxCount 1 .'
    profile=prepared(page,static_site,[source(main,'main.ttl'),source(child,'child.ttl')])
    result=worker(page,static_site,{'action':'proposal','profile':profile,'settings':{'rootShapeUri':'urn:test:S','names':[]}})
    assert result['ok'] and len(result['value']['rows'])==2,result
