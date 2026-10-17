"""Separate append-only version lifecycle; immutable snapshot bytes stay authoritative."""
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.contracts import Contract
from apps.api.models import LifecycleEvent, LifecycleOutboxEvent, ProductVersion, IdempotentOperation


class LifecycleCommand(Contract):
    version: str = Field(pattern=r'^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$', max_length=50)
    status: Literal['deprecated', 'withdrawn']
    reason: str = Field(min_length=10, max_length=2000)
    replacementVersion: str | None = Field(default=None, pattern=r'^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$', max_length=50)


def find_version(session, product_id, version):
    row = session.scalar(select(ProductVersion).where(ProductVersion.product_id == product_id, ProductVersion.version == version))
    if row is None:raise HTTPException(404, 'Julkaisuversiota ei löydy')
    return row


def version_uri(base, row):
    # Earliest 2C snapshots predate versionUri. Derive a read-only identity without backfilling bytes.
    return row.content.get('versionUri') or (row.content.get('uri') or f'{base}/id/products/{row.product_id}').rstrip('/')+'/versions/'+row.version


def lifecycle_uri(base, row):
    return f'{base}/api/v1/products/{row.product_id}/versions/{row.version}/lifecycle'


def lifecycle_state(session, row, base):
    events = session.scalars(select(LifecycleEvent).where(LifecycleEvent.version_id == row.id).order_by(LifecycleEvent.sequence)).all()
    replacements = {event.replacement_version_id for event in events if event.replacement_version_id}
    targets = {target.id:target for target in session.scalars(select(ProductVersion).where(ProductVersion.id.in_(replacements))).all()} if replacements else {}
    history = []
    for event in events:
        replacement = targets.get(event.replacement_version_id)
        history.append({'id':str(event.id), 'revision':event.sequence, 'previousStatus':event.previous_status,
            'status':event.status, 'reason':event.reason, 'createdAt':event.created_at.isoformat(),
            'organizationId':str(event.organization_id), 'replacementVersion':replacement.version if replacement else None,
            'replacementVersionUri':version_uri(base,replacement) if replacement else None})
    revision = events[-1].sequence if events else 0
    return {'uri':lifecycle_uri(base,row), 'productId':str(row.product_id), 'version':row.version,
        'versionUri':version_uri(base,row), 'sequence':row.sequence, 'versionContentHash':row.checksum,
        'status':history[-1]['status'] if history else 'published', 'revision':revision,
        'etag':f'"lifecycle:{row.id}:{revision}"',
        'updatedAt':history[-1]['createdAt'] if history else row.created_at.isoformat(),
        'reason':history[-1]['reason'] if history else None,
        'replacementVersion':history[-1]['replacementVersion'] if history else None,
        'replacementVersionUri':history[-1]['replacementVersionUri'] if history else None, 'events':history}


def snapshot_headers(session, row, base):
    state = lifecycle_state(session,row,base)
    return {'ETag':'"'+row.checksum+'"', 'X-Product-Lifecycle-Status':state['status'],
            'Link':f'<{state["uri"]}>; rel="describedby"; type="application/json"'}


def live_body(session, row, base):
    body = dict(row.content) | {'version':row.version, 'contentHash':row.checksum}
    state = lifecycle_state(session,row,base)
    if state['revision'] or 'lifecycle' in body:
        body['lifecycle'] = state
    return body


def build_lifecycle_router(engine, base):
    # Reuse the existing authority, serialization locks and idempotency contract.
    from apps.api.publication import get_owned, membership, idempotent, record, now
    router = APIRouter()

    @router.get('/api/v1/products/{product_id}/versions/{version}/lifecycle')
    def read(product_id:UUID, version:str, response:Response):
        with Session(engine) as session:
            state = lifecycle_state(session,find_version(session,product_id,version),base)
            response.headers['ETag'] = state['etag']
            return state

    @router.post('/api/v1/products/{product_id}/lifecycle-events', status_code=201)
    def change(product_id:UUID, data:LifecycleCommand, request:Request, response:Response):
        with Session(engine) as session:
            product, identity = get_owned(session,request,product_id,write=True)
            membership(session,identity,product.owner_organization_id,('publisher',))
            cached, operation = idempotent(session,request,identity,'lifecycle:'+str(product.id),
                data.model_dump() | {'etag':request.headers.get('if-match')})
            if cached:
                response.headers['ETag'] = cached['etag']
                return cached
            row = find_version(session,product.id,data.version)
            before = lifecycle_state(session,row,base)
            expected = request.headers.get('if-match')
            if expected is None:raise HTTPException(428,'If-Match puuttuu; lue version elinkaaritieto ensin')
            if expected != before['etag']:raise HTTPException(412,'Elinkaaritila on muuttunut. Lue ajantasainen elinkaaritieto.')
            if before['status'] == 'withdrawn' or before['status'] == data.status:
                raise HTTPException(409,'Tämä elinkaarisiirtymä ei ole sallittu; sisältö palautetaan uutena hyväksyttynä julkaisuna')
            replacement = None
            if data.replacementVersion:
                if data.status != 'deprecated':raise HTTPException(409,'Korvaava versio liitetään deprecated-tapahtumaan')
                replacement = find_version(session,product.id,data.replacementVersion)
                if replacement.sequence <= row.sequence or lifecycle_state(session,replacement,base)['status'] == 'withdrawn':
                    raise HTTPException(409,'Korvaavan version on oltava saman tuotteen myöhempi julkaisu, jota ei ole poistettu käytöstä')
            event = LifecycleEvent(version_id=row.id, sequence=before['revision']+1, previous_status=before['status'],
                status=data.status, reason=data.reason, replacement_version_id=replacement.id if replacement else None,
                actor=identity.subject, organization_id=product.owner_organization_id, created_at=now())
            session.add(event);session.flush()
            after = lifecycle_state(session,row,base)
            session.add(LifecycleOutboxEvent(event_id=event.id, payload={'type':'product.lifecycleChanged',
                'eventId':str(event.id), 'productId':str(product.id), 'version':row.version,
                'versionContentHash':row.checksum, 'lifecycle':after}, created_at=now()))
            record(session,product,identity,'version.'+data.status,row.checksum,row.checksum,data.reason,
                {'version':row.version, 'eventId':str(event.id), 'previousStatus':before['status'],
                 'status':data.status, 'revision':after['revision'], 'replacementVersion':data.replacementVersion})
            session.add(IdempotentOperation(**operation,response=after));session.commit()
            response.headers['ETag'] = after['etag']
            return after
    return router
