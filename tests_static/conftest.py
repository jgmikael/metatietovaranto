"""Static HTTP and real browser fixtures, isolated from backend tests/conftest.py."""
import functools,http.server,os,shutil,threading
from pathlib import Path
from urllib.parse import urlsplit
import pytest
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]

@pytest.fixture(scope='module')
def static_site(tmp_path_factory):
    directory=tmp_path_factory.mktemp('pages-http')
    build=ROOT/'apps/web/dist-pages'
    assert (build/'index.html').exists(),'Run bash scripts/build-pages.sh first'
    shutil.copytree(build,directory/'metatietovaranto')
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(directory)))
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    base=f'http://127.0.0.1:{server.server_port}/metatietovaranto/'
    try:yield base
    finally:server.shutdown();thread.join();server.server_close()

@pytest.fixture
def page(static_site):
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=os.getenv('CHROMIUM_EXECUTABLE') or shutil.which('chromium'),headless=True)
        context=browser.new_context();errors=[];blocked=[]
        def monitor(page):
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.on('console',lambda msg:errors.append(msg.text) if msg.type=='error' else None)
        context.on('page',monitor);page=context.new_page()
        def guard(route):
            url=urlsplit(route.request.url)
            if route.request.url.startswith(static_site) and not any(part in url.path.split('/') for part in ['api','auth','identity']) and route.request.method=='GET':route.continue_()
            else:blocked.append(route.request.url);route.abort()
        context.route('**/*',guard)
        yield page
        browser.close()
        assert not blocked,'Attempted backend/external network calls: '+str(blocked)
        assert not errors

