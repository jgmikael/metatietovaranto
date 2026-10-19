"""Own-experiment integration: real browser storage, only static GETs permitted."""
import copy,json
from pathlib import Path
import pytest
from playwright.sync_api import expect

KEY='fi.metatietovaranto.pages.own-experiment.v1'
FORMAT='fi.metatietovaranto.own-experiment'
DEMO='00000000-0000-4000-8000-000000000004'
TITLE='Yrityssisältö — JSON API, W3C VC ja SD-JWT VC (synteettinen demo)'


def saved(page):expect(page.get_by_role('status',name='Paikallisen tallennuksen tila')).to_have_text('Tallennettu')
def stored(page):return page.evaluate('(key)=>JSON.parse(localStorage.getItem(key)).data',KEY)
def start(page,base):
    page.goto(base);page.get_by_role('button',name='Aloita oma kokeilu',exact=True).click();saved(page)
def open_product(page,title=TITLE):page.get_by_role('button',name=title,exact=True).click()
def edit(page,title=TITLE):
    open_product(page,title);page.get_by_role('button',name='Muokkaa paikallista tuotetta',exact=True).click()
def open_import(page):page.get_by_text('JSON-tuonti ja alkuperäisten esimerkkien palautus',exact=True).click()
def upload(page,data):page.get_by_label('Tuotava kokeilutiedosto',exact=True).set_input_files({'name':'experiment.json','mimeType':'application/json','buffer':json.dumps(data).encode()})
def export(page,tmp_path):
    with page.expect_download() as event:page.get_by_role('button',name='Vie kokeilu JSONina',exact=True).click()
    path=tmp_path/'experiment.json';event.value.save_as(path);return json.loads(path.read_text())
def replace(page):
    page.once('dialog',lambda dialog:dialog.accept());page.get_by_role('button',name='Korvaa kokeilu tuodulla aineistolla',exact=True).click();saved(page)


def test_local_autosave_reload_and_public_catalogue_isolation(page,static_site):
    start(page,static_site)
    original=stored(page);edit(page)
    page.get_by_label('Nimi',exact=True).fill('OMA PAIKALLINEN YRITYS')
    saved(page)
    changed=stored(page);assert changed['products'][-1]['id']==DEMO
    assert changed['products'][-1]['metadata']['title']=='OMA PAIKALLINEN YRITYS'
    assert changed['products'][-1]['originalPackageReference']==original['products'][-1]['originalPackageReference']
    assert 'technicalPackage' not in changed['products'][-1] and 'semanticValidation' not in changed['products'][-1]
    page.reload();saved(page);open_product(page,'OMA PAIKALLINEN YRITYS')
    expect(page.get_by_text('Ei validoitu tässä kokeilussa',exact=True)).to_be_visible()
    expect(page.get_by_role('region',name='Alkuperäinen lähtöesimerkki')).to_contain_text('ei tämän tuotteen validointitulos')
    page.get_by_role('button',name='Palaa julkiseen esittelyyn',exact=True).click()
    expect(page.get_by_role('heading',name='Löydä tietotuote',exact=True)).to_be_visible()
    expect(page.get_by_role('link',name=TITLE,exact=True)).to_be_visible()
    expect(page.get_by_text('OMA PAIKALLINEN YRITYS',exact=True)).not_to_be_visible()
    page.get_by_role('button',name='Aloita oma kokeilu',exact=True).click()
    expect(page.get_by_role('heading',name='OMA PAIKALLINEN YRITYS',exact=True)).to_be_visible()
    assert stored(page)==changed


def test_product_organization_maintenance_and_references(page,static_site):
    start(page,static_site)
    page.get_by_role('button',name='Omat organisaatiot',exact=True).click()
    page.get_by_role('button',name='Demo-veroviranomainen',exact=True).click()
    page.get_by_role('button',name='Poista paikallinen organisaatio',exact=True).click()
    expect(page.get_by_role('alert')).to_contain_text('Organisaatio on käytössä')
    page.get_by_role('button',name='Lisää paikallinen organisaatio',exact=True).click()
    page.get_by_label('Organisaation virallinen nimi',exact=True).fill('Kokeilutarjoaja')
    page.get_by_role('button',name='Lisää organisaatiotunniste',exact=True).click()
    page.get_by_label('Tunnistejärjestelmä',exact=True).fill('synthetic')
    page.get_by_label('Organisaatiotunniste',exact=True).fill('DEMO-123')
    saved(page);org=next(o for o in stored(page)['organizations'] if o['legalName']=='Kokeilutarjoaja')
    page.get_by_role('button',name='Omat tietotuotteet',exact=True).click()
    page.get_by_role('button',name='Lisää paikallinen tietotuote',exact=True).click()
    page.get_by_label('Nimi',exact=True).fill('Oma uusi tuote')
    page.get_by_label('Tarjoaja',exact=True).select_option(org['id'])
    page.get_by_label('Sisältöprofiilin snapshot',exact=True).select_option(index=1)
    for label in ['JSON API','W3C VC','SD-JWT VC']:
        page.get_by_role('button',name='Lisää '+label+' -kuvaus',exact=True).click()
    saved(page);new=next(p for p in stored(page)['products'] if p['metadata']['title']=='Oma uusi tuote')
    assert len(new['metadata']['distributions'])==3 and new['profileReference']['sha256']
    # Ordinary metadata can describe a future production service, but no action becomes active.
    page.get_by_label('JSON API 1: saatavuus',exact=True).select_option('production')
    page.get_by_label('JSON API 1: palveluosoite',exact=True).fill('https://untrusted.example/source')
    saved(page);page.get_by_role('button',name='Sulje muokkaus',exact=True).click()
    expect(page.get_by_role('link',name='Käytä JSON-rajapintaa',exact=True)).to_have_count(0)
    page.get_by_role('button',name='Omat organisaatiot',exact=True).click();page.get_by_role('button',name='Kokeilutarjoaja',exact=True).click()
    page.get_by_role('button',name='Poista paikallinen organisaatio',exact=True).click();expect(page.get_by_role('alert')).to_contain_text('Organisaatio on käytössä')
    page.get_by_role('button',name='Omat tietotuotteet',exact=True).click();open_product(page,'Oma uusi tuote')
    page.once('dialog',lambda dialog:dialog.accept());page.get_by_role('button',name='Poista paikallinen tuote',exact=True).click();saved(page)
    page.get_by_role('button',name='Omat organisaatiot',exact=True).click();page.get_by_role('button',name='Kokeilutarjoaja',exact=True).click()
    page.once('dialog',lambda dialog:dialog.accept());page.get_by_role('button',name='Poista paikallinen organisaatio',exact=True).click();saved(page)
    assert not any(o['id']==org['id'] for o in stored(page)['organizations'])
    assert not any(p['id']==new['id'] for p in stored(page)['products'])


def test_export_import_confirmation_and_reset_only_own_key(page,static_site,tmp_path):
    start(page,static_site)
    page.evaluate("localStorage.setItem('unrelated.application','preserve')")
    before=stored(page);payload=export(page,tmp_path)
    assert payload['format']==FORMAT and payload['schemaVersion']==1 and payload['synthetic'] is True and payload['exportedAt']
    assert 'technicalPackage' not in json.dumps(payload) and 'csrfToken' not in json.dumps(payload)
    payload['products'][0]['metadata']['title']='Palautettu tiedostosta'
    open_import(page);upload(page,payload)
    assert stored(page)==before
    page.once('dialog',lambda dialog:dialog.dismiss());page.get_by_role('button',name='Korvaa kokeilu tuodulla aineistolla',exact=True).click()
    assert stored(page)==before
    replace(page);assert stored(page)['products'][0]['metadata']['title']=='Palautettu tiedostosta'
    page.once('dialog',lambda dialog:dialog.dismiss());page.get_by_role('button',name='Palauta alkuperäiset esimerkit',exact=True).click()
    assert stored(page)['products'][0]['metadata']['title']=='Palautettu tiedostosta'
    page.once('dialog',lambda dialog:dialog.accept());page.get_by_role('button',name='Palauta alkuperäiset esimerkit',exact=True).click();saved(page)
    assert stored(page)==before
    assert page.evaluate("localStorage.getItem('unrelated.application')")=='preserve'


@pytest.mark.parametrize('problem',['invalid-json','version','too-large','duplicate-id','broken-org','validation-claim','oversized-field','wrong-format'])
def test_invalid_import_is_atomic(page,static_site,tmp_path,problem):
    start(page,static_site);before=stored(page);payload=export(page,tmp_path);open_import(page)
    if problem=='invalid-json':raw=b'{ not json'
    elif problem=='too-large':raw=b' '*(2*1024*1024+1)
    else:
        if problem=='version':payload['schemaVersion']=999
        elif problem=='wrong-format':payload['format']='other-system'
        elif problem=='duplicate-id':payload['products'].append(copy.deepcopy(payload['products'][0]))
        elif problem=='broken-org':payload['products'][0]['metadata']['providerOrganizationId']='11111111-1111-4111-8111-111111111111'
        elif problem=='validation-claim':payload['products'][0]['semanticValidation']={'status':'conforms'}
        elif problem=='oversized-field':payload['products'][0]['metadata']['title']='X'*201
        raw=json.dumps(payload).encode()
    page.get_by_label('Tuotava kokeilutiedosto',exact=True).set_input_files({'name':'bad.json','mimeType':'application/json','buffer':raw})
    expect(page.get_by_role('alert')).to_contain_text('Tuonti epäonnistui')
    expect(page.get_by_role('button',name='Korvaa kokeilu tuodulla aineistolla',exact=True)).to_have_count(0)
    assert stored(page)==before


def test_untrusted_strings_and_missing_references_are_not_resolved_or_promoted(page,static_site,tmp_path):
    start(page,static_site);payload=export(page,tmp_path)
    product=payload['products'][-1];product['metadata']['title']='<img src="https://untrusted.example/pixel" onerror="window.injected=1">'
    missing='11111111-1111-4111-8111-111111111111'
    product['profileReference']={'snapshotId':missing,'sha256':'a'*64};product['metadata']['profileSnapshotId']=missing
    for d in product['metadata']['distributions']:
        d['profileSnapshotId']=missing
        if d['type']=='jsonApi':d['api']['serviceUrl']='javascript:window.injected=1';d['availability']='production'
    product['originalPackageReference']['packageId']='b'*64
    open_import(page);upload(page,payload);replace(page);open_product(page,product['metadata']['title'])
    expect(page.get_by_role('alert').filter(has_text='Puuttuva profiiliviittaus')).to_be_visible()
    expect(page.get_by_role('alert').filter(has_text='Puuttuva artefaktiviittaus')).to_be_visible()
    expect(page.get_by_text('Ei validoitu tässä kokeilussa',exact=True)).to_be_visible()
    assert page.evaluate('window.injected') is None
    expect(page.locator('img')).to_have_count(0)
    expect(page.locator('a[href^="javascript:"]')).to_have_count(0)
    page.reload();saved(page)
    assert stored(page)['products'][-1]['profileReference']['snapshotId']==missing


@pytest.mark.parametrize('error_name',['QuotaExceededError','SecurityError'])
def test_storage_failure_keeps_memory_and_export_then_retry(page,static_site,tmp_path,error_name):
    page.add_init_script(f"""window.originalSet=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){{if(k==='{KEY}')throw new DOMException('Blocked','{error_name}');return window.originalSet.call(this,k,v);}};""")
    page.goto(static_site+'#kokeilu')
    expect(page.get_by_role('status',name='Paikallisen tallennuksen tila')).to_have_text('Tallennus epäonnistui')
    edit(page);page.get_by_label('Nimi',exact=True).fill('Muistissa säilyvä kokeilu')
    expect(page.get_by_role('alert')).to_contain_text('Muutokset ovat muistissa')
    assert export(page,tmp_path)['products'][-1]['metadata']['title']=='Muistissa säilyvä kokeilu'
    assert page.evaluate('(key)=>localStorage.getItem(key)',KEY) is None
    page.evaluate('() => {Storage.prototype.setItem=window.originalSet;}')
    page.get_by_role('button',name='Yritä tallennusta uudelleen',exact=True).click();saved(page)
    assert stored(page)['products'][-1]['metadata']['title']=='Muistissa säilyvä kokeilu'


@pytest.mark.parametrize('raw',['{broken json',json.dumps({'storageVersion':999,'data':{}})])
def test_corrupt_or_unknown_storage_is_preserved_until_confirmed_reset(page,static_site,raw):
    page.add_init_script('(function(){localStorage.setItem('+json.dumps(KEY)+','+json.dumps(raw)+');})()')
    page.goto(static_site+'#kokeilu')
    expect(page.get_by_role('alert')).to_contain_text('Tallennetta ei korvattu')
    expect(page.get_by_role('button',name='Lataa alkuperäinen tallenne talteen',exact=True)).to_be_visible()
    assert page.evaluate('(key)=>localStorage.getItem(key)',KEY)==raw
    open_import(page)
    page.once('dialog',lambda dialog:dialog.dismiss());page.get_by_role('button',name='Palauta alkuperäiset esimerkit',exact=True).click()
    assert page.evaluate('(key)=>localStorage.getItem(key)',KEY)==raw
    page.once('dialog',lambda dialog:dialog.accept());page.get_by_role('button',name='Palauta alkuperäiset esimerkit',exact=True).click();saved(page)
    assert len(stored(page)['products'])==4


def test_two_tabs_conflict_preserves_losing_edits_and_requires_reload(page,static_site,tmp_path):
    start(page,static_site)
    second=page.context.new_page();second.goto(static_site+'#kokeilu');saved(second)
    edit(page);edit(second)
    # Queue both writes behind a real Web Lock to test compare-and-write, not just storage events.
    page.evaluate('''(key)=>{window.lockHeld=false;navigator.locks.request(key,()=>new Promise(resolve=>{window.releaseExperimentLock=resolve;window.lockHeld=true;}));}''',KEY)
    page.wait_for_function('window.lockHeld===true')
    page.get_by_label('Nimi',exact=True).fill('Välilehti A')
    # Establish queue order explicitly: timers in background tabs may be throttled.
    page.wait_for_function('(async()=> (await navigator.locks.query()).pending.length===1)')
    second.get_by_label('Nimi',exact=True).fill('Välilehti B')
    page.wait_for_function('(async()=> (await navigator.locks.query()).pending.length===2)')
    page.evaluate('window.releaseExperimentLock()')
    expect(page.get_by_role('status',name='Paikallisen tallennuksen tila')).to_have_text('Tallennettu')
    expect(second.get_by_role('alert')).to_contain_text('toisessa välilehdessä')
    assert export(second,tmp_path)['products'][-1]['metadata']['title']=='Välilehti B'
    assert stored(page)['products'][-1]['metadata']['title']=='Välilehti A'
    second.once('dialog',lambda dialog:dialog.accept());second.get_by_role('button',name='Avaa selaimen tallennettu kokeilu',exact=True).click();saved(second)
    expect(second.get_by_label('Nimi',exact=True)).to_have_value('Välilehti A')


def test_import_storage_failure_does_not_replace_existing_workspace(page,static_site,tmp_path):
    start(page,static_site);before=stored(page);payload=export(page,tmp_path)
    payload['products'][0]['metadata']['title']='Ei saa korvata tallennusvirheessä'
    page.evaluate('''(key)=>{window.originalSet=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){if(k===key)throw new DOMException('Quota exceeded','QuotaExceededError');return window.originalSet.call(this,k,v);};}''',KEY)
    open_import(page);upload(page,payload)
    page.once('dialog',lambda dialog:dialog.accept());page.get_by_role('button',name='Korvaa kokeilu tuodulla aineistolla',exact=True).click()
    expect(page.get_by_role('alert')).to_contain_text('Nykyistä kokeilua ei muutettu')
    assert stored(page)==before
    assert export(page,tmp_path)['products']==before['products']
    page.evaluate('() => {Storage.prototype.setItem=window.originalSet;}')
    replace(page)
    assert stored(page)['products'][0]['metadata']['title']=='Ei saa korvata tallennusvirheessä'


def test_read_access_failure_preserves_saved_data_and_can_return_to_public(page,static_site):
    start(page,static_site);before=page.evaluate('(key)=>localStorage.getItem(key)',KEY)
    page.add_init_script(f"""window.originalGet=Storage.prototype.getItem;Storage.prototype.getItem=function(k){{if(k==='{KEY}')throw new DOMException('Blocked','SecurityError');return window.originalGet.call(this,k);}};""")
    page.reload()
    expect(page.get_by_role('alert')).to_contain_text('Tallennetta ei korvattu')
    assert page.evaluate('(key)=>window.originalGet.call(localStorage,key)',KEY)==before
    page.get_by_role('button',name='Palaa julkiseen esittelyyn',exact=True).click()
    expect(page.get_by_role('heading',name='Löydä tietotuote',exact=True)).to_be_visible()
    page.evaluate('() => {Storage.prototype.getItem=window.originalGet;}')
    page.get_by_role('button',name='Aloita oma kokeilu',exact=True).click()
    page.get_by_role('button',name='Avaa selaimen tallennettu kokeilu',exact=True).click();saved(page)
    assert page.evaluate('(key)=>localStorage.getItem(key)',KEY)==before


def test_new_pages_version_does_not_overwrite_local_data_or_missing_sources(page,static_site):
    start(page,static_site);edit(page);page.get_by_label('Nimi',exact=True).fill('Säilyy uuden demon yli');saved(page)
    before=page.evaluate('(key)=>localStorage.getItem(key)',KEY)
    catalogue=page.request.get(static_site+'demo/catalog.json').json()
    catalogue['version']='2.0.0';catalogue['profiles']=[];catalogue['items'][-1].pop('technicalPackage')
    page.route('**/demo/catalog.json',lambda route:route.fulfill(json=catalogue))
    page.reload();saved(page)
    expect(page.get_by_text('Esittelyaineiston versio on vaihtunut.',exact=False)).to_be_visible()
    assert page.evaluate('(key)=>localStorage.getItem(key)',KEY)==before
    open_product(page,'Säilyy uuden demon yli')
    expect(page.get_by_role('alert').filter(has_text='Puuttuva profiiliviittaus')).to_be_visible()
    expect(page.get_by_role('alert').filter(has_text='Puuttuva artefaktiviittaus')).to_be_visible()


def test_mapping_edit_does_not_reuse_original_validation_claims(page,static_site):
    start(page,static_site);original=stored(page)['products'][-1]['originalPackageReference'];edit(page)
    page.get_by_label('JSON API 1, kenttä 1: tietotyypin IRI',exact=True).fill('http://www.w3.org/2001/XMLSchema#integer')
    saved(page);local=stored(page)['products'][-1]
    assert local['metadata']['distributions'][0]['mapping']['entries'][0]['datatype'].endswith('#integer')
    assert local['originalPackageReference']==original
    assert not any(k in local for k in ['technicalPackage','semanticValidation','distributionValidation','status'])
    expect(page.get_by_text('Ei validoitu tässä kokeilussa',exact=True)).to_be_visible()
    expect(page.get_by_role('region',name='Alkuperäinen lähtöesimerkki')).to_contain_text('ei tämän tuotteen validointitulos')
