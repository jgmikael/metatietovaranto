"""Real browser smoke tests against a separately started demo (opt-in)."""
import os
import shutil
import uuid
import re
import pytest
import httpx
from playwright.sync_api import sync_playwright, expect

# Bounded validation spawns several offline workers; this is a correctness suite, not a latency benchmark.
expect.set_options(timeout=20000)

pytestmark=pytest.mark.skipif(not os.getenv('BROWSER_BASE_URL'), reason='Set BROWSER_BASE_URL to run live browser tests')

@pytest.fixture
def page():
    with sync_playwright() as playwright:
        executable=os.getenv('CHROMIUM_EXECUTABLE') or shutil.which('chromium')
        browser=playwright.chromium.launch(executable_path=executable,headless=True)
        page=browser.new_page()
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        yield page
        browser.close()
        assert not errors

def login(page, username='vero', password='demo-vero'):
    page.goto(os.environ['BROWSER_BASE_URL']+'/auth/login')
    page.locator('#username').fill(username)
    page.locator('#password').fill(password)
    page.locator('#kc-login').click()
    expect(page.get_by_role('button',name='Kirjaudu ulos',exact=True)).to_be_visible()
    expect(page.get_by_text(username,exact=True)).to_be_visible()
    cookie=next(cookie for cookie in page.context.cookies() if cookie['name']=='mtv_session')
    assert cookie['httpOnly'] and cookie['sameSite']=='Lax'
    assert cookie['secure']==os.environ['BROWSER_BASE_URL'].startswith('https://')


def delete_test_product(page, product_id):
    base=os.environ['BROWSER_BASE_URL']
    identity=page.request.get(base+'/auth/me').json()
    draft=page.request.get(f'{base}/api/v1/products/{product_id}/draft')
    if draft.status==200:
        return page.request.delete(f'{base}/api/v1/products/{product_id}',
            headers={'X-CSRF-Token':identity.get('csrfToken',''),'If-Match':draft.json()['etag']})


def test_search_detail_edit_create_delete(page):
    base=os.environ['BROWSER_BASE_URL'];title='Selaintesti '+uuid.uuid4().hex;created_id=None
    login(page)
    try:
        page.get_by_role('button',name='Lisää tietotuote',exact=True).click()
        for label,value in [('Nimi',title),('Kuvaus','<script>window.injected=true</script>'),('Teema','Testit'),('Synteettinen lähde','Synteettinen fixture'),('Käyttötarkoitus','Selaimen tallennustesti'),('Rajaukset — mitä tuote ei todista','Ei aitoja tietoja')]:
            page.get_by_label(label,exact=True).fill(value)
        page.get_by_label('Tarjoaja',exact=True).select_option(index=1)
        page.get_by_role('button',name='Tallenna',exact=True).click()
        expect(page.get_by_role('heading',name=title,exact=True)).to_be_visible()
        created_id=page.url.split('#draft/')[1]
        assert page.evaluate('window.injected') is None
        assert httpx.get(f'{base}/api/v1/products/{created_id}').status_code==404
        page.reload();expect(page.get_by_role('heading',name=title,exact=True)).to_be_visible()
        page.get_by_role('button',name='Muokkaa',exact=True).click()
        page.get_by_label('Nimi',exact=True).fill(title+' muokattu')
        page.get_by_role('button',name='Tallenna',exact=True).click()
        expect(page.get_by_role('heading',name=title+' muokattu',exact=True)).to_be_visible()
        page.once('dialog',lambda dialog:dialog.accept())
        page.get_by_role('button',name='Poista tietotuote',exact=True).click()
        expect(page.get_by_role('heading',name='Omat luonnokset',exact=True)).to_be_visible()
    finally:
        if created_id:delete_test_product(page,created_id)


def test_mobile_search(page):
    page.set_viewport_size({'width':390,'height':844});page.goto(os.environ['BROWSER_BASE_URL'])
    expect(page.get_by_role('heading',name='Löydä tietotuote')).to_be_visible()
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')


def test_organization_navigation_and_provider_link(page):
    base=os.environ['BROWSER_BASE_URL'];page.goto(base)
    page.get_by_role('link',name='Organisaatiot',exact=True).click()
    page.get_by_role('link',name='Demo-veroviranomainen',exact=True).click()
    expect(page.get_by_role('heading',name='Demo-veroviranomainen',exact=True)).to_be_visible()
    expect(page.get_by_text('Organisaatiotunnisteet',exact=True)).to_be_visible()
    page.reload();expect(page.get_by_role('heading',name='Demo-veroviranomainen',exact=True)).to_be_visible()
    login(page);page.get_by_role('link',name='Omat luonnokset',exact=True).click()
    page.get_by_role('link',name='Verovelkatieto — synteettinen demo',exact=True).click()
    page.get_by_role('link',name='Demo-veroviranomainen',exact=True).click()
    expect(page.get_by_role('heading',name='Demo-veroviranomainen',exact=True)).to_be_visible()


def logout(page):
    page.get_by_role('button',name='Kirjaudu ulos',exact=True).click();page.locator('#kc-logout').click()
    expect(page.get_by_role('link',name='Kirjaudu sisään',exact=True)).to_be_visible()


def test_anonymous_reader_and_logout(page):
    base=os.environ['BROWSER_BASE_URL'];page.goto(base)
    expect(page.get_by_role('link',name='Kirjaudu sisään',exact=True)).to_be_visible()
    expect(page.get_by_role('button',name='Lisää tietotuote',exact=True)).to_have_count(0)
    assert page.request.get(base+'/api/v1/products/00000000-0000-4000-8000-000000000001').status==404
    login(page,'lukija','demo-lukija')
    page.get_by_role('link',name='Omat luonnokset',exact=True).click()
    page.get_by_role('link',name='Verovelkatieto — synteettinen demo',exact=True).click()
    expect(page.get_by_role('button',name='Muokkaa',exact=True)).to_have_count(0)
    expect(page.get_by_role('button',name='Hyväksy',exact=True)).to_have_count(0)
    logout(page);page.reload();expect(page.get_by_role('link',name='Kirjaudu sisään',exact=True)).to_be_visible()
    login(page);expect(page.get_by_role('button',name='Lisää tietotuote',exact=True)).to_be_visible()


def test_second_organization_editor_is_isolated(page):
    login(page,'yritys','demo-yritys');page.get_by_role('link',name='Omat luonnokset',exact=True).click()
    page.get_by_role('link',name='Verovelkatieto — synteettinen demo',exact=True).click()
    expect(page.get_by_role('button',name='Muokkaa',exact=True)).to_have_count(0)
    page.get_by_role('link',name='Omat luonnokset',exact=True).click()
    page.get_by_role('link',name='Yrityksen perustiedot — synteettinen demo',exact=True).click()
    page.get_by_role('button',name='Muokkaa',exact=True).click()
    expect(page.get_by_label('Tarjoaja',exact=True)).to_have_value('fde32818-c368-5a6c-9804-a5ea7a9dcc98')
    expect(page.get_by_label('Tarjoaja',exact=True).locator('option')).to_have_count(2)


def test_expired_ui_session_returns_to_login(page):
    base=os.environ['BROWSER_BASE_URL'];login(page)
    page.get_by_role('link',name='Omat luonnokset',exact=True).click()
    page.get_by_role('link',name='Verovelkatieto — synteettinen demo',exact=True).click()
    page.get_by_role('button',name='Muokkaa',exact=True).click()
    identity=page.request.get(base+'/auth/me').json()
    assert page.request.post(base+'/auth/logout',headers={'X-CSRF-Token':identity['csrfToken']}).status==204
    page.get_by_role('button',name='Tallenna',exact=True).click()
    expect(page.get_by_role('link',name='Kirjaudu sisään',exact=True)).to_be_visible()
    expect(page.get_by_role('button',name='Tallenna',exact=True)).to_have_count(0)


def test_profile_import_separate_approval_publication_and_public_search(page):
    """Two real OIDC users, file ingestion and immutable public export; no auth bypass."""
    from pathlib import Path
    base=os.environ['BROWSER_BASE_URL'];title='Julkaisutesti '+uuid.uuid4().hex
    login(page);page.get_by_role('button',name='Lisää tietotuote',exact=True).click()
    page.get_by_label('Tarjoaja',exact=True).select_option(index=1)
    for label,value in [('Nimi',title),('Kuvaus','Synteettinen julkaisuketjun selaintesti'),('Teema','Testit'),('Synteettinen lähde','Ei oikeaa rekisteriä'),('Käyttötarkoitus','Julkaisuketjun testi'),('Rajaukset — mitä tuote ei todista','Ei oikeita todistuksia')]:
        page.get_by_label(label,exact=True).fill(value)
    page.get_by_text('Tuo Tietomallit-soveltamisprofiili',exact=True).click()
    page.get_by_label('Profiilin alkuperäinen IRI',exact=True).fill('https://example.org/metatietovaranto/demo/profile')
    page.get_by_label('OWL-sanaston nimiavaruus',exact=True).fill('https://example.org/metatietovaranto/demo/')
    page.get_by_label('Lähdeilmoitus',exact=True).fill('Synteettinen testifixture; ei oikea Tietomallit-export. Vain ohjelmistotesti.')
    page.get_by_label('SHACL-tiedosto tai johdannainen',exact=True).set_input_files(str(Path('fixtures/semantic-profile-demo.ttl').resolve()))
    page.get_by_role('button',name='Tuo profiili',exact=True).click()
    expect(page.get_by_role('status')).to_contain_text('Profiilisnapshot tallennettu')
    page.get_by_label('Esimerkin RDF-sisältö',exact=True).fill('<urn:unrelated> <urn:name> "Synteettinen kohdistamaton tieto".')
    page.get_by_label('Vahvistan, että esimerkki on synteettinen eikä sisällä henkilötietoja tai salaisuuksia',exact=True).check()
    page.get_by_role('button',name='Tallenna',exact=True).click()
    expect(page.get_by_text('SHACL-tarkistus ei läpäissyt',exact=True)).to_be_visible()
    page.get_by_role('button',name='Lähetä tarkastukseen',exact=True).click()
    expect(page.get_by_role('alert')).to_contain_text('rdf:type')
    page.get_by_role('button',name='Muokkaa',exact=True).click()
    page.get_by_label('Esimerkkitiedosto',exact=True).set_input_files(str(Path('fixtures/semantic-example-demo.ttl').resolve()))
    expect(page.get_by_label('Esimerkin RDF-sisältö',exact=True)).to_have_value(re.compile('Synteettinen Esimerkki Oy'))
    page.get_by_label('Vahvistan, että esimerkki on synteettinen eikä sisällä henkilötietoja tai salaisuuksia',exact=True).check()
    page.get_by_role('button',name='Tallenna',exact=True).click()
    expect(page.get_by_role('heading',name=title,exact=True)).to_be_visible()
    expect(page.get_by_text('Esimerkki läpäisee SHACL-tarkistuksen',exact=True)).to_be_visible()
    product_id=page.url.split('#draft/')[1]
    page.get_by_role('button',name='Lähetä tarkastukseen',exact=True).click()
    expect(page.get_by_text('Tarkastuksessa',exact=True)).to_be_visible()
    expect(page.get_by_role('button',name='Hyväksy',exact=True)).to_have_count(0)
    logout(page);login(page,'yritys','demo-yritys');page.goto(base+'/#draft/'+product_id)
    expect(page.get_by_role('heading',name=title,exact=True)).to_be_visible()
    page.get_by_label('Tarkastuksen perustelu',exact=True).fill('Synteettinen lähdeilmoitus ja profiiligraafi tarkastettu vain ohjelmistotestinä.')
    page.get_by_label('Olen tarkastanut lähdeilmoituksen, SHACL-profiilin ja sen riippuvuudet',exact=True).check()
    page.get_by_role('button',name='Hyväksy',exact=True).click()
    expect(page.get_by_text('Hyväksytty',exact=True)).to_be_visible()
    page.get_by_label('Julkaisuversio',exact=True).fill('1.0.0')
    page.get_by_role('button',name='Julkaise',exact=True).click()
    expect(page.get_by_text('Julkaistu versio 1.0.0',exact=True)).to_be_visible()
    assert page.get_by_role('link',name='JSON-LD',exact=True).get_attribute('href').endswith('format=jsonld&version=1.0.0')
    expect(page.get_by_text('Lompakkotodistus suunnitteilla',exact=True)).to_be_visible()
    expect(page.get_by_role('link',name='Pyydä todistus lompakkoon',exact=True)).to_have_count(0)
    first=httpx.get(base+'/api/v1/products/'+product_id+'/versions/1.0.0').json()
    logout(page);page.goto(base)
    page.get_by_label('Hakusana',exact=True).fill(title);page.get_by_role('button',name='Hae',exact=True).click()
    expect(page.get_by_role('status')).to_have_text('1 tietotuotetta')
    page.get_by_role('link',name=title,exact=True).click()
    expect(page.get_by_role('heading',name=title,exact=True)).to_be_visible()
    assert httpx.get(base+'/api/v1/products/'+product_id+'/versions/1.0.0').json()==first
    # Published fixtures intentionally remain as immutable history in this demo DB.


def test_derived_schema_import_example_correction_and_publication(page):
    from pathlib import Path
    base=os.environ['BROWSER_BASE_URL'];title='JSON-johdannaistesti '+uuid.uuid4().hex
    login(page);page.get_by_role('button',name='Lisää tietotuote',exact=True).click()
    page.get_by_label('Tarjoaja',exact=True).select_option(index=1)
    for label,value in [('Nimi',title),('Kuvaus','Synteettinen JSON-johdannaisen koe'),('Teema','Testit'),('Synteettinen lähde','Ei oikea Tietomallit-export'),('Käyttötarkoitus','Johdannaisten validointikoe'),('Rajaukset — mitä tuote ei todista','Ei VC-todistuksia tai tuotantopalvelua')]:
        page.get_by_label(label,exact=True).fill(value)
    page.get_by_text('Tuo Tietomallit-soveltamisprofiili',exact=True).click()
    page.get_by_label('Profiilin alkuperäinen IRI',exact=True).fill('https://example.org/metatietovaranto/demo/profile')
    page.get_by_label('OWL-sanaston nimiavaruus',exact=True).fill('https://example.org/metatietovaranto/demo/')
    page.get_by_label('Lähdeilmoitus',exact=True).fill('Synteettinen ohjelmistotesti, ei oikea alustavienti tai rekisteriote.')
    page.get_by_label('SHACL-tiedosto tai johdannainen',exact=True).set_input_files(str(Path('fixtures/semantic-profile-demo.ttl').resolve()))
    page.get_by_label('Liitä JSON Schema- tai OpenAPI-johdannainen',exact=True).check()
    page.get_by_label('Johdannaisen JSON-tiedosto',exact=True).set_input_files(str(Path('fixtures/derived-schema-demo.json').resolve()))
    page.get_by_label('Semanttisen kartoituksen JSON-tiedosto',exact=True).set_input_files(str(Path('fixtures/derived-mappings-demo.json').resolve()))
    expect(page.get_by_label('Semanttiset kenttäkartoitukset (JSON)',exact=True)).to_have_value(re.compile('ProductShape'))
    page.get_by_role('button',name='Tuo profiili',exact=True).click()
    expect(page.get_by_role('status')).to_contain_text('Profiilisnapshot tallennettu')
    page.get_by_label('Esimerkkitiedosto',exact=True).set_input_files(str(Path('fixtures/semantic-example-demo.ttl').resolve()))
    expect(page.get_by_label('Esimerkin RDF-sisältö',exact=True)).to_have_value(re.compile('Synteettinen Esimerkki Oy'))
    page.get_by_label('Vahvistan, että esimerkki on synteettinen eikä sisällä henkilötietoja tai salaisuuksia',exact=True).check()
    page.get_by_label('Johdannainen 1: JSON-esimerkkisisältö',exact=True).fill('{"companyName":123}')
    page.get_by_label('Johdannainen 1: vahvistan JSON-esimerkin synteettisyyden',exact=True).check()
    page.get_by_role('button',name='Tallenna',exact=True).click()
    expect(page.get_by_text('Johdannaisten tarkistus ei läpäissyt',exact=True)).to_be_visible()
    page.get_by_role('button',name='Lähetä tarkastukseen',exact=True).click()
    expect(page.get_by_role('alert')).to_contain_text('JSON-esimerkki')
    product_id=page.url.split('#draft/')[1]
    page.get_by_role('button',name='Muokkaa',exact=True).click()
    page.get_by_label('Johdannainen 1: JSON-esimerkkitiedosto',exact=True).set_input_files(str(Path('fixtures/derived-example-demo.json').resolve()))
    expect(page.get_by_label('Johdannainen 1: JSON-esimerkkisisältö',exact=True)).to_have_value(re.compile('Synteettinen Esimerkki Oy'))
    page.get_by_label('Johdannainen 1: vahvistan JSON-esimerkin synteettisyyden',exact=True).check()
    page.get_by_role('button',name='Tallenna',exact=True).click()
    expect(page.get_by_text('Johdannaisten rajattu tarkistus läpäisty',exact=True)).to_be_visible()
    page.get_by_role('button',name='Lähetä tarkastukseen',exact=True).click()
    expect(page.get_by_text('Tarkastuksessa',exact=True)).to_be_visible()
    logout(page);login(page,'yritys','demo-yritys');page.goto(base+'/#draft/'+product_id)
    expect(page.get_by_role('heading',name=title,exact=True)).to_be_visible()
    page.get_by_label('Tarkastuksen perustelu',exact=True).fill('Synteettiset SHACL/JSON-skeema/esimerkit ja suorat semanttiset kartoitukset tarkastettu.')
    page.get_by_label('Olen tarkastanut lähdeilmoituksen, SHACL-profiilin ja sen riippuvuudet',exact=True).check()
    page.get_by_role('button',name='Hyväksy',exact=True).click()
    page.get_by_role('button',name='Julkaise',exact=True).click()
    expect(page.get_by_text('Julkaistu versio 1.0.0',exact=True)).to_be_visible()
    expect(page.get_by_text('Johdannaisten rajattu tarkistus läpäisty',exact=True)).to_be_visible()
    link=page.get_by_role('link',name='Johdannainen 1: lataa alkuperäinen skeema',exact=True)
    assert page.request.get(base+link.get_attribute('href')).status==200
    logout(page);page.goto(base+'/#'+product_id)
    expect(page.get_by_text('Johdannaisten rajattu tarkistus läpäisty',exact=True)).to_be_visible()
    snapshot=httpx.get(base+'/api/v1/products/'+product_id).json()
    assert snapshot['derivedValidation']['status']=='conforms' and snapshot['derivedExamples'][0]['synthetic'] is True


def test_parallel_distributions_edit_publish_and_format_specific_links(page):
    base=os.environ['BROWSER_BASE_URL'];title='Kolme toimitustapaa '+uuid.uuid4().hex
    login(page)
    sample=page.request.get(base+'/api/v1/products/00000000-0000-4000-8000-000000000004/draft').json()
    fields=('title','description','providerOrganizationId','theme','source','purpose','limitations','accessConditions','availability','synthetic','profileSnapshotId','issuance','syntheticExample','derivedExamples','distributions','primaryDistributionId')
    data={key:sample[key] for key in fields};data['title']=title
    identity=page.request.get(base+'/auth/me').json()
    response=page.request.post(base+'/api/v1/products',data=data,headers={'X-CSRF-Token':identity['csrfToken'],'Idempotency-Key':str(uuid.uuid4())})
    assert response.status==201,response.text()
    created=response.json();page.goto(base+'/#draft/'+created['id'])
    expect(page.get_by_role('heading',name=title,exact=True)).to_be_visible()
    expect(page.get_by_role('link',name='Käytä JSON-rajapintaa',exact=True)).to_have_count(0)
    expect(page.get_by_role('link',name='Pyydä SD-JWT VC lompakkoon',exact=True)).to_have_count(0)
    page.get_by_role('button',name='Muokkaa',exact=True).click()
    for prefix in ('JSON API 1','W3C VC 2','SD-JWT VC 3'):
        page.get_by_label(prefix+': saatavuus',exact=True).select_option('planned')
    page.get_by_label('JSON API 1: palveluosoite',exact=True).fill('https://provider.fi/company')
    page.get_by_label('JSON API 1: rajapintakuvauksen osoite',exact=True).fill('https://provider.fi/docs')
    for prefix,configuration in [('W3C VC 2','w3c'),('SD-JWT VC 3','sd-jwt')]:
        page.get_by_label(prefix+': myöntäjäpalvelun HTTPS-tunniste',exact=True).fill('https://issuer.fi/')
        page.get_by_label(prefix+': pysyvä myöntämisen aloituslinkki',exact=True).fill('https://issuer.fi/start?configuration='+configuration)
    page.get_by_role('button',name='Tallenna',exact=True).click()
    expect(page.get_by_text('Toimitustapojen metadata ja mappingit tarkistettu',exact=True)).to_be_visible(timeout=20000)
    # Private drafts never expose active service actions.
    expect(page.get_by_role('link',name='Käytä JSON-rajapintaa',exact=True)).to_have_count(0)
    page.get_by_role('button',name='Lähetä tarkastukseen',exact=True).click()
    expect(page.get_by_text('Tarkastuksessa',exact=True)).to_be_visible()
    logout(page);login(page,'yritys','demo-yritys');page.goto(base+'/#draft/'+created['id'])
    page.get_by_label('Tarkastuksen perustelu',exact=True).fill('Synteettiset kolme toimitustapaa, yhteinen profiili ja mappingit tarkastettu; ei palveluyhteyttä.')
    page.get_by_label('Olen tarkastanut lähdeilmoituksen, SHACL-profiilin ja sen riippuvuudet',exact=True).check()
    page.get_by_role('button',name='Hyväksy',exact=True).click();page.get_by_role('button',name='Julkaise',exact=True).click()
    expect(page.get_by_text('Julkaistu versio 1.0.0',exact=True)).to_be_visible()
    expect(page.get_by_role('link',name='Käytä JSON-rajapintaa',exact=True)).to_have_count(0)
    expect(page.get_by_role('link',name='Pyydä W3C VC lompakkoon',exact=True)).to_have_count(0)
    expect(page.get_by_role('link',name='Pyydä SD-JWT VC lompakkoon',exact=True)).to_have_count(0)
    logout(page);page.goto(base+'/#'+created['id'])
    expect(page.get_by_role('heading',name='W3C VC · Ensisijainen',exact=True)).to_be_visible()
    snapshot=httpx.get(base+'/api/v1/products/'+created['id']).json()
    assert len({binding['profileSnapshotSha256'] for binding in snapshot['distributionBindings']})==1
    assert all(item['availability']=='planned' for item in snapshot['distributions'])
    # Render-only fixture: no fake active services are persisted in the user's catalogue.
    import copy
    active=copy.deepcopy(snapshot)
    for item in active['distributions']:item['availability']='sandbox'
    page.route(base+'/api/v1/products/'+created['id'],lambda route:route.fulfill(json=active))
    page.reload()
    for label,href in [('Käytä JSON-rajapintaa','https://provider.fi/company'),('Tutustu rajapintakuvaukseen','https://provider.fi/docs'),('Pyydä W3C VC lompakkoon','https://issuer.fi/start?configuration=w3c'),('Pyydä SD-JWT VC lompakkoon','https://issuer.fi/start?configuration=sd-jwt')]:
        expect(page.get_by_role('link',name=label,exact=True)).to_have_attribute('href',href)
    # No external link is followed. Real active metadata gating is covered against catalog_test.


def test_synthetic_json_rdf_preview_same_different_and_invalid_without_saving(page):
    base=os.environ['BROWSER_BASE_URL']
    login(page)
    page.goto(base+'/#draft/00000000-0000-4000-8000-000000000004')
    lab=page.get_by_role('region',name='JSON–RDF-muunnoskokeilu',exact=True)
    expect(lab).to_be_visible()
    before=page.request.get(base+'/api/v1/products/00000000-0000-4000-8000-000000000004/draft').json()
    lab.get_by_role('button',name='Täytä synteettinen kolmen muodon esimerkki',exact=True).click()
    confirmation=lab.get_by_label('Vahvistan muunnoksen esimerkit synteettisiksi ilman henkilötietoja tai salaisuuksia',exact=True)
    action=lab.get_by_role('button',name='Muunna ja vertaa RDF-sisältöä',exact=True)
    expect(action).to_be_disabled();confirmation.check();action.click()
    expect(lab.get_by_text('Sama RDF-sisältö',exact=True)).to_be_visible()
    expect(lab.get_by_text('JSON Schema/OpenAPI: Läpäissyt · Semanttinen SHACL: Läpäissyt',exact=True)).to_be_visible()
    field=lab.get_by_label('SD-JWT VC — synteettinen JSON-sisältö',exact=True)
    field.fill('{"company_name":"Toinen synteettinen arvo"}')
    expect(lab.get_by_text('Sama RDF-sisältö',exact=True)).to_have_count(0)
    expect(action).to_be_disabled();confirmation.check();action.click()
    expect(lab.get_by_text('RDF-sisällöt eroavat',exact=True)).to_be_visible()
    field.fill('{"company_name":null}');confirmation.check();action.click()
    expect(lab.get_by_text('JSON_DATATYPE',exact=True)).to_be_visible()
    expect(lab.get_by_text('Vertailua ei tehty',exact=True)).to_be_visible()
    assert page.request.get(base+'/api/v1/products/00000000-0000-4000-8000-000000000004/draft').json()==before
    page.reload();expect(lab).to_be_visible()
    expect(field).to_have_value('')
    logout(page)
    assert page.request.post(base+'/api/v1/drafts/'+before['draftId']+'/conversion-preview',
        data={'examples':[]}).status in (401,422)


def test_version_lifecycle_deprecate_withdraw_and_block_service_actions(page):
    import copy
    base=os.environ['BROWSER_BASE_URL'];title='Elinkaaritesti '+uuid.uuid4().hex
    login(page)
    sample=page.request.get(base+'/api/v1/products/00000000-0000-4000-8000-000000000004/draft').json()
    fields=('title','description','providerOrganizationId','theme','source','purpose','limitations','accessConditions','availability','synthetic','profileSnapshotId','issuance','syntheticExample','derivedExamples','distributions','primaryDistributionId')
    data={key:sample[key] for key in fields};data['title']=title
    identity=page.request.get(base+'/auth/me').json()
    response=page.request.post(base+'/api/v1/products',data=data,headers={'X-CSRF-Token':identity['csrfToken'],'Idempotency-Key':str(uuid.uuid4())})
    assert response.status==201,response.text()
    created=response.json();page.goto(base+'/#draft/'+created['id'])
    page.get_by_role('button',name='Lähetä tarkastukseen',exact=True).click()
    expect(page.get_by_text('Tarkastuksessa',exact=True)).to_be_visible()
    logout(page);login(page,'yritys','demo-yritys');page.goto(base+'/#draft/'+created['id'])
    page.get_by_label('Tarkastuksen perustelu',exact=True).fill('Synteettinen elinkaaritesti; profiili ja toimitustapojen mappingit tarkastettu.')
    page.get_by_label('Olen tarkastanut lähdeilmoituksen, SHACL-profiilin ja sen riippuvuudet',exact=True).check()
    page.get_by_role('button',name='Hyväksy',exact=True).click();page.get_by_role('button',name='Julkaise',exact=True).click()
    expect(page.get_by_text('Julkaistu versio 1.0.0',exact=True)).to_be_visible()
    product_id=created['id'];snapshot=page.request.get(base+f'/api/v1/products/{product_id}/versions/1.0.0').json()
    # Exercise active rendering without storing or calling nonexistent source/issuer services.
    active=copy.deepcopy(snapshot)
    for item in active['distributions']:
        item['availability']='sandbox'
        if item['type']=='jsonApi':item['api']['serviceUrl']='https://provider.fi/company';item['api']['descriptionUrl']='https://provider.fi/docs'
        else:item['credential']['initiationUrl']='https://issuer.fi/start?configuration='+item['type']
    def render(route):route.fulfill(json=active)
    page.route(base+'/api/v1/products/'+product_id,render)
    page.route(base+f'/api/v1/products/{product_id}/versions/1.0.0',render)
    page.reload()
    for label in ('Käytä JSON-rajapintaa','Pyydä W3C VC lompakkoon','Pyydä SD-JWT VC lompakkoon'):
        expect(page.get_by_role('link',name=label,exact=True)).to_be_visible()
    lifecycle_path=base+f'/api/v1/products/{product_id}/versions/1.0.0/lifecycle'
    def unavailable_parallel(route):route.fulfill(status=503,json={'detail':'Synthetic unavailable lifecycle'})
    page.route(lifecycle_path,unavailable_parallel);page.reload()
    expect(page.get_by_text('Ajantasainen elinkaaritieto puuttuu. Palvelutoiminnot ovat estettyinä; lataa sivu uudelleen.',exact=True)).to_be_visible()
    for label in ('Käytä JSON-rajapintaa','Pyydä W3C VC lompakkoon','Pyydä SD-JWT VC lompakkoon'):
        expect(page.get_by_role('link',name=label,exact=True)).to_have_count(0)
    page.unroute(lifecycle_path,unavailable_parallel);page.reload()
    expect(page.get_by_role('link',name='Käytä JSON-rajapintaa',exact=True)).to_be_visible()
    panel=page.get_by_role('region',name='Version elinkaari',exact=True)
    panel.get_by_label('Julkinen elinkaariperustelu — ei henkilötietoja tai salaisuuksia',exact=True).fill('Synteettinen versio on poistumassa käytöstä; korvaavaa versiota ei vielä ole.')
    panel.get_by_role('button',name='Tallenna elinkaarimuutos',exact=True).click()
    expect(panel.get_by_text('Versio on poistumassa käytöstä.',exact=True)).to_be_visible()
    expect(page.get_by_role('link',name='Käytä JSON-rajapintaa',exact=True)).to_be_visible()
    panel.get_by_label('Uusi elinkaaritila',exact=True).select_option('withdrawn')
    panel.get_by_label('Julkinen elinkaariperustelu — ei henkilötietoja tai salaisuuksia',exact=True).fill('Synteettinen versio vedetään pois käytöstä testin päätösvaiheessa.')
    page.once('dialog',lambda dialog:dialog.accept())
    panel.get_by_role('button',name='Tallenna elinkaarimuutos',exact=True).click()
    expect(panel.get_by_text('Versio on poistettu käytöstä.',exact=True)).to_be_visible()
    for label in ('Käytä JSON-rajapintaa','Tutustu rajapintakuvaukseen','Pyydä W3C VC lompakkoon','Pyydä SD-JWT VC lompakkoon'):
        expect(page.get_by_role('link',name=label,exact=True)).to_have_count(0)
    page.goto(base+'/#'+product_id+'@1.0.0');expect(panel.get_by_text('Versio on poistettu käytöstä.',exact=True)).to_be_visible()
    expect(page.get_by_role('link',name='Käytä JSON-rajapintaa',exact=True)).to_have_count(0)
    page.unroute(base+'/api/v1/products/'+product_id,render);page.unroute(base+f'/api/v1/products/{product_id}/versions/1.0.0',render)
    logout(page);page.goto(base+'/#');page.get_by_label('Hakusana',exact=True).fill(title);page.get_by_role('button',name='Hae',exact=True).click()
    expect(page.get_by_role('link',name=title,exact=True)).to_have_count(0)
    page.get_by_label('Version elinkaaritila',exact=True).select_option('withdrawn');page.get_by_role('button',name='Hae',exact=True).click()
    page.get_by_role('link',name=title,exact=True).click()
    expect(panel.get_by_text('Versio on poistettu käytöstä.',exact=True)).to_be_visible()
    expect(panel.get_by_role('button',name='Tallenna elinkaarimuutos',exact=True)).to_have_count(0)
    original=page.request.get(base+f'/api/v1/products/{product_id}/versions/1.0.0')
    assert original.json()==snapshot and original.headers['x-product-lifecycle-status']=='withdrawn'
    assert page.request.get(base+f'/api/v1/products/{product_id}/export?version=1.0.0').json()==snapshot


def test_missing_or_withdrawn_lifecycle_blocks_legacy_service_link(page):
    import copy
    base=os.environ['BROWSER_BASE_URL'];page.goto(base)
    items=page.request.get(base+'/api/v1/products?lifecycleStatus=all').json()['items']
    assert items,'Earlier publication browser tests should supply a synthetic snapshot'
    source=copy.deepcopy(items[0]);source.pop('lifecycle',None)
    source['distributions']=None;source['issuance']={'serviceAvailability':'sandbox','issuanceInitiationUrl':'https://issuer.fi/start','primaryDelivery':'w3cVc'}
    product=source['id'];version=source['version']
    page.route(base+'/api/v1/products/'+product,lambda route:route.fulfill(json=source))
    def unavailable(route):route.fulfill(status=503,json={'detail':'Synthetic unavailable lifecycle'})
    page.route(base+f'/api/v1/products/{product}/versions/{version}/lifecycle',unavailable)
    page.goto(base+'/#'+product)
    expect(page.get_by_text('Ajantasainen elinkaaritieto puuttuu. Palvelutoiminnot ovat estettyinä; lataa sivu uudelleen.',exact=True)).to_be_visible()
    expect(page.get_by_role('link',name='Pyydä todistus lompakkoon',exact=True)).to_have_count(0)
    page.unroute(base+f'/api/v1/products/{product}/versions/{version}/lifecycle',unavailable)
    # A real withdrawn state must block the legacy action too; no state is persisted by route fixtures.
    life=page.request.get(base+f'/api/v1/products/{product}/versions/{version}/lifecycle').json()
    page.route(base+f'/api/v1/products/{product}/versions/{version}/lifecycle',lambda route:route.fulfill(json=life|{'status':'withdrawn','reason':'Synteettinen renderöintitesti','events':[]}))
    page.reload()
    expect(page.get_by_text('Versio on poistettu käytöstä.',exact=True)).to_be_visible()
    expect(page.get_by_role('link',name='Pyydä todistus lompakkoon',exact=True)).to_have_count(0)
