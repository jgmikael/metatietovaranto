import json,hashlib
from pathlib import Path
from rdflib import Graph,RDF,SH
from apps.api.technical_packages import proposal
from tests_static.test_browser_generation import worker,prepared,source
ROOT=Path(__file__).resolve().parents[1]
FIX=ROOT/'fixtures/tietomallit/ryhti-akr-1.0.5'
def corrected_source():
    raw=(FIX/'original.ttl').read_bytes();r=json.loads((FIX/'repair-report.json').read_text());pins=json.loads((FIX/'provenance.json').read_text())
    assert hashlib.sha256((FIX/'repair-report.json').read_bytes()).hexdigest()==pins['reportSha256']
    assert len(raw)==pins['bytes'] and len(r['changes'])==pins['approvedTermCorrections']==62
    assert hashlib.sha256(raw).hexdigest()==pins['sha256']==r['originalSources'][0]['sha256']
    assert raw.decode()==r['originalSources'][0]['content']
    b=bytearray(raw.decode().encode('utf-16-le'))
    for c in sorted(r['changes'],key=lambda c:c['start'],reverse=True):
        assert b[c['start']*2:c['end']*2].decode('utf-16-le')==c['before'];b[c['start']*2:c['end']*2]=c['after'].encode('utf-16-le')
    text=bytes(b).decode('utf-16-le');assert hashlib.sha256(text.encode()).hexdigest()==pins['correctedSha256']
    return text

def test_ryhti_before_after_matrix(page,static_site):
    text=corrected_source();g=Graph().parse(data=text,format='turtle');profile=prepared(page,static_site,[source(text)])
    manifest={'sourceArtifacts':[source(text)|{'serialization':'turtle'}],'dependencies':[],'derivedArtifacts':[]}
    rows=[]
    for root in sorted(g.subjects(RDF.type,SH.NodeShape),key=str):
        choices={'rootShapeUri':str(root),'names':[]}
        choices['languageRepresentation']='valueLanguage-v1'
        backend=proposal(manifest,choices);browser=worker(page,static_site,{'action':'proposal','profile':profile,'settings':choices})
        rows.append({'root':str(root),'server':{'status':backend['status'],'codes':[f['ruleId'] for f in backend['results']]},'browser':{'status':'proposed' if browser['ok'] else 'invalid','codes':[f['ruleId'] for f in (browser.get('findings') or [browser.get('error')]) if f]}})
    assert len(rows)==15
    expected=json.loads((ROOT/'docs/ryhti-generation-results.json').read_text())
    assert rows==expected
    baseline=json.loads((FIX/'before.json').read_text())
    assert [r['root'] for r in rows]==[r['root'] for r in baseline]
    for old,new in zip(baseline,rows):
        if old['server']['status']=='proposed':assert new['server']['status']==new['browser']['status']=='proposed'
