"""Same compiled App on a plain HTTP server, with all backend/network requests rejected."""
import functools,hashlib,http.server,json,os,shutil,threading,urllib.request
from pathlib import Path
from urllib.parse import urlsplit
import pytest
from playwright.sync_api import sync_playwright,expect

ROOT=Path(__file__).resolve().parents[1]
DEMO='00000000-0000-4000-8000-000000000004'


def test_list_search_filters_no_login_and_no_backend(page,static_site):
    page.goto(static_site)
    expect(page.get_by_text('Julkinen esittelydemo – synteettinen aineisto',exact=True)).to_be_visible()
    expect(page.get_by_role('status')).to_have_text('4 tietotuotetta')
    expect(page.get_by_role('link',name='Kirjaudu sisään',exact=True)).to_have_count(0)
    expect(page.get_by_role('button',name='Lisää tietotuote',exact=True)).to_have_count(0)
    page.get_by_label('Hakusana',exact=True).fill('verovelka');page.get_by_role('button',name='Hae',exact=True).click()
    expect(page.get_by_role('status')).to_have_text('1 tietotuotetta')
    page.get_by_label('Hakusana',exact=True).fill('');page.get_by_label('Teema',exact=True).fill('Yritykset');page.get_by_role('button',name='Hae',exact=True).click()
    expect(page.get_by_role('status')).to_have_text('2 tietotuotetta')
    page.get_by_label('Tarjoaja',exact=True).fill('Demo-veroviranomainen');page.get_by_role('button',name='Hae',exact=True).click()
    expect(page.get_by_role('status')).to_have_text('1 tietotuotetta')
    page.set_viewport_size({'width':390,'height':844})
    assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth')


def test_direct_product_reload_artifact_download_and_semantic_inspection(page,static_site,tmp_path):
    page.goto(static_site+'#'+DEMO+'@1.0.0')
    expect(page.get_by_role('heading',name='Yrityssisältö — JSON API, W3C VC ja SD-JWT VC (synteettinen demo)',exact=True)).to_be_visible()
    page.reload();expect(page.get_by_text('Staattinen esimerkkiversio 1.0.0',exact=True)).to_be_visible()
    for label in ['JSON API','W3C VC · Ensisijainen','SD-JWT VC']:expect(page.get_by_role('heading',name=label,exact=True)).to_be_visible()
    expect(page.get_by_role('link',name='Pyydä W3C VC lompakkoon',exact=True)).to_have_count(0)
    expect(page.get_by_role('link',name='Pyydä SD-JWT VC lompakkoon',exact=True)).to_have_count(0)
    expect(page.get_by_text('Palvelu on suunnitteilla.',exact=True)).to_have_count(3)
    page.get_by_text('Väitepolku: ["companyName"]',exact=True).click()
    expect(page.get_by_role('region',name='Attribuuttien semanttiset viittaukset')).to_contain_text('https://example.org/metatietovaranto/demo/companyName')
    page.get_by_text('Tarkastele: content.schema.json',exact=True).click()
    expect(page.locator('details').filter(has=page.get_by_text('Tarkastele: content.schema.json',exact=True))).to_contain_text('x-term')
    with page.expect_download() as download:
        page.get_by_role('link',name='context.jsonld',exact=True).click()
    event=download.value;event.save_as(tmp_path/'context.jsonld')
    data=json.loads(urllib.request.urlopen(static_site+'demo/catalog.json').read())
    product=next(item for item in data['items'] if item['id']==DEMO)
    assert hashlib.sha256((tmp_path/'context.jsonld').read_bytes()).hexdigest()==product['technicalPackage']['artifacts']['context.jsonld']['sha256']
    for anchor in page.locator('a[href]').all():
        target=anchor.get_attribute('href')
        if target.startswith('/metatietovaranto/'):
            response=page.request.get(urlsplit(static_site).scheme+'://'+urlsplit(static_site).netloc+target)
            assert response.status==200,target
    page.get_by_role('link',name='Demo-veroviranomainen',exact=True).click()
    expect(page.get_by_role('heading',name='Demo-veroviranomainen',exact=True)).to_be_visible()
    expect(page.get_by_text('Organisaatiotunnisteet',exact=True)).to_be_visible()
    page.reload();expect(page.get_by_role('heading',name='Demo-veroviranomainen',exact=True)).to_be_visible()


def test_profiles_source_and_machine_readable_artifacts(static_site,page):
    page.goto(static_site+'#profiles');expect(page.get_by_role('heading',name='Sisältöprofiilit',exact=True)).to_be_visible()
    expect(page.get_by_text('https://example.org/metatietovaranto/demo/profile',exact=True)).to_be_visible()
    page.get_by_text('Tarkastele alkuperäistä SHACLia',exact=True).click()
    expect(page.locator('pre')).to_contain_text('sh:PropertyShape')
    data=json.loads(urllib.request.urlopen(static_site+'demo/catalog.json').read())
    for path in data['resources'].values():
        with urllib.request.urlopen(static_site+path) as response:assert response.status==200
    package=data['items'][-1]['technicalPackage']
    documents={}
    for name,record in package['artifacts'].items():
        path=urlsplit(record['url']).path.removeprefix('/metatietovaranto/')
        with urllib.request.urlopen(static_site+path) as response:raw=response.read()
        assert hashlib.sha256(raw).hexdigest()==record['sha256'];documents[record['url']]=raw
    from apps.semantic_reader import verify_bundle,integrity,resolve_claim
    metadata=package['artifacts']['sd-jwt-type-metadata.json'];raw=documents[metadata['url']]
    assert verify_bundle(raw,integrity(raw),documents.__getitem__)
    assert resolve_claim(raw,integrity(raw),['companyName'],documents.__getitem__)['propertyIri'].endswith('/companyName')
    source=data['profiles'][0]['manifest']['sourceArtifacts'][0]
    path=data['resources'][f'/api/v1/profile-snapshots/{data["profiles"][0]["id"]}/artifacts/{source["id"]}']
    assert urllib.request.urlopen(static_site+path).read().decode()==source['content']


def test_build_contains_only_allowlisted_data_and_no_local_credentials():
    directory=ROOT/'apps/web/dist-pages'
    catalogue=json.loads((directory/'demo/catalog.json').read_text())
    inventory=json.loads((directory/'demo/inventory.json').read_text())
    allowed=set(inventory['files'])|{'demo/inventory.json','index.html'}
    for path in directory.rglob('*'):
        if not path.is_file():continue
        relative=path.relative_to(directory).as_posix()
        assert relative in allowed or relative.startswith('assets/')
        raw=path.read_bytes()
        for forbidden in [b'demo-vero',b'demo-yritys',b'demo-lukija',b'localhost:8000',b'localhost:5432']:
            assert forbidden not in raw,(relative,forbidden)
    assert catalogue['synthetic'] is True


def test_private_draft_hash_cannot_enable_maintenance_or_backend_access(page,static_site):
    page.goto(static_site+'#draft/'+DEMO)
    expect(page.get_by_role('alert')).to_contain_text('Sivua ei ole julkisessa esittelyaineistossa')
    for label in ['Tallenna','Hyväksy','Julkaise','Muokkaa','Kirjaudu sisään']:
        expect(page.get_by_role('button',name=label,exact=True)).to_have_count(0)
