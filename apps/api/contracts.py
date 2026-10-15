"""Phase 2C metadata contracts; no issuance transactions or wallet tokens."""
from datetime import datetime
import ipaddress
from typing import Literal
from urllib.parse import urlsplit, parse_qs
import re
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator, model_validator


class Contract(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


class WalletCompatibility(Contract):
    profile: str = Field(min_length=1, max_length=200)
    version: str = Field(min_length=1, max_length=100)
    status: Literal['planned','declared','tested','incompatible'] = 'planned'
    evidence: HttpUrl | None = None
    testedAt: datetime | None = None

    @model_validator(mode='after')
    def evidence_required(self):
        if self.status == 'tested' and (not self.evidence or not self.testedAt):
            raise ValueError('Testattu lompakkotuki vaatii näytön ja testipäivän')
        return self


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


def initiation_url(value):
    url = urlsplit(value)
    host = (url.hostname or '').lower()
    if url.scheme != 'https' or not host or url.username or url.password or url.fragment or url.port not in (None,443):
        raise ValueError('Asiointilinkin on oltava pysyvä HTTPS-osoite ilman tunnuksia tai fragmenttia')
    if (host == 'localhost' or host.endswith(('.localhost','.invalid','.test','.example'))
            or any(host == domain or host.endswith('.'+domain) for domain in ('example.com','example.org','example.net'))):
        raise ValueError('Esimerkkiverkkotunnus ei ole käytettävä myöntämispalvelu')
    try:
        if not ipaddress.ip_address(host).is_global:
            raise ValueError('Sisäverkon osoite ei ole julkinen asiointilinkki')
    except ValueError as error:
        if 'Sisäverkon' in str(error):raise
    query = parse_qs(url.query, keep_blank_values=True)
    if set(query) - {'product','profile','configuration'} or len(value)>2048:
        raise ValueError('Asiointilinkkiin sallitaan vain julkiset product/profile/configuration-tunnisteet, ei tarjouksia tai tokeneita')
    if any(len(v)>256 for values in query.values() for v in values):
        raise ValueError('Liian pitkä julkinen tunniste')
    return value


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
