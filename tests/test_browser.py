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

def test_search_detail_edit_create_delete(page):
    base=os.environ['BROWSER_BASE_URL']
    title='Selaintesti '+uuid.uuid4().hex
    created_id=None
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
            httpx.delete(f'{base}/api/v1/products/{created_id}')

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
