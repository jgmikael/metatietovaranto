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
    return page.request.delete(f'{base}/api/v1/products/{product_id}',
                              headers={'X-CSRF-Token':identity.get('csrfToken','')})


def test_search_detail_edit_create_delete(page):
    base=os.environ['BROWSER_BASE_URL']
    title='Selaintesti '+uuid.uuid4().hex
    created_id=None
    login(page)
    try:
        page.goto(base)
        expect(page.get_by_role('heading',name='Löydä tietotuote')).to_be_visible()
        page.get_by_label('Hakusana').fill('verovelka')
        page.get_by_role('button',name='Hae',exact=True).click()
        expect(page.get_by_role('status')).to_have_text('1 tietotuotetta')
        page.get_by_role('link',name='Verovelkatieto — synteettinen demo').click()
        expect(page.get_by_role('heading',name='Tietoelementit',exact=True)).to_be_visible()
        assert page.get_by_role('link',name='JSON-LD',exact=True).get_attribute('href').endswith('format=jsonld')
        page.get_by_role('link',name='← Takaisin hakuun').click()
        page.get_by_role('button',name='Lisää tietotuote',exact=True).click()
        for label,value in [('Nimi',title),('Kuvaus','<script>window.injected=true</script>'),('Teema','Testit'),('Synteettinen lähde','Synteettinen fixture'),('Käyttötarkoitus','Selaimen tallennustesti'),('Rajaukset — mitä tuote ei todista','Ei aitoja tietoja'),('Elementin nimi','test'),('Elementin kuvaus','Synteettinen elementti')]:
            page.get_by_label(label,exact=True).fill(value)
        page.get_by_label('Tarjoaja',exact=True).select_option(index=1)
        page.get_by_role('button',name='Tallenna',exact=True).click()
        expect(page.get_by_role('heading',name=title,exact=True)).to_be_visible()
        created_id=page.url.split('#')[1]
        assert page.evaluate('window.injected') is None
        page.reload()
        expect(page.get_by_role('heading',name=title,exact=True)).to_be_visible()
        page.get_by_role('button',name='Muokkaa',exact=True).click()
        page.get_by_label('Nimi',exact=True).fill(title+' muokattu')
        page.get_by_role('button',name='Tallenna',exact=True).click()
        expect(page.get_by_role('heading',name=title+' muokattu',exact=True)).to_be_visible()
        page.once('dialog',lambda dialog:dialog.accept())
        page.get_by_role('button',name='Poista tietotuote',exact=True).click()
        expect(page.get_by_role('heading',name='Löydä tietotuote')).to_be_visible()
        assert httpx.get(f'{base}/api/v1/products/{created_id}').status_code==404
    finally:
        if created_id:
            delete_test_product(page,created_id)

def test_mobile_search(page):
    page.set_viewport_size({'width':390,'height':844})
    page.goto(os.environ['BROWSER_BASE_URL'])
    expect(page.get_by_role('heading',name='Löydä tietotuote')).to_be_visible()
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')


def test_organization_navigation_and_provider_link(page):
    page.goto(os.environ['BROWSER_BASE_URL'])
    page.get_by_role('link',name='Organisaatiot',exact=True).click()
    expect(page.get_by_role('heading',name='Organisaatiot',exact=True)).to_be_visible()
    page.get_by_role('link',name='Demo-veroviranomainen',exact=True).click()
    expect(page.get_by_role('heading',name='Demo-veroviranomainen',exact=True)).to_be_visible()
    expect(page.get_by_text('Organisaatiotunnisteet',exact=True)).to_be_visible()
    page.reload()
    expect(page.get_by_role('heading',name='Demo-veroviranomainen',exact=True)).to_be_visible()
    page.get_by_role('link',name='← Takaisin hakuun').click()
    page.get_by_role('link',name='Verovelkatieto — synteettinen demo',exact=True).click()
    page.get_by_role('link',name='Demo-veroviranomainen',exact=True).click()
    expect(page.get_by_role('heading',name='Demo-veroviranomainen',exact=True)).to_be_visible()


def test_anonymous_reader_and_logout(page):
    base=os.environ['BROWSER_BASE_URL']
    page.goto(base)
    expect(page.get_by_role('link',name='Kirjaudu sisään',exact=True)).to_be_visible()
    expect(page.get_by_role('button',name='Lisää tietotuote',exact=True)).to_have_count(0)
    page.get_by_role('link',name='Verovelkatieto — synteettinen demo',exact=True).click()
    expect(page.get_by_role('button',name='Muokkaa',exact=True)).to_have_count(0)
    login(page,'lukija','demo-lukija')
    expect(page.get_by_role('button',name='Lisää tietotuote',exact=True)).to_have_count(0)
    page.get_by_role('link',name='Verovelkatieto — synteettinen demo',exact=True).click()
    expect(page.get_by_role('button',name='Muokkaa',exact=True)).to_have_count(0)
    page.get_by_role('button',name='Kirjaudu ulos',exact=True).click()
    page.locator('#kc-logout').click()
    expect(page.get_by_role('link',name='Kirjaudu sisään',exact=True)).to_be_visible()
    page.reload()
    expect(page.get_by_role('link',name='Kirjaudu sisään',exact=True)).to_be_visible()
    login(page,'vero','demo-vero')
    expect(page.get_by_role('button',name='Lisää tietotuote',exact=True)).to_be_visible()


def test_second_organization_editor_is_isolated(page):
    login(page,'yritys','demo-yritys')
    page.get_by_role('link',name='Verovelkatieto — synteettinen demo',exact=True).click()
    expect(page.get_by_role('button',name='Muokkaa',exact=True)).to_have_count(0)
    page.get_by_role('link',name='← Takaisin hakuun').click()
    page.get_by_role('link',name='Yrityksen perustiedot — synteettinen demo',exact=True).click()
    page.get_by_role('button',name='Muokkaa',exact=True).click()
    expect(page.get_by_label('Tarjoaja',exact=True)).to_have_value('fde32818-c368-5a6c-9804-a5ea7a9dcc98')
    expect(page.get_by_label('Tarjoaja',exact=True).locator('option')).to_have_count(2)


def test_expired_ui_session_returns_to_login(page):
    base=os.environ['BROWSER_BASE_URL']
    login(page)
    page.get_by_role('link',name='Verovelkatieto — synteettinen demo',exact=True).click()
    page.get_by_role('button',name='Muokkaa',exact=True).click()
    identity=page.request.get(base+'/auth/me').json()
    response=page.request.post(base+'/auth/logout',headers={'X-CSRF-Token':identity['csrfToken']})
    assert response.status==204
    page.get_by_role('button',name='Tallenna',exact=True).click()
    expect(page.get_by_role('link',name='Kirjaudu sisään',exact=True)).to_be_visible()
    expect(page.get_by_role('button',name='Tallenna',exact=True)).to_have_count(0)
