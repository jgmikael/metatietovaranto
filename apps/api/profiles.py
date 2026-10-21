"""Bounded, non-executing Tietomallit export ingestion and immutable snapshots."""
import hashlib
import ipaddress
import json
import socket
from urllib.parse import urlsplit
from uuid import UUID, uuid4
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response
from pydantic import Field, HttpUrl, AfterValidator, StringConstraints
from typing import Annotated
from rdflib import Graph, Dataset, URIRef, RDF, OWL, SH, BNode, Literal
from rdflib.compare import to_isomorphic
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from apps.api.auth import current_session, require_session, require_editor
from apps.api.contracts import Contract
from apps.api.models import SemanticProfile, ProfileSnapshot, ProductVersion, OrganizationMembership

MAX_BYTES = 1_000_000
MAX_TRIPLES = 10000
FORMATS = {'turtle':'turtle','rdfxml':'xml','jsonld':'json-ld'}


def canonical(value):
    return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'))


def checksum(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def absolute_iri(value):
    if not urlsplit(value).scheme or any(char.isspace() for char in value):raise ValueError('Absoluuttinen IRI tarvitaan')
    return value

Iri=Annotated[str,Field(min_length=1,max_length=2048),AfterValidator(absolute_iri)]

class SemanticMapping(Contract):
    shapeUri: Iri
    semanticUri: Iri
    propertyName: Annotated[str, StringConstraints(strip_whitespace=False)] = Field(min_length=1,max_length=200)


class ArtifactInput(Contract):
    serialization: str = Field(pattern='^(turtle|rdfxml|jsonld|jsonSchema|openapi)$')
    content: Annotated[str, StringConstraints(strip_whitespace=False)] = Field(max_length=MAX_BYTES)
    sourceUrl: HttpUrl | None = None
    schemaPointer: str = Field(default='',max_length=1000)
    semanticMappings: list[SemanticMapping] = Field(default_factory=list,max_length=100)


class VocabularyReference(Contract):
    uri: Iri
    version: str | None = Field(default=None,max_length=200)
    location: str = Field(default='external',pattern='^(platform|external)$')


class DependencyInput(Contract):
    uri: Iri
    artifact: ArtifactInput


class ProfileInput(Contract):
    organizationId: UUID
    sourcePlatform: str = Field(default='TietomallitSuomiFi',pattern='^TietomallitSuomiFi$')
    profileUri: Iri | None = None
    sourcePageUrl: HttpUrl | None = None
    sourceVersion: str | None = Field(default=None,max_length=200)
    sourceStatus: str | None = Field(default=None,max_length=200)
    sourceDeclaration: str = Field(default='',max_length=2000)
    ingestionMethod: str = Field(pattern='^(upload|link)$')
    artifact: ArtifactInput | None = None
    sourceUrl: HttpUrl | None = None
    serialization: str = Field(default='turtle',pattern='^(turtle|rdfxml|jsonld)$')
    vocabularyReferences: list[VocabularyReference] = Field(default_factory=list,max_length=30)
    dependencyArtifacts: list[DependencyInput] = Field(default_factory=list,max_length=20)
    derivedArtifacts: list[ArtifactInput] = Field(default_factory=list,max_length=10)
    entryShapeUris: list[Iri] = Field(default_factory=list,max_length=30)


class LimitedGraph(Graph):
    def add(self,triple):
        if len(self)>=MAX_TRIPLES:
            raise ValueError('RDF-graafi ylittää 10000 kolmikon rajan')
        return super().add(triple)
    def addN(self,quads):
        for s,p,o,c in quads:self.add((s,p,o))
        return self


def reject_remote_contexts(value):
    if isinstance(value,dict):
        for key,item in value.items():
            if key=='@import' or (key=='@context' and isinstance(item,str)):
                raise ValueError('Ulkoinen JSON-LD-konteksti vaatii lukitun paikallisen esityksen; verkkonoutoa ei tehdä jäsentämisessä')
            if key=='@context' and isinstance(item,list) and any(isinstance(v,str) for v in item):
                raise ValueError('Ulkoista JSON-LD-kontekstia ei noudeta automaattisesti')
            reject_remote_contexts(item)
    elif isinstance(value,list):
        for item in value:reject_remote_contexts(item)


def parse_artifact(artifact, *, preserve_turtle_lexical=False):
    content=artifact.content
    if len(content.encode())>MAX_BYTES:raise ValueError('Tiedosto ylittää 1 MB rajan')
    raw_hash=hashlib.sha256(content.encode()).hexdigest()
    result={'id':str(uuid4()),'content':content,'serialization':artifact.serialization,'sha256':raw_hash,
            'sourceUrl':str(artifact.sourceUrl) if artifact.sourceUrl else None,
            'acquiredAt':datetime.now(timezone.utc).isoformat()}
    if artifact.serialization in ('jsonSchema','openapi'):
        doc=json.loads(content)
        if not isinstance(doc,dict):raise ValueError('Johdannaisen on oltava JSON-olio')
        result['schemaPointer']=artifact.schemaPointer
        result['semanticMappings']=[item.model_dump(mode='json') for item in artifact.semanticMappings]
        result['dialect']=doc.get('$schema') if artifact.serialization=='jsonSchema' else doc.get('openapi')
        result['mediaType']='application/schema+json' if artifact.serialization=='jsonSchema' else 'application/json'
        return None,result
    if '<!DOCTYPE' in content.upper() or '<!ENTITY' in content.upper():
        raise ValueError('XML DTD/ENTITY ei ole sallittu')
    if artifact.serialization=='jsonld':reject_remote_contexts(json.loads(content))
    graph=LimitedGraph()
    if artifact.serialization=='jsonld':
        dataset=Dataset()
        dataset.parse(data=content,format='json-ld',publicID='urn:metatietovaranto:unresolved-base:')
        for s,p,o,context in dataset.quads():
            if context!=dataset.default_graph.identifier:
                raise ValueError('Nimettyjä JSON-LD-graafeja ei tueta; toimita yksi täydellinen oletusgraafi')
            graph.add((s,p,o))
    elif artifact.serialization=='turtle' and preserve_turtle_lexical:
        # Per-parser sink: retain typed literal spelling for count checks, without
        # changing rdflib.NORMALIZE_LITERALS process-wide or altering snapshots.
        from io import StringIO
        from rdflib.plugins.parsers.notation3 import RDFSink, SinkParser
        class LexicalSink(RDFSink):
            def newLiteral(self, value, datatype, language):
                return Literal(value, datatype=datatype, lang=None if datatype else language, normalize=False)
        parser=SinkParser(LexicalSink(graph),baseURI='urn:metatietovaranto:unresolved-base:',turtle=True)
        parser.loadStream(StringIO(content))
        for prefix,namespace in parser._bindings.items():graph.bind(prefix,namespace)
    else:
        graph.parse(data=content,format=FORMATS[artifact.serialization],publicID='urn:metatietovaranto:unresolved-base:')
    result['mediaType']={'turtle':'text/turtle','rdfxml':'application/rdf+xml','jsonld':'application/ld+json'}[artifact.serialization]
    return graph,result


def fetch_artifact(url,serialization):
    parsed=urlsplit(str(url))
    if (parsed.scheme!='https' or parsed.hostname not in {'tietomallit.suomi.fi','iri.suomi.fi'}
            or parsed.username or parsed.password or parsed.port not in (None,443) or parsed.fragment):
        raise ValueError('Linkkituonti sallii vain tietomallit.suomi.fi- ja iri.suomi.fi-palvelujen HTTPS-exportit')
    addresses=socket.getaddrinfo(parsed.hostname,443,type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(addr[4][0]).is_global for addr in addresses):
        raise ValueError('Lähteen on osoitettava julkiseen verkkoon')
    with httpx.stream('GET',str(url),timeout=15,follow_redirects=False) as response:
        if response.status_code!=200:raise ValueError('Exportia ei saatu (uudelleenohjauksia ei seurata)')
        if 'text/html' in response.headers.get('content-type',''):raise ValueError('Sivulinkki ei ole koneluettava SHACL-export')
        content=b''
        for chunk in response.iter_bytes():
            content+=chunk
            if len(content)>MAX_BYTES:raise ValueError('Export ylittää 1 MB rajan')
    return ArtifactInput(serialization=serialization,content=content.decode('utf-8'),sourceUrl=url)


def snapshot_manifest(data):
    if data.ingestionMethod=='link':
        if not data.sourceUrl or data.artifact:raise ValueError('Linkkituonti tarvitsee vain koneluettavan sourceUrl-osoitteen')
        artifact=fetch_artifact(data.sourceUrl,data.serialization)
    else:
        if not data.artifact or data.sourceUrl:raise ValueError('Tiedostotuonti tarvitsee vain tiedoston sisällön; verkkolinkki ei ole pakollinen')
        artifact=data.artifact
    graph,source=parse_artifact(artifact)
    dependencies=[]; combined=Graph()
    if graph is not None:
        for triple in graph:combined.add(triple)
    for dependency in data.dependencyArtifacts:
        dep_graph,dep_source=parse_artifact(dependency.artifact)
        if dep_graph is None:raise ValueError('Riippuvuuden on oltava RDF-aineistoa')
        dependencies.append({'uri':str(dependency.uri),'artifact':dep_source,'status':'snapshot'})
        for triple in dep_graph:combined.add(triple)
    if len(combined)>MAX_TRIPLES:raise ValueError('Graafi ja riippuvuudet ylittävät kolmikkorajan')
    derived=[parse_artifact(item)[1] for item in data.derivedArtifacts]
    errors=[];elements=[];profile_uri=str(data.profileUri) if data.profileUri else None
    if graph is None:
        derived.insert(0,source);errors.append('Pelkkä JSON Schema/OpenAPI ei ole SHACL-soveltamisprofiili')
    else:
        shapes=set(graph.subjects(RDF.type,SH.NodeShape))
        if not shapes:errors.append('SHACL-luokkamuodot puuttuvat; OWL tai konteksti ei yksin riitä')
        if profile_uri is None:
            candidates=[str(node) for node in graph.subjects(RDF.type,OWL.Ontology) if isinstance(node,URIRef)]
            profile_uri=candidates[0] if len(candidates)==1 else None
        if profile_uri and not list(graph.triples((URIRef(profile_uri),None,None))):
            errors.append('Ilmoitettua profiili-IRIä ei löydy graafista')
        for uri in data.entryShapeUris:
            if URIRef(str(uri)) not in shapes:errors.append(f'Aloitusmuoto puuttuu: {uri}')
        selected=[URIRef(str(uri)) for uri in data.entryShapeUris] or sorted(shapes,key=str)
        for shape in selected:
            for prop in graph.objects(shape,SH.property):
                path=graph.value(prop,SH.path)
                target=graph.value(shape,SH.targetClass)
                elements.append({'name':str(graph.value(prop,SH.name) or path or prop),
                    'description':str(graph.value(prop,SH.description) or ''),
                    'shapeUri':str(shape),'propertyShapeUri':str(prop) if isinstance(prop,URIRef) else None,
                    'subjectClassUri':str(target) if target else None,
                    'semanticUri':str(path) if isinstance(path,URIRef) else None,
                    'complexPath':not isinstance(path,URIRef),'datatype':str(graph.value(prop,SH.datatype) or ''),
                    'minCount':str(graph.value(prop,SH.minCount) or ''),'maxCount':str(graph.value(prop,SH.maxCount) or ''),
                    'associationClassUri':str(graph.value(prop,SH['class']) or '')})
        supplied={item['uri'] for item in dependencies}
        missing={str(uri) for uri in combined.objects(None,OWL.imports)}-supplied
        defined=set(combined.subjects())
        missing|={str(uri) for uri in combined.objects(None,SH.node) if isinstance(uri,URIRef) and uri not in defined}
        for uri in sorted(missing):dependencies.append({'uri':uri,'status':'unresolved'})
        for subject in combined.all_nodes():
            if isinstance(subject,URIRef) and str(subject).startswith('urn:metatietovaranto:unresolved-base:'):
                errors.append('Suhteellinen IRI vaatii alkuperäisen absoluuttisen nimiavaruuden');break
    if not profile_uri:errors.append('Profiilin alkuperäinen IRI puuttuu')
    if not data.sourceDeclaration.strip():errors.append('Lähdeilmoitus puuttuu')
    if not data.vocabularyReferences:errors.append('OWL-sanastoviitteet puuttuvat')
    if any(item['status']=='unresolved' for item in dependencies):errors.append('Profiilin riippuvuuksia puuttuu')
    core_check=None
    if graph is not None:
        from apps.api.semantic_validation import profile_check, ENGINE, POLICY
        try:core_check=profile_check(combined)|{'engine':ENGINE,'policy':POLICY}
        except Exception:
            core_check={'conforms':False,'engine':ENGINE,'policy':POLICY,'results':[]}
        if not core_check['conforms']:errors.append('SHACL Core -rakennetarkistus ei läpäissyt; tarkista rajoitteet tai tukemattomat laajennukset')
    manifest={'sourcePlatform':'TietomallitSuomiFi','profileUri':profile_uri,
        'sourcePageUrl':str(data.sourcePageUrl) if data.sourcePageUrl else None,
        'sourceVersion':data.sourceVersion,'sourceStatus':data.sourceStatus,
        'ingestionMethod':data.ingestionMethod,'sourceDeclaration':data.sourceDeclaration,
        'sourceArtifacts':[source] if graph is not None else [],'shapesArtifactId':source['id'] if graph is not None and elements else None,
        'entryShapeUris':[str(uri) for uri in data.entryShapeUris],
        'vocabularyReferences':[ref.model_dump(mode='json') for ref in data.vocabularyReferences],
        'dependencies':dependencies,'derivedArtifacts':derived,'elements':elements,
        'verificationStatus':'needsAttention' if errors else 'pending','issues':errors,
        'sourceVerification':'declared; not independently verified','profileValidation':core_check,
        'graphHash':str(to_isomorphic(combined).internal_hash()) if graph is not None else None}
    if not elements:
        manifest['issues'].append('Profiilista ei löytynyt näytettäviä tietoelementtejä');manifest['verificationStatus']='needsAttention'
    return manifest


def _manifest_worker(data,pipe):
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_CPU,(5,5))
        resource.setrlimit(resource.RLIMIT_AS,(512*1024*1024,512*1024*1024))
        pipe.send((True,snapshot_manifest(ProfileInput.model_validate(data))))
    except Exception as error:
        pipe.send((False,type(error).__name__+': '+str(error)[:250]))
    finally:pipe.close()


def bounded_manifest(data):
    import multiprocessing
    value=data.model_dump(mode='json')
    if len(canonical(value).encode())>2*MAX_BYTES:raise ValueError('Profiilin ja riippuvuuksien yhteisraja on 2 MB')
    context=multiprocessing.get_context('spawn')
    reader,writer=context.Pipe(duplex=False)
    process=context.Process(target=_manifest_worker,args=(value,writer))
    process.start();writer.close()
    try:
        if not reader.poll(25):raise ValueError('Profiilin käsittelyn aikaraja ylittyi')
        try:success,result=reader.recv()
        except EOFError:raise ValueError('Profiilin käsittely ylitti resurssirajan') from None
        if not success:raise ValueError(result)
        return result
    finally:
        reader.close();process.join(.2)
        if process.is_alive():process.terminate();process.join(1)


def snapshot_summary(snapshot):
    return {'id':str(snapshot.id),'profileId':str(snapshot.profile_id),'sha256':snapshot.checksum,
            **{key:value for key,value in snapshot.manifest.items() if key not in ('sourceArtifacts','derivedArtifacts','dependencies')}}


def can_read_snapshot(session,request,snapshot):
    if session.scalar(select(ProductVersion.id).where(ProductVersion.profile_snapshot_id==snapshot.id).limit(1)):
        return True
    identity=current_session(request,session)
    return identity is not None and session.get(OrganizationMembership,(identity.subject,snapshot.owner_organization_id)) is not None


def build_profile_router(engine):
    router=APIRouter()
    @router.post('/api/v1/profile-snapshots',status_code=201)
    def register(data:ProfileInput,request:Request):
        with Session(engine) as session:
            identity=require_session(request,session)
            require_editor(session,identity,data.organizationId)
            try:manifest=bounded_manifest(data)
            except (ValueError,TypeError,KeyError,httpx.HTTPError,OSError,RecursionError) as error:
                raise HTTPException(422,'Profiilia ei voitu tuoda: '+str(error)[:250]) from None
            uri=manifest['profileUri']
            # Serialize registration of a shared profile identity without merging snapshots or owner rights.
            session.execute(text('SELECT pg_advisory_xact_lock(hashtextextended(:uri,0))'),{'uri':uri or str(uuid4())})
            profile=session.scalar(select(SemanticProfile).where(SemanticProfile.profile_uri==uri)) if uri else None
            if profile is None:
                profile=SemanticProfile(profile_uri=uri);session.add(profile);session.flush()
            snapshot=ProfileSnapshot(profile_id=profile.id,owner_organization_id=data.organizationId,
                manifest=manifest,checksum=checksum(manifest),graph_hash=manifest['graphHash'],created_at=datetime.now(timezone.utc))
            session.add(snapshot);session.commit()
            return snapshot_summary(snapshot)
    @router.get('/api/v1/profile-snapshots')
    def listing(request:Request):
        with Session(engine) as session:
            return {'items':[snapshot_summary(snapshot) for snapshot in session.scalars(select(ProfileSnapshot)).all()
                             if can_read_snapshot(session,request,snapshot)]}
    @router.get('/api/v1/profile-snapshots/{snapshot_id}')
    def detail(snapshot_id:UUID,request:Request):
        with Session(engine) as session:
            snapshot=session.get(ProfileSnapshot,snapshot_id)
            if snapshot is None or not can_read_snapshot(session,request,snapshot):raise HTTPException(404)
            return snapshot_summary(snapshot)|{'manifest':snapshot.manifest}
    @router.get('/api/v1/profile-snapshots/{snapshot_id}/artifacts/{artifact_id}')
    def artifact(snapshot_id:UUID,artifact_id:UUID,request:Request):
        with Session(engine) as session:
            snapshot=session.get(ProfileSnapshot,snapshot_id)
            if snapshot is None or not can_read_snapshot(session,request,snapshot):raise HTTPException(404)
            items=snapshot.manifest['sourceArtifacts']+snapshot.manifest['derivedArtifacts']
            items += [dep['artifact'] for dep in snapshot.manifest['dependencies'] if 'artifact' in dep]
            source=next((source for source in items if source['id']==str(artifact_id)),None)
            if source is None:raise HTTPException(404)
            return Response(source['content'],media_type=source['mediaType'],headers={'ETag':'"'+source['sha256']+'"','X-Content-Type-Options':'nosniff','Content-Disposition':'attachment; filename=profile-'+str(artifact_id)+'.'+source['serialization']})
    return router
