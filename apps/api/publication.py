"""Organization-scoped draft workflow and atomic, immutable publication."""
from datetime import datetime, timezone, timedelta
import re
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import Field
from sqlalchemy import select, func, text
from sqlalchemy.orm import Session

from apps.api.auth import current_session, require_session, require_editor
from apps.api.contracts import Contract, ProductWrite, Issuance
from apps.api.models import (Product, Organization, OrganizationMembership, Draft, ProfileSnapshot,
                            ProductVersion, Review, AuditEvent, IdempotentOperation, OutboxEvent)
from apps.api.profiles import checksum, can_read_snapshot, snapshot_summary
from apps.api.semantic_validation import validate_snapshot, current_report
from apps.api.derived_validation import validate_derived, derived_errors
from apps.api.distributions import normalize_distributions, validate_distributions, distribution_errors
from apps.api.conversion import ConversionRequest, conversion_preview


def now():return datetime.now(timezone.utc)


def etag(draft):return f'"{draft.revision}"'


def check_etag(request,draft):
    value=request.headers.get('if-match')
    if value is None:raise HTTPException(428,'If-Match puuttuu; lue nykyinen luonnos ensin')
    if value!=etag(draft):raise HTTPException(412,'Luonnosta on muutettu. Lue uusin versio ennen tallennusta.')


def membership(session,identity,org,roles=('editor','reader','reviewer','publisher')):
    member=session.get(OrganizationMembership,(identity.subject,org)) if identity else None
    if member is None or member.role not in roles:raise HTTPException(404,'Kuvausta ei löydy')
    return member


def get_owned(session,request,product_id,*,write=False):
    identity=require_session(request,session,csrf=write)
    product=session.scalar(select(Product).where(Product.id==product_id).with_for_update()) if write else session.get(Product,product_id)
    if product is None:raise HTTPException(404)
    membership(session,identity,product.owner_organization_id)
    return product,identity


def get_draft(session,product):
    draft=session.scalar(select(Draft).where(Draft.product_id==product.id).with_for_update().execution_options(populate_existing=True))
    if draft is None:raise HTTPException(404)
    return draft


def record(session,product,identity,action,before,after,reason='',details=None):
    session.add(AuditEvent(organization_id=product.owner_organization_id,product_id=product.id,
        actor=identity.subject if identity else 'migration',action=action,before_hash=before,after_hash=after,
        reason=reason,details=details or {},created_at=now()))


def initialize_drafts(session):
    for product in session.scalars(select(Product).outerjoin(Draft,Draft.product_id==Product.id).where(Draft.id==None)).all():
        body=dict(product.metadata_)|{'title':product.title,'description':product.description,'theme':product.theme,
            'provider':product.provider,'providerOrganizationId':str(product.provider_organization_id),
            'modifiedAt':product.modified_at.isoformat(),'profileSnapshotId':None,
            'issuance':Issuance().model_dump(mode='json')}
        session.add(Draft(product_id=product.id,content=body,revision=1,status='draft',checksum=checksum(body),
                          contributors=['legacy:unknown'],modified_at=product.modified_at))


def validation(session,draft):
    errors=[]
    snapshot=session.get(ProfileSnapshot,draft.profile_snapshot_id) if draft.profile_snapshot_id else None
    if snapshot is None:errors.append({'path':'profileSnapshotId','message':'Tietomallit-profiilin lukittu SHACL-snapshot puuttuu'})
    else:
        errors += [{'path':'profileSnapshotId','message':issue} for issue in snapshot.manifest['issues']]
        if not snapshot.manifest['shapesArtifactId']:errors.append({'path':'profileSnapshotId','message':'SHACL-graafi puuttuu'})
    if snapshot:
        report=draft.content.get('semanticValidation')
        if not current_report(report,snapshot,draft.content.get('syntheticExample')):
            errors.append({'path':'syntheticExample','message':'Esimerkki tai ajantasainen SHACL-raportti puuttuu. Tallenna luonnos tarkistaaksesi sisällön.'})
        elif report.get('status')!='conforms':
            errors += [{'path':item.get('path','/syntheticExample'),'message':item.get('message','SHACL-tarkistus epäonnistui'),
                        'ruleId':item.get('ruleId')} for item in report.get('results',[])]
            if not report.get('results'):errors.append({'path':'syntheticExample','message':'SHACL-tarkistus ei läpäissyt'})
    if snapshot:errors+=derived_errors(snapshot,draft.content)
    if draft.content.get('distributions') is not None:
        if snapshot:errors+=distribution_errors(snapshot,draft.content)
        return errors
    delivery=Issuance.model_validate(draft.content.get('issuance',{}))
    if delivery.legalCategory=='QEAA':
        errors.append({'path':'issuance.legalCategory','message':'Demo ei vahvista QEAA-asemaa; käytä unassessed-luokkaa'})
    if delivery.serviceAvailability in ('sandbox','production'):
        required={'issuanceInitiationUrl':delivery.issuanceInitiationUrl,'issuerOrganizationId':delivery.issuerOrganizationId,
            'operatorOrganizationId':delivery.operatorOrganizationId,'sourceProviderOrganizationId':delivery.sourceProviderOrganizationId,
            'credentialProfile.vcTypes':delivery.credentialProfile.vcTypes,'credentialProfile.contexts':delivery.credentialProfile.contexts,
            'credentialProfile.securityMechanism':delivery.credentialProfile.securityMechanism,
            'credentialProfile.fieldMappings':delivery.credentialProfile.fieldMappings,
            'subjectTypes':delivery.subjectTypes,'representationRequirements':delivery.representationRequirements,
            'validityPolicy':delivery.validityPolicy,'statusPolicy':delivery.statusPolicy,'support':delivery.support}
        if delivery.issuanceProtocol=='OpenID4VCI':
            required|={'credentialIssuer':delivery.credentialIssuer,'credentialConfigurationIds':delivery.credentialConfigurationIds}
        for key,value in required.items():
            if not value:errors.append({'path':'issuance.'+key,'message':'Käytettävän VC-palvelun pakollinen tieto puuttuu'})
        if 'https://www.w3.org/ns/credentials/v2' not in [str(uri) for uri in delivery.credentialProfile.contexts]:
            errors.append({'path':'issuance.credentialProfile.contexts','message':'W3C VCDM 2.0 -konteksti puuttuu'})
        if 'VerifiableCredential' not in delivery.credentialProfile.vcTypes:
            errors.append({'path':'issuance.credentialProfile.vcTypes','message':'W3C VC:n perustyyppi VerifiableCredential puuttuu'})
        if delivery.credentialIssuer and delivery.credentialIssuer.scheme != 'https':
            errors.append({'path':'issuance.credentialIssuer','message':'Myöntäjän tunnisteen on oltava HTTPS-osoite'})
        mapped=set(delivery.credentialProfile.fieldMappings)
        if snapshot:
            simple_paths={element['semanticUri'] for element in snapshot.manifest['elements'] if element['semanticUri']}
            if not simple_paths.issubset(mapped):errors.append({'path':'issuance.credentialProfile.fieldMappings','message':'Sisällön kenttäkartoitus on puutteellinen'})
    return errors


def draft_response(session,draft):
    snapshot=session.get(ProfileSnapshot,draft.profile_snapshot_id) if draft.profile_snapshot_id else None
    return dict(draft.content)|{'ownerOrganizationId':str(session.get(Product,draft.product_id).owner_organization_id),'id':str(draft.product_id),'draftId':str(draft.id),'revision':draft.revision,
        'status':draft.status,'etag':etag(draft),'contentHash':draft.checksum,
        'profileSnapshot':snapshot_summary(snapshot) if snapshot else None,'validationErrors':validation(session,draft)}


def write_content(session,request,product,draft,data,identity):
    require_editor(session,identity,product.owner_organization_id)
    require_editor(session,identity,data.providerOrganizationId)
    provider=session.get(Organization,data.providerOrganizationId)
    if provider is None:raise HTTPException(422,'Tarjoaja puuttuu')
    body=draft.content|data.model_dump(mode='json')
    snapshot=session.get(ProfileSnapshot,data.profileSnapshotId) if data.profileSnapshotId else None
    if data.profileSnapshotId and (snapshot is None or not can_read_snapshot(session,request,snapshot)):
        raise HTTPException(404,'Profiilisnapshotia ei löydy')
    if draft.content.get('distributions') is not None and data.distributions is None:
        raise HTTPException(422,'Säilytä tuotteen distributions-kuvaus; vanhaan issuance-malliin ei palata hiljaisesti')
    try:normalize_distributions(body,snapshot)
    except ValueError as error:raise HTTPException(422,str(error)) from None
    for item in body.get('distributions') or []:
        refs=[item[key] for key in ('providerOrganizationId','operatorOrganizationId','sourceProviderOrganizationId')]
        if item['type']!='jsonApi' and item['credential']['issuerOrganizationId']:refs.append(item['credential']['issuerOrganizationId'])
        if any(session.get(Organization,UUID(ref)) is None for ref in refs):raise HTTPException(422,'Toimitustavan organisaatioviite puuttuu')
    for key in ('issuerOrganizationId','operatorOrganizationId','sourceProviderOrganizationId'):
        organization_id=getattr(data.issuance,key)
        if organization_id and session.get(Organization,organization_id) is None:raise HTTPException(422,f'{key}: organisaatiota ei löydy')
    body|={'provider':provider.legal_name,'modifiedAt':now().isoformat(),
           'dataElements':snapshot.manifest['elements'] if snapshot else draft.content.get('dataElements',[])}
    body['semanticValidation']=validate_snapshot(snapshot,body.get('syntheticExample')) if snapshot else None
    body['derivedValidation']=validate_derived(snapshot,body.get('derivedExamples',[])) if snapshot else None
    body['distributionValidation']=validate_distributions(snapshot,body.get('distributions')) if snapshot else None
    draft.content=body;draft.profile_snapshot_id=data.profileSnapshotId;draft.revision+=1
    draft.checksum=checksum(body);draft.status='draft';draft.approved_review_id=None
    draft.contributors=list(dict.fromkeys(draft.contributors+[identity.subject]));draft.modified_at=now()


def idempotent(session,request,identity,scope,body):
    key=request.headers.get('idempotency-key','')
    if not re.fullmatch(r'[A-Za-z0-9_.:-]{1,128}',key):raise HTTPException(428,'Idempotency-Key puuttuu tai on virheellinen')
    session.execute(text('SELECT pg_advisory_xact_lock(hashtextextended(:scope,0))'),{'scope':identity.subject+scope+key})
    item=session.get(IdempotentOperation,(identity.subject,scope,key))
    request_hash=checksum(body)
    if item and item.expires_at<now():session.delete(item);session.flush();item=None
    if item:
        if item.request_hash!=request_hash:raise HTTPException(409,'Idempotency-Key on jo käytetty eri sisällölle')
        return item.response,None
    return None,dict(subject=identity.subject,operation=scope,key=key,request_hash=request_hash,expires_at=now()+timedelta(hours=24))


class Decision(Contract):
    decision:str=Field(pattern='^(approved|changesRequested)$')
    reason:str=Field(min_length=5,max_length=2000)
    sourceReviewed:bool=False


class Publish(Contract):
    version:str=Field(pattern=r'^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$',max_length=50)


def build_publication_router(engine,base_url,jsonld):
    router=APIRouter()
    def version_body(version):return dict(version.content)|{'version':version.version,'contentHash':version.checksum}
    def latest(session,product_id):
        version=session.scalar(select(ProductVersion).where(ProductVersion.product_id==product_id).order_by(ProductVersion.sequence.desc()).limit(1))
        if version is None:raise HTTPException(404,'Tuotteella ei ole julkista versiota')
        return version
    def latest_rows(session):
        current=select(ProductVersion.product_id,func.max(ProductVersion.sequence).label('sequence')).group_by(ProductVersion.product_id).subquery()
        return session.scalars(select(ProductVersion).join(current, (ProductVersion.product_id==current.c.product_id)&(ProductVersion.sequence==current.c.sequence)).order_by(ProductVersion.product_id)).all()
    @router.get('/api/v1/my/products')
    def mine(request:Request):
        with Session(engine) as session:
            identity=require_session(request,session,csrf=False)
            products=session.scalars(select(Product).join(OrganizationMembership,
                OrganizationMembership.organization_id==Product.owner_organization_id)
                .where(OrganizationMembership.subject==identity.subject)).all()
            return {'items':[draft_response(session,get_draft(session,product)) for product in products]}
    @router.get('/api/v1/products')
    def search(q:str=Query('',max_length=200),theme:str=Query('',max_length=100),provider:str=Query('',max_length=200),
               limit:int=Query(20,ge=1,le=100),offset:int=Query(0,ge=0)):
        with Session(engine) as session:
            bodies=[version_body(row) for row in latest_rows(session)]
            bodies=[body for body in bodies if (not q.strip() or q.strip().casefold() in ' '.join(str(body[key]) for key in ('title','description','provider')).casefold())
                    and (not theme or body['theme']==theme) and (not provider or body['provider']==provider)]
            bodies.sort(key=lambda body:(body['title'],body['id']))
            return {'items':bodies[offset:offset+limit],'total':len(bodies),'offset':offset,'limit':limit}
    @router.get('/api/v1/products/{product_id}')
    def detail(product_id:UUID):
        with Session(engine) as session:return version_body(latest(session,product_id))
    @router.get('/api/v1/products/{product_id}/versions')
    def versions(product_id:UUID):
        with Session(engine) as session:
            return {'items':[{'version':row.version,'sha256':row.checksum,'publishedAt':row.created_at.isoformat()}
                for row in session.scalars(select(ProductVersion).where(ProductVersion.product_id==product_id).order_by(ProductVersion.sequence.desc())).all()]}
    @router.get('/api/v1/products/{product_id}/versions/{version}')
    def version(product_id:UUID,version:str):
        with Session(engine) as session:
            row=session.scalar(select(ProductVersion).where(ProductVersion.product_id==product_id,ProductVersion.version==version))
            if row is None:raise HTTPException(404)
            return JSONResponse(version_body(row),headers={'ETag':'"'+row.checksum+'"'})
    @router.get('/api/v1/products/{product_id}/export')
    def export(product_id:UUID,format:str=Query('json',pattern='^(json|jsonld)$'),version:str|None=None):
        with Session(engine) as session:
            row=(session.scalar(select(ProductVersion).where(ProductVersion.product_id==product_id,ProductVersion.version==version))
                 if version else latest(session,product_id))
            if row is None:raise HTTPException(404)
            body=version_body(row)
            return JSONResponse(jsonld(body) if format=='jsonld' else body,
                media_type='application/ld+json' if format=='jsonld' else 'application/json')
    @router.get('/api/v1/catalog/export')
    def catalog(format:str=Query('json',pattern='^(json|jsonld)$')):
        with Session(engine) as session:
            bodies=[version_body(row) for row in latest_rows(session)]
            if format=='json':return {'demo':True,'items':bodies}
            return JSONResponse({'@context':{'dcat':'http://www.w3.org/ns/dcat#'},'@id':base_url+'/id/catalog',
                '@type':'dcat:Catalog','dcat:dataset':[jsonld(body) for body in bodies]},media_type='application/ld+json')
    @router.get('/id/products/{product_id}')
    def uri(product_id:UUID,request:Request):
        with Session(engine) as session:
            body=version_body(latest(session,product_id));accept=request.headers.get('accept','text/html');headers={'Vary':'Accept'}
            if 'application/ld+json' in accept:return JSONResponse(jsonld(body),media_type='application/ld+json',headers=headers)
            if 'application/json' in accept:return JSONResponse(body,headers=headers)
            return RedirectResponse(f'/#{product_id}',status_code=303,headers=headers)
    @router.get('/id/products/{product_id}/versions/{version}')
    def version_uri(product_id:UUID,version:str,request:Request):
        with Session(engine) as session:
            row=session.scalar(select(ProductVersion).where(ProductVersion.product_id==product_id,ProductVersion.version==version))
            if row is None:raise HTTPException(404)
            body=version_body(row);headers={'Vary':'Accept','ETag':'"'+row.checksum+'"'}
            accept=request.headers.get('accept','text/html')
            if 'application/ld+json' in accept:return JSONResponse(jsonld(body),media_type='application/ld+json',headers=headers)
            if 'application/json' in accept:return JSONResponse(body,headers=headers)
            return RedirectResponse(f'/#{product_id}@{version}',status_code=303,headers=headers)
    @router.post('/api/v1/products',status_code=201)
    def create(data:ProductWrite,request:Request,response:Response):
        with Session(engine) as session:
            identity=require_session(request,session);require_editor(session,identity,data.providerOrganizationId)
            cached,operation=idempotent(session,request,identity,'create',data.model_dump(mode='json'))
            if cached:
                response.headers['Location']='/api/v1/products/'+cached['id']+'/draft';response.headers['ETag']=cached['etag'];return cached
            provider=session.get(Organization,data.providerOrganizationId)
            product=Product(title=data.title,description=data.description,provider=provider.legal_name,
                provider_organization_id=provider.id,owner_organization_id=provider.id,theme=data.theme,
                metadata_={},modified_at=now())
            session.add(product);session.flush()
            draft=Draft(product_id=product.id,content={},revision=0,status='draft',checksum='',contributors=[],modified_at=now())
            write_content(session,request,product,draft,data,identity);session.add(draft);session.flush()
            record(session,product,identity,'draft.created',None,draft.checksum)
            result=draft_response(session,draft);session.add(IdempotentOperation(**operation,response=result));session.commit()
            response.headers['Location']='/api/v1/products/'+str(product.id)+'/draft';response.headers['ETag']=etag(draft)
            return result
    @router.get('/api/v1/products/{product_id}/draft')
    def private_draft(product_id:UUID,request:Request,response:Response):
        with Session(engine) as session:
            product,_=get_owned(session,request,product_id);draft=get_draft(session,product)
            response.headers['ETag']=etag(draft);return draft_response(session,draft)
    @router.get('/api/v1/drafts/{draft_id}')
    def draft_detail(draft_id:UUID,request:Request,response:Response):
        with Session(engine) as session:
            draft=session.get(Draft,draft_id)
            if draft is None:raise HTTPException(404)
            get_owned(session,request,draft.product_id);response.headers['ETag']=etag(draft)
            return draft_response(session,draft)
    def save(product_id,data,request,response):
        with Session(engine) as session:
            product,identity=get_owned(session,request,product_id,write=True);draft=get_draft(session,product);check_etag(request,draft)
            if draft.status=='published':raise HTTPException(409,'Luo julkaistun version rinnalle uusi työkopio')
            before=draft.checksum;write_content(session,request,product,draft,data,identity)
            record(session,product,identity,'draft.updated',before,draft.checksum,'Hyväksyntä mitätöity muokkauksen vuoksi')
            session.commit();response.headers['ETag']=etag(draft);return draft_response(session,draft)
    @router.put('/api/v1/products/{product_id}')
    def update(product_id:UUID,data:ProductWrite,request:Request,response:Response):return save(product_id,data,request,response)
    @router.put('/api/v1/drafts/{draft_id}')
    def draft_update(draft_id:UUID,data:ProductWrite,request:Request,response:Response):
        with Session(engine) as session:
            draft=session.get(Draft,draft_id)
            if draft is None:raise HTTPException(404)
            return save(draft.product_id,data,request,response)
    @router.post('/api/v1/drafts/{draft_id}/conversion-preview')
    def preview_conversion(draft_id:UUID,data:ConversionRequest,request:Request,response:Response):
        with Session(engine) as session:
            found=session.get(Draft,draft_id)
            if found is None:raise HTTPException(404)
            product,identity=get_owned(session,request,found.product_id,write=True)
            require_editor(session,identity,product.owner_organization_id)
            draft=get_draft(session,product);check_etag(request,draft)
            snapshot=session.get(ProfileSnapshot,draft.profile_snapshot_id) if draft.profile_snapshot_id else None
            if snapshot is None or not draft.content.get('distributions'):
                raise HTTPException(422,'Tallenna ensin yhteinen profiili ja toimitustapojen mappingit')
            result=conversion_preview(snapshot,draft.content['distributions'],data.model_dump(mode='json')['examples'])
            response.headers['ETag']=etag(draft)
            return result|{'draftRevision':draft.revision,'draftContentHash':draft.checksum}
    @router.post('/api/v1/products/{product_id}/drafts')
    def next_draft(product_id:UUID,request:Request,response:Response):
        with Session(engine) as session:
            product,identity=get_owned(session,request,product_id,write=True);require_editor(session,identity,product.owner_organization_id)
            draft=get_draft(session,product);check_etag(request,draft)
            if draft.status!='published':raise HTTPException(409,'Aktiivinen luonnos on jo olemassa')
            draft.status='draft';draft.revision+=1;draft.approved_review_id=None;draft.contributors=[identity.subject]
            record(session,product,identity,'draft.opened',draft.checksum,draft.checksum)
            session.commit();response.headers['ETag']=etag(draft);return draft_response(session,draft)
    @router.post('/api/v1/drafts/{draft_id}/submit')
    @router.post('/api/v1/drafts/{draft_id}/reviews')
    @router.post('/api/v1/drafts/{draft_id}/validate')
    def transition(draft_id:UUID,request:Request,response:Response,decision:Decision|None=None):
        command=request.url.path.rsplit('/',1)[-1]
        with Session(engine) as session:
            found=session.get(Draft,draft_id)
            if found is None:raise HTTPException(404)
            product,identity=get_owned(session,request,found.product_id,write=True);draft=get_draft(session,product)
            if command=='validate':
                snapshot=session.get(ProfileSnapshot,draft.profile_snapshot_id) if draft.profile_snapshot_id else None
                return {'errors':validation(session,draft),'contentHash':draft.checksum,
                    'semanticValidation':validate_snapshot(snapshot,draft.content.get('syntheticExample')) if snapshot else None,
                    'storedReport':draft.content.get('semanticValidation'),
                    'derivedValidation':validate_derived(snapshot,draft.content.get('derivedExamples',[])) if snapshot else None}
            check_etag(request,draft)
            if command=='submit':
                require_editor(session,identity,product.owner_organization_id)
                if draft.status!='draft':raise HTTPException(409,'Vain luonnoksen voi lähettää tarkastukseen')
                errors=validation(session,draft)
                if errors:raise HTTPException(422,errors)
                draft.status='inReview';record(session,product,identity,'draft.submitted',draft.checksum,draft.checksum)
            else:
                membership(session,identity,product.owner_organization_id,('reviewer','publisher'))
                if draft.status!='inReview' or decision is None:raise HTTPException(409,'Tarkastettava luonnos ja päätös tarvitaan')
                if identity.subject in draft.contributors:raise HTTPException(403,'Kirjoittaja ei voi hyväksyä omaa sisältöään')
                if decision.decision=='approved' and (not decision.sourceReviewed or validation(session,draft)):
                    raise HTTPException(422,'Tarkista lähdeilmoitus, profiiligraafi ja julkaisun estävät puutteet')
                review=Review(draft_id=draft.id,revision=draft.revision+1,checksum=draft.checksum,reviewer=identity.subject,
                    decision=decision.decision,reason=decision.reason,source_reviewed=decision.sourceReviewed,created_at=now())
                session.add(review);session.flush();draft.approved_review_id=review.id if decision.decision=='approved' else None
                draft.status='approved' if decision.decision=='approved' else 'draft'
                record(session,product,identity,'review.'+decision.decision,draft.checksum,draft.checksum,decision.reason,{'reviewId':str(review.id)})
            draft.revision+=1;session.commit();response.headers['ETag']=etag(draft);return draft_response(session,draft)
    @router.post('/api/v1/drafts/{draft_id}/publish')
    def publish(draft_id:UUID,data:Publish,request:Request):
        with Session(engine) as session:
            found=session.get(Draft,draft_id)
            if found is None:raise HTTPException(404)
            product,identity=get_owned(session,request,found.product_id,write=True)
            membership(session,identity,product.owner_organization_id,('publisher',))
            cached,operation=idempotent(session,request,identity,'publish:'+str(product.id),data.model_dump()|{'etag':request.headers.get('if-match')})
            if cached:return cached
            draft=get_draft(session,product);check_etag(request,draft)
            review=session.get(Review,draft.approved_review_id) if draft.approved_review_id else None
            if (draft.status!='approved' or review is None or review.checksum!=draft.checksum
                    or review.revision!=draft.revision or not review.source_reviewed or review.reviewer in draft.contributors):
                raise HTTPException(409,'Julkaisu vaatii voimassa olevan toisen käyttäjän hyväksynnän')
            errors=validation(session,draft)
            if errors:raise HTTPException(422,errors)
            previous=session.scalar(select(ProductVersion).where(ProductVersion.product_id==product.id).order_by(ProductVersion.sequence.desc()).limit(1))
            if previous and tuple(map(int,data.version.split('.')))<=tuple(map(int,previous.version.split('.'))):
                raise HTTPException(409,'Uuden semanttisen version on oltava aiempaa suurempi')
            if previous and draft.content.get('distributions') is not None:
                earlier={item['id']:item for item in previous.content.get('distributions') or []}
                for item in draft.content['distributions']:
                    old=earlier.get(item['id'])
                    if old:
                        before=tuple(map(int,old['mapping']['version'].split('.')));after=tuple(map(int,item['mapping']['version'].split('.')))
                        if after<before or (item['mapping']['entries']!=old['mapping']['entries'] and after<=before):
                            raise HTTPException(409,'Mappingin muutos tarvitsee aiempaa suuremman mapping-version; versionumeroa ei alenneta')
            snapshot=session.get(ProfileSnapshot,draft.profile_snapshot_id)
            body=dict(draft.content)|{'ownerOrganizationId':str(product.owner_organization_id),'id':str(product.id),'uri':base_url+'/id/products/'+str(product.id),'demo':True,
                'versionUri':base_url+'/id/products/'+str(product.id)+'/versions/'+data.version,
                'version':data.version,'issuanceBinding':{'productVersion':data.version,'profileSnapshotId':str(snapshot.id),'profileSnapshotSha256':snapshot.checksum},
                'semanticProfileSnapshot':snapshot_summary(snapshot),
                'semanticProfileAssessment':{'verificationStatus':'verified','method':'manualReview',
                    'sourceVerification':'declarationReviewed; not automatic platform attestation','reviewer':review.reviewer,
                    'reason':review.reason,'snapshotHash':snapshot.checksum},'publishedAt':now().isoformat()}
            if body.get('distributions') is not None:
                body['distributionBindings']=[{'distributionId':item['id'],'productVersion':data.version,
                    'profileSnapshotId':str(snapshot.id),'profileSnapshotSha256':snapshot.checksum,
                    'mappingVersion':item['mapping']['version']} for item in body['distributions']]
            version=ProductVersion(product_id=product.id,version=data.version,sequence=previous.sequence+1 if previous else 1,
                content=body,checksum=checksum(body),profile_snapshot_id=snapshot.id,review_id=review.id,
                publisher=identity.subject,created_at=now())
            session.add(version);session.flush()
            session.add(OutboxEvent(version_id=version.id,payload={'type':'product.published','productId':str(product.id),
                'version':data.version,'sha256':version.checksum},created_at=now()))
            record(session,product,identity,'product.published',previous.checksum if previous else None,version.checksum,
                review.reason,{'version':data.version,'reviewId':str(review.id),'profileHash':snapshot.checksum})
            draft.status='published';draft.revision+=1
            result=version_body(version);session.add(IdempotentOperation(**operation,response=result));session.commit();return result
    @router.delete('/api/v1/products/{product_id}',status_code=204)
    def delete(product_id:UUID,request:Request):
        with Session(engine) as session:
            product,identity=get_owned(session,request,product_id,write=True);require_editor(session,identity,product.owner_organization_id)
            draft=get_draft(session,product);check_etag(request,draft)
            if session.scalar(select(ProductVersion.id).where(ProductVersion.product_id==product.id).limit(1)):
                raise HTTPException(409,'Julkaistua historiaa ei poisteta')
            if session.scalar(select(Review.id).where(Review.draft_id==draft.id).limit(1)):
                raise HTTPException(409,'Tarkastushistoriaa ei poisteta')
            record(session,product,identity,'draft.deleted',draft.checksum,None,'Julkaisemattoman luonnoksen poisto')
            session.delete(draft);session.flush();session.delete(product);session.commit()
    @router.get('/api/v1/products/{product_id}/audit-events')
    def audit(product_id:UUID,request:Request):
        with Session(engine) as session:
            product,identity=get_owned(session,request,product_id)
            membership(session,identity,product.owner_organization_id,('editor','reviewer','publisher'))
            return {'items':[{'id':str(row.id),'actorId':row.actor,'action':row.action,'beforeHash':row.before_hash,
                'afterHash':row.after_hash,'reason':row.reason,'details':row.details,'createdAt':row.created_at.isoformat()}
                for row in session.scalars(select(AuditEvent).where(AuditEvent.product_id==product.id).order_by(AuditEvent.created_at)).all()]}
    return router
