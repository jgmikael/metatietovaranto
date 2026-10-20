"""Bundled guide, field coverage and preserved local workflow, static GETs only."""
from pathlib import Path
from playwright.sync_api import expect
from tests_static.test_experiment import start,edit,saved,stored,KEY,TITLE
from tests_static.test_browser_generation import attach_demo
ROOT=Path(__file__).resolve().parents[1]


def panel(page,label):
    button=page.get_by_role('button',name='Ohje: '+label,exact=True)
    return button,page.locator('[id="'+button.get_attribute('aria-controls')+'"]')


def assert_coverage(page):
    assert page.locator('[data-help-missing]').count()==0
    fields=page.locator('input:visible,textarea:visible,select:visible')
    assert fields.count()>0
    for field in fields.all():
        assert field.get_attribute('aria-describedby'),field.evaluate('(e)=>e.outerHTML')
        for id in field.get_attribute('aria-describedby').split():
            description=page.locator('[id="'+id+'"]')
            assert description.count()==1,id
            assert description.inner_text().strip()
        assert field.evaluate('(e)=>e.labels.length>0')


def test_search_help_keyboard_without_submit_and_return_focus(page,static_site):
    page.goto(static_site)
    search=page.get_by_label('Hakusana',exact=True);search.fill('ei löydy ennen hakua')
    button,description=panel(page,'Hakusana')
    expect(description).to_be_hidden();button.focus();button.press('Enter')
    expect(button).to_have_attribute('aria-expanded','true');expect(description).to_be_visible()
    expect(page.get_by_role('status')).to_have_text('4 tietotuotetta')
    button.press('Space');expect(description).to_be_hidden();expect(button).to_be_focused()
    assert_coverage(page)
    button.click();link=description.get_by_role('link',name='Lue lisää');link.click()
    expect(page).to_have_url(static_site+'#ohje/julkinen-esittely')
    expect(page.locator('#ohje-julkinen-esittely')).to_be_focused()
    page.get_by_role('button',name='Palaa edelliseen näkymään').click()
    expect(search).to_have_value('ei löydy ennen hakua');expect(link).to_be_focused()
    expect(page.get_by_role('status')).to_have_text('4 tietotuotetta')


def test_guide_direct_reload_sections_rendering_and_download(page,static_site,tmp_path):
    page.goto(static_site+'#ohje/ensikokeilu');page.reload()
    expect(page.locator('#ohje-ensikokeilu')).to_be_focused()
    expect(page.get_by_role('navigation',name='Käyttöohjeen sisällysluettelo')).to_be_visible()
    assert page.locator('.help-view table').count()>10
    assert page.locator('.help-view ol li').count()>0
    expect(page.locator('.help-view pre code').filter(has_text='Synteettinen Esimerkki Oy')).to_be_visible()
    toc=page.get_by_role('navigation',name='Käyttöohjeen sisällysluettelo')
    links=toc.get_by_role('link').all()
    for link in links:
        href=link.get_attribute('href');assert href.startswith('#ohje/')
        assert page.locator('#ohje-'+href.split('/')[1]).count()==1
    toc.get_by_role('link',name='10. SD-JWT VC -kuvauksen omat kentät',exact=True).click()
    expect(page.locator('#ohje-sd-jwt-vc')).to_be_focused()
    with page.expect_download() as event:page.get_by_role('link',name='Lataa käyttöohje Markdownina').click()
    target=tmp_path/'guide.md';event.value.save_as(target)
    assert target.read_text()==(ROOT/'docs/pages-kayttoohje.md').read_text()
    # Bundled source and report links resolve beneath the Pages prefix without API.
    for name in ['semantic-profile-demo.ttl','Juurikohtainen tukiraportti']:
        href=page.get_by_role('link',name=name,exact=True).get_attribute('href')
        assert href.startswith('/metatietovaranto/') or href.startswith('data:')
        # Vite may inline a small fixture as a data URL; it is a download, no runtime service.
        if href.startswith('/'):assert page.request.get(static_site.rstrip('/')+href.removeprefix('/metatietovaranto')).ok
    page.goto(static_site+'#ohje/ei-ole');expect(page.get_by_role('alert')).to_contain_text('Ohjeosiota ei löydy')


def test_metadata_organizations_and_all_distribution_fields_have_help(page,static_site):
    start(page,static_site);edit(page)
    assert_coverage(page)
    # Cover hidden conditional fields: object mapping and wallet configurations.
    for kind in ['W3C VC 2','SD-JWT VC 3']:
        page.get_by_text(kind+': lompakkoprofiilit',exact=True).click()
        page.get_by_role('button',name='Lisää lompakkoprofiili: '+kind,exact=True).click()
    page.get_by_label('JSON API 1, kenttä 1: arvon rakenne',exact=True).select_option('object')
    assert_coverage(page)
    for label in ['Kuvaus','Käyttötarkoitus','Rajaukset — mitä tuote ei todista','Käyttöehdot','W3C VC 2: myöntäjäorganisaatio','SD-JWT VC 3: vct']:
        button,description=panel(page,label);button.click();expect(description).to_be_visible();button.click()
    page.get_by_role('button',name='Omat organisaatiot',exact=True).click()
    page.get_by_role('button',name='Lisää paikallinen organisaatio',exact=True).click()
    page.get_by_role('button',name='Lisää organisaatiotunniste',exact=True).click()
    assert_coverage(page)
    page.get_by_text('JSON-tuonti ja alkuperäisten esimerkkien palautus',exact=True).click()
    assert_coverage(page)


def test_guide_keeps_unsaved_file_inspection_and_local_changes(page,static_site):
    start(page,static_site);edit(page)
    page.get_by_label('Nimi',exact=True).fill('Ohjevierailu säilyttää tämän')
    source=page.get_by_label('SHACL Turtle -tiedosto',exact=True)
    source.set_input_files(ROOT/'fixtures/semantic-profile-demo.ttl')
    expect(page.get_by_text('Turtle jäsennetty:',exact=False)).to_be_visible()
    page.get_by_label('Lähdeprofiilin versio (jos tiedossa)',exact=True).fill('oma-synteettinen-versio')
    saved(page);before=page.evaluate('(key)=>localStorage.getItem(key)',KEY)
    assert_coverage(page)
    button,description=panel(page,'Lähdeprofiilin versio (jos tiedossa)');button.click()
    more=description.get_by_role('link',name='Lue lisää');more.click()
    expect(page).to_have_url(static_site+'#ohje/shacl-tuonti')
    page.go_back()
    expect(more).to_be_focused()
    expect(page.get_by_label('Nimi',exact=True)).to_have_value('Ohjevierailu säilyttää tämän')
    expect(page.get_by_label('Lähdeprofiilin versio (jos tiedossa)',exact=True)).to_have_value('oma-synteettinen-versio')
    expect(page.get_by_text('Turtle jäsennetty:',exact=False)).to_be_visible()
    assert page.evaluate('(key)=>localStorage.getItem(key)',KEY)==before
    page.get_by_role('button',name='Liitä tuotu profiili tuotteeseen',exact=True).click()
    expect(page.get_by_text('Profiili liitetty paikalliseen tuotteeseen. Valitse juurimuoto.',exact=True)).to_be_visible()


def test_generation_proposal_checkboxes_and_scroll_survive_help(page,static_site):
    attach_demo(page,static_site)
    page.get_by_role('button',name='Näytä tuodun profiilin luokkamuodot',exact=True).click()
    assert_coverage(page)
    saved(page);before=stored(page)
    button,description=panel(page,'Vahvistan JSON-esimerkin synteettiseksi');button.click()
    more=description.get_by_role('link',name='Lue lisää');more.scroll_into_view_if_needed()
    scroll=page.evaluate('window.scrollY');more.click()
    page.get_by_role('button',name='Palaa edelliseen näkymään').click()
    expect(more).to_be_focused()
    expect(page.get_by_label('Vahvistan JSON-esimerkin synteettiseksi',exact=True)).to_be_checked()
    assert abs(page.evaluate('window.scrollY')-scroll)<3
    expect(page.get_by_role('button',name='Muodosta paikallinen tekninen paketti',exact=True)).to_be_enabled()
    assert stored(page)==before
    page.get_by_role('button',name='Muodosta paikallinen tekninen paketti',exact=True).click()
    expect(page.get_by_role('heading',name='Paikallinen kokeilupaketti – ei julkaistu',exact=True)).to_be_visible()


def test_public_product_stays_open_and_mobile_touch_help(page,static_site):
    mobile=page
    mobile.set_viewport_size({'width':390,'height':844})
    mobile.goto(static_site)
    mobile.get_by_role('link',name=TITLE,exact=True).click()
    expect(mobile.get_by_role('heading',name=TITLE,exact=True)).to_be_visible()
    mobile.get_by_role('link',name='Käyttöohje',exact=True).click()
    mobile.get_by_role('button',name='Palaa edelliseen näkymään').click()
    expect(mobile.get_by_role('heading',name=TITLE,exact=True)).to_be_visible()
    mobile.get_by_role('link',name='← Takaisin hakuun',exact=True).click()
    button,description=panel(mobile,'Hakusana')
    button.scroll_into_view_if_needed();box=button.bounding_box()
    session=page.context.new_cdp_session(page)
    session.send('Emulation.setTouchEmulationEnabled',{'enabled':True})
    session.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':box['x']+box['width']/2,'y':box['y']+box['height']/2}]})
    session.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
    expect(description).to_be_visible();session.detach()
    assert mobile.evaluate('document.documentElement.scrollWidth<=window.innerWidth')
