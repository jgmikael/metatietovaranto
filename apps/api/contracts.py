"""Phase 2C metadata contracts; no issuance transactions or wallet tokens."""
from datetime import datetime
import ipaddress
from typing import Literal, Annotated
from urllib.parse import urlsplit, parse_qs
import re
from uuid import UUID
from apps.api.metadata_urls import initiation_url
from apps.api.distribution_contracts import Distribution, WalletCompatibility
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator, model_validator, StringConstraints


class Contract(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


class CredentialProfile(Contract):
    vcTypes: list[str] = Field(default_factory=list, max_length=20)
    vcdmVersion: Literal['2.0'] = '2.0'
    contexts: list[HttpUrl] = Field(default_factory=list, max_length=20)
    contentPath: str = Field(default='credentialSubject', min_length=1, max_length=200)
    fieldMappings: dict[str,str] = Field(default_factory=dict, max_length=100)
    securityMechanism: str = Field(default='', max_length=300)

    @field_validator('vcTypes')
    @classmethod
    def absolute_types(cls, values):
        if any(value != 'VerifiableCredential' and not re.match(r'^[A-Za-z][A-Za-z0-9+.-]*:[^\s]+$', value) for value in values):
            raise ValueError('VC-tyypin on oltava VerifiableCredential tai alkuperäinen absoluuttinen IRI')
        return values


class Issuance(Contract):
    primaryDelivery: Literal['w3cVc'] = 'w3cVc'
    serviceAvailability: Literal['planned','sandbox','production','suspended'] = 'planned'
    environment: Literal['sandbox','production'] = 'sandbox'
    issuanceInitiationUrl: str | None = Field(default=None, max_length=2048)
    issuerOrganizationId: UUID | None = None
    operatorOrganizationId: UUID | None = None
    sourceProviderOrganizationId: UUID | None = None
    credentialProfile: CredentialProfile = Field(default_factory=CredentialProfile)
    credentialIssuer: HttpUrl | None = None
    credentialConfigurationIds: list[str] = Field(default_factory=list, max_length=50)
    issuanceProtocol: str = Field(default='OpenID4VCI', min_length=1, max_length=100)
    protocolVersion: str = Field(default='1.0', min_length=1, max_length=100)
    walletCompatibility: list[WalletCompatibility] = Field(default_factory=list, max_length=20)
    subjectTypes: list[Literal['person','legalPerson']] = Field(default_factory=list)
    representationRequirements: str = Field(default='', max_length=2000)
    legalCategory: Literal['unassessed','nonQualified','publicSectorAttestation','QEAA'] = 'unassessed'
    qualificationEvidence: str = Field(default='', max_length=2000)
    validityPolicy: str = Field(default='', max_length=2000)
    statusPolicy: str = Field(default='', max_length=2000)
    support: str = Field(default='', max_length=1000)
    fee: str = Field(default='', max_length=300)

    @field_validator('issuanceInitiationUrl')
    @classmethod
    def public_link(cls,value):
        return initiation_url(value) if value else None


class SyntheticExample(Contract):
    serialization: Literal['turtle','rdfxml','jsonld'] = 'turtle'
    content: Annotated[str, StringConstraints(strip_whitespace=False)] = Field(min_length=1, max_length=100_000)
    synthetic: Literal[True]

    @field_validator('content')
    @classmethod
    def bounded_utf8(cls, value):
        if len(value.encode()) > 100_000:
            raise ValueError('Synteettisen esimerkin raja on 100 kB')
        return value


class DerivedExample(Contract):
    artifactId: UUID
    content: Annotated[str, StringConstraints(strip_whitespace=False)] = Field(min_length=1,max_length=100_000)
    synthetic: Literal[True]

    @field_validator('content')
    @classmethod
    def bounded_json_utf8(cls,value):
        if len(value.encode())>100_000:raise ValueError('JSON-esimerkin raja on 100 kB')
        return value


class ProductWrite(Contract):
    title: str = Field(min_length=1,max_length=200)
    description: str = Field(min_length=1,max_length=5000)
    providerOrganizationId: UUID
    theme: str = Field(min_length=1,max_length=100)
    source: str = Field(min_length=1,max_length=500)
    purpose: str = Field(min_length=1,max_length=2000)
    limitations: str = Field(min_length=1,max_length=2000)
    accessConditions: str = Field(min_length=1,max_length=2000)
    availability: Literal['planned','sandbox'] = 'sandbox'
    synthetic: Literal[True] = True
    profileSnapshotId: UUID | None = None
    issuance: Issuance = Field(default_factory=Issuance)
    syntheticExample: SyntheticExample | None = None
    distributions: list[Distribution] | None = Field(default=None,min_length=1,max_length=10)
    primaryDistributionId: UUID | None = None
    derivedExamples: list[DerivedExample] = Field(default_factory=list,max_length=10)

    @field_validator('derivedExamples')
    @classmethod
    def bounded_derived_examples(cls, examples):
        if sum(len(example.content.encode()) for example in examples)>200_000:
            raise ValueError('JSON-esimerkkien yhteisraja on 200 kB')
        if len({example.artifactId for example in examples})!=len(examples):
            raise ValueError('Yksi JSON-esimerkki kutakin johdannaisartefaktia kohti')
        return examples
