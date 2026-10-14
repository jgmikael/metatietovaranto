"""Real browser smoke tests against a separately started demo (opt-in)."""
import os
import shutil
import uuid
import pytest
import httpx
from playwright.sync_api import sync_playwright, expect

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
    page.get_by_role('button',name='Tallenna',exact=True).click()
    expect(page.get_by_role('heading',name=title,exact=True)).to_be_visible()
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
