#!/usr/bin/env python3
"""Read one public claim description. No SD-JWT, disclosure or signature processing."""
import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import build_opener,HTTPRedirectHandler
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from apps.semantic_reader import resolve_claim,MAX_BYTES

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):return None


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--type-metadata',required=True)
    parser.add_argument('--integrity',required=True,help='Trusted vct#integrity: sha256- plus standard base64')
    parser.add_argument('--claim-path',required=True,help='IETF JSON array, e.g. ["addresses",null,"city"]')
    args=parser.parse_args();origin=urlsplit(args.type_metadata)
    if origin.scheme!='https' and not (origin.scheme=='http' and origin.hostname in ('localhost','127.0.0.1')):
        parser.error('HTTPS required, except local demo')
    if origin.username or origin.password or origin.query or origin.fragment:parser.error('Credentials/query/fragment forbidden')
    # Explicit caller-selected origin only; never follow metadata to arbitrary hosts or redirects.
    opener=build_opener(NoRedirect());cache={}
    def load(url):
        parts=urlsplit(url)
        if (parts.scheme,parts.netloc)!=(origin.scheme,origin.netloc) or parts.username or parts.password or parts.query or parts.fragment:
            raise ValueError('Document outside explicitly selected origin')
        if url not in cache:
            with opener.open(url,timeout=10) as response:
                raw=response.read(MAX_BYTES+1)
                if len(raw)>MAX_BYTES:raise ValueError('Document too large')
                cache[url]=raw
        return cache[url]
    path=json.loads(args.claim_path)
    if not isinstance(path,list) or not path or any(not(isinstance(p,str) or p is None or type(p)is int and p>=0) for p in path):
        parser.error('Claim Path must be a nonempty array of strings, nulls or nonnegative integers')
    print(json.dumps(resolve_claim(load(args.type_metadata),args.integrity,path,load),ensure_ascii=False,indent=2))

if __name__=='__main__':main()
