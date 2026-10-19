"""Offline Pages builder and real generated-artifact integrity. No API-test conftest/DB."""
import hashlib,json,socket
from pathlib import Path
from urllib.parse import urlsplit
import pytest
import sqlalchemy
from apps.semantic_reader import resolve_claim,verify_bundle,integrity
from scripts.build_pages_data import build,DEFAULT_BASE


def test_offline_deterministic_fixture_build_preserves_semantics_and_integrity(tmp_path,monkeypatch):
    def forbidden(*args,**kwargs):raise AssertionError('Static data build attempted a network/database connection')
    monkeypatch.setattr(socket.socket,'connect',forbidden)
    monkeypatch.setattr(sqlalchemy,'create_engine',forbidden)
    one=build(tmp_path/'one');two=build(tmp_path/'two')
    assert one==two
    data=json.loads(one['demo/catalog.json']);assert len(data['items'])==4
    assert all(item['synthetic'] for item in data['items'])
    product=data['items'][-1];package=product['technicalPackage']
    assert {item['type'] for item in product['distributions']}=={'jsonApi','w3cVc','sdJwtVc'}
    assert all(item['availability']=='planned' for item in product['distributions'])
    assert package['validation']['jsonLdGraphComparison']=='isomorphic' and package['validation']['shacl']=='conforms'
    docs={record['url']:record['content'].encode() for record in package['artifacts'].values()}
    raw=docs[package['artifacts']['sd-jwt-type-metadata.json']['url']]
    assert verify_bundle(raw,integrity(raw),docs.__getitem__)
    claim=resolve_claim(raw,integrity(raw),['companyName'],docs.__getitem__)
    assert claim['propertyIri']=='https://example.org/metatietovaranto/demo/companyName'
    assert claim['sourceProfile']['snapshotUrl'].startswith(DEFAULT_BASE+'/demo/profiles/')
    snapshot_path=urlsplit(claim['sourceProfile']['snapshotUrl']).path.removeprefix('/metatietovaranto/')
    snapshot=json.loads(one[snapshot_path])
    assert snapshot['sha256']==claim['sourceProfile']['snapshotSha256']
    assert snapshot['manifest']['sourceArtifacts'][0]['content']==Path('fixtures/semantic-profile-demo.ttl').read_text()
    inventory=json.loads(one['demo/inventory.json'])
    for path,digest in inventory['files'].items():assert hashlib.sha256(one[path]).hexdigest()==digest
    for path in data['resources'].values():assert path in one
    # No database rows, identities, audit subjects or application-session fixtures are exported.
    forbidden_keys={'draftId','contributors','csrfToken','username','password','access_token','refresh_token','auditEvents','memberships'}
    def inspect(value):
        if isinstance(value,dict):
            assert not forbidden_keys.intersection(value)
            for child in value.values():inspect(child)
        elif isinstance(value,list):
            for child in value:inspect(child)
    for path,content in one.items():
        if path.endswith(('.json','.jsonld')):inspect(json.loads(content))
    # Only fixture-owned files may be copied by Vite's publicDir.
    (tmp_path/'one'/'unexpected.txt').write_text('unapproved')
    with pytest.raises(ValueError,match='Unexpected file'):build(tmp_path/'one')
    (tmp_path/'one'/'unexpected.txt').unlink()
    (tmp_path/'one'/'linked-data').symlink_to(tmp_path/'two',target_is_directory=True)
    with pytest.raises(ValueError,match='Symlink'):build(tmp_path/'one')


def test_configured_publication_origin_is_applied_before_hashing(tmp_path):
    first=build(tmp_path/'first');other_base='https://demo.example.org/metatietovaranto'
    second=build(tmp_path/'second',other_base)
    p1=json.loads(first['demo/catalog.json'])['items'][-1]['technicalPackage']
    p2=json.loads(second['demo/catalog.json'])['items'][-1]['technicalPackage']
    assert p1['packageId']!=p2['packageId']
    for record in p2['artifacts'].values():
        assert record['url'].startswith(other_base+'/id/technical-packages/')
        assert hashlib.sha256(record['content'].encode()).hexdigest()==record['sha256']
    assert 'https://example.org/metatietovaranto/demo/companyName' in p2['artifacts']['semantic-mapping.json']['content']
    for invalid in ['http://localhost:8000/metatietovaranto','https://demo.example.org/other','https://demo.example.org/metatietovaranto?token=secret']:
        with pytest.raises(ValueError):build(tmp_path/'invalid',invalid)
