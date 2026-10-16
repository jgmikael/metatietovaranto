"""Typed delivery metadata. No source API, credential issuance or cryptography."""
from datetime import datetime
from typing import Annotated, Literal, Union
from urllib.parse import urlsplit
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, AfterValidator, model_validator, field_validator
from apps.api.metadata_urls import initiation_url

class Metadata(BaseModel):
    model_config=ConfigDict(extra='forbid',str_strip_whitespace=True)


def absolute_iri(value):
    if not urlsplit(value).scheme or any(c.isspace() for c in value):raise ValueError('Absoluuttinen IRI tarvitaan')
    return value
Iri=Annotated[str,Field(min_length=1,max_length=2048),AfterValidator(absolute_iri)]


def field_path(value):
    import re
    if not value.startswith('/') or re.search(r'~(?![01])',value):raise ValueError('Kenttäpolun on oltava JSON Pointer -malli; * tarkoittaa taulukon alkiota')
    return value
Path=Annotated[str,Field(min_length=1,max_length=1000),AfterValidator(field_path)]
Semver=Annotated[str,Field(pattern=r'^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$',max_length=50)]
ServiceUrl=Annotated[str,Field(max_length=2048),AfterValidator(initiation_url)]

class WalletCompatibility(Metadata):
    profile:str=Field(min_length=1,max_length=200)
    version:str=Field(min_length=1,max_length=100)
    status:Literal['planned','declared','tested','incompatible']='planned'
    evidence:HttpUrl|None=None
    testedAt:datetime|None=None
    @model_validator(mode='after')
    def evidence_required(self):
        if self.status=='tested' and (not self.evidence or not self.testedAt):raise ValueError('Testattu lompakkotuki vaatii näytön ja testipäivän')
        return self

class FieldMapping(Metadata):
    shapeUri:Iri
    semanticPath:list[Iri]=Field(min_length=1,max_length=10)
    fieldPath:Path
    valueKind:Literal['literal','object']='literal'
    datatype:Iri|None=None
    classUri:Iri|None=None
    minCount:int=Field(default=0,ge=0,le=10000)
    maxCount:int|None=Field(default=None,ge=0,le=10000)
    disclosure:Literal['selective','always']|None=None
    @model_validator(mode='after')
    def consistent(self):
        if self.maxCount is not None and self.minCount>self.maxCount:raise ValueError('minCount ei saa ylittää maxCount-arvoa')
        if self.valueKind=='literal' and (not self.datatype or self.classUri):raise ValueError('Literaalikartoitus tarvitsee tietotyypin, ei olion luokkaa')
        if self.valueKind=='object' and self.datatype:raise ValueError('Oliokartoitukseen ei kuulu literaalin tietotyyppiä')
        return self

class Mapping(Metadata):
    version:Semver='1.0.0'
    entries:list[FieldMapping]=Field(default_factory=list,max_length=200)

class Security(Metadata):
    mechanism:Literal['tls','dataIntegrity','jose','sdJwt']
    profileUri:Iri|None=None
    algorithms:list[Literal['ES256','ES384','EdDSA']]=Field(default_factory=list,max_length=10)

class Common(Metadata):
    id:UUID
    availability:Literal['planned','sandbox','production','suspended']='planned'
    environment:Literal['sandbox','production']='sandbox'
    providerOrganizationId:UUID
    operatorOrganizationId:UUID
    sourceProviderOrganizationId:UUID
    profileSnapshotId:UUID|None=None
    mapping:Mapping=Field(default_factory=Mapping)
    security:Security
    @model_validator(mode='after')
    def environment_matches(self):
        if self.availability in ('sandbox','production') and self.availability!=self.environment:raise ValueError('Käytettävän toimitustavan saatavuuden ja ympäristön on vastattava toisiaan')
        return self

class JsonApiDetails(Metadata):
    serviceUrl:ServiceUrl|None=None
    descriptionUrl:ServiceUrl|None=None
    openApiArtifactId:UUID|None=None
    jsonSchemaArtifactId:UUID|None=None
    authentication:Literal['none','oauth2','apiKey','mtls']='oauth2'
    requiredRights:list[Annotated[str,Field(min_length=1,max_length=200,pattern=r'^[A-Za-z0-9:._/\-]+$')]]=Field(default_factory=list,max_length=30)
    freshness:str=Field(default='',max_length=2000)

class JsonApiDistribution(Common):
    type:Literal['jsonApi']
    format:Literal['application/json']='application/json'
    protocol:Literal['httpsRest']='httpsRest'
    api:JsonApiDetails=Field(default_factory=JsonApiDetails)
    @model_validator(mode='after')
    def tls_security(self):
        if self.security.mechanism!='tls':raise ValueError('JSON API:n suojausmekanismi on tls; tunnistautuminen kuvataan erikseen')
        return self

class CredentialService(Metadata):
    issuerOrganizationId:UUID|None=None
    credentialIssuer:ServiceUrl|None=None
    initiationUrl:ServiceUrl|None=None
    protocol:Literal['OpenID4VCI']='OpenID4VCI'
    protocolVersion:Literal['1.0']='1.0'
    configurationIds:list[str]=Field(default_factory=list,max_length=30)
    validityProfile:Iri|None=None
    statusProfile:Iri|None=None
    subjectTypes:list[Literal['person','legalPerson']]=Field(default_factory=list)
    representationRequirements:str=Field(default='',max_length=2000)
    walletCompatibility:list[WalletCompatibility]=Field(default_factory=list,max_length=20)
    legalCategory:Literal['unassessed','nonQualified','publicSectorAttestation','QEAA']='unassessed'
    qualificationEvidence:str=Field(default='',max_length=2000)
    fee:str=Field(default='',max_length=300)
    support:str=Field(default='',max_length=1000)
    @field_validator('configurationIds')
    @classmethod
    def distinct_ids(cls,value):
        if any(not item or len(item)>200 for item in value) or len(set(value))!=len(value):raise ValueError('Konfiguraatiotunnisteiden on oltava yksilöllisiä ja enintään 200 merkkiä')
        return value

class W3cProfile(Metadata):
    vcdmVersion:Literal['2.0']='2.0'
    vcTypes:list[Iri|Literal['VerifiableCredential']]=Field(default_factory=lambda:['VerifiableCredential'],max_length=20)
    contexts:list[HttpUrl]=Field(default_factory=lambda:['https://www.w3.org/ns/credentials/v2'],max_length=20)
    contentPath:Path='/credentialSubject'

class W3cDistribution(Common):
    type:Literal['w3cVc']
    format:Literal['application/vc+ld+json']='application/vc+ld+json'
    credential:CredentialService=Field(default_factory=CredentialService)
    w3c:W3cProfile=Field(default_factory=W3cProfile)
    @model_validator(mode='after')
    def security_type(self):
        if self.security.mechanism not in ('dataIntegrity','jose'):raise ValueError('W3C VC:n suojaus on dataIntegrity tai jose')
        return self

class SdJwtProfile(Metadata):
    vct:Iri|None=None
    profileVersion:str=Field(default='',max_length=200)
    selectiveDisclosure:Literal['perClaim','always','never']='perClaim'
    holderBinding:Literal['required','optional','none']='required'
    nonDisclosableClaims:list[Path]=Field(default_factory=lambda:['/iss','/vct'],max_length=50)

class SdJwtDistribution(Common):
    type:Literal['sdJwtVc']
    format:Literal['application/dc+sd-jwt']='application/dc+sd-jwt'
    credential:CredentialService=Field(default_factory=CredentialService)
    sdJwt:SdJwtProfile=Field(default_factory=SdJwtProfile)
    @model_validator(mode='after')
    def security_type(self):
        if self.security.mechanism!='sdJwt':raise ValueError('SD-JWT VC:n suojausprofiili on sdJwt')
        return self

Distribution=Annotated[Union[JsonApiDistribution,W3cDistribution,SdJwtDistribution],Field(discriminator='type')]
