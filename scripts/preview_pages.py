"""Serve a built Pages demo using only Python's standard static HTTP server."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--port',type=int,default=4173)
    args=parser.parse_args()
    build=Path(__file__).resolve().parents[1]/'apps/web/dist-pages'
    if not (build/'index.html').is_file():parser.error('Build the Pages demo first: bash scripts/build-pages.sh')
    with TemporaryDirectory(prefix='metatietovaranto-pages-') as directory:
        shutil.copytree(build,Path(directory)/'metatietovaranto')
        handler=partial(SimpleHTTPRequestHandler,directory=directory)
        with ThreadingHTTPServer(('127.0.0.1',args.port),handler) as server:
            print(f'Static Pages demo: http://127.0.0.1:{server.server_port}/metatietovaranto/',flush=True)
            try:server.serve_forever()
            except KeyboardInterrupt:pass

if __name__=='__main__':main()
