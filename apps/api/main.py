"""Phase 2C catalogue: private drafts, profile snapshots and immutable publications."""
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
from uuid import UUID, NAMESPACE_URL, uuid5
import json

from fastapi import FastAPI, HTTPException, Query, Response, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator
from sqlalchemy import create_engine, func, or_, select, text
from sqlalchemy.orm import Session
from apps.api.public_url import public_base_url
from apps.api.models import Base, Product, Organization, DemoInitialization
from apps.api.migrate import upgrade_database
from apps.api.publication import build_publication_router, initialize_drafts
from apps.api.profiles import build_profile_router
from apps.api.auth import build_router, seed_memberships, require_session, require_editor, seed_review_memberships

ROOT = Path(__file__).resolve().parents[2]
BASE_URL = public_base_url()
engine = create_engine(os.getenv("DATABASE_URL", "postgresql+psycopg://demo:demo@localhost:5432/catalog"), pool_pre_ping=True)

class Element(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=500)
    semanticUri: HttpUrl

class ProductInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=5000)
    providerOrganizationId: UUID
    theme: str = Field(min_length=1, max_length=100)
    source: str = Field(min_length=1, max_length=500)
    purpose: str = Field(min_length=1, max_length=2000)
    limitations: str = Field(min_length=1, max_length=2000)
    accessConditions: str = Field(min_length=1, max_length=2000)
    availability: Literal["planned", "sandbox"] = "sandbox"
    dataElements: list[Element] = Field(min_length=1, max_length=50)
    synthetic: Literal[True] = True

    @field_validator("title", "description", "theme", "source", "purpose", "limitations", "accessConditions")
    @classmethod
    def not_blank(cls, value):
        if not value.strip():
            raise ValueError("Kenttä ei saa olla tyhjä")
        return value

def assign(product, data, session):
    values = data.model_dump(mode="json")
    organization_id = values.pop("providerOrganizationId")
    organization = session.get(Organization, UUID(organization_id))
    if organization is None:
        raise HTTPException(422, "Tarjoajaorganisaatiota ei löydy")
    product.provider_organization_id = organization.id
    product.provider = organization.legal_name
    for key in ("title", "description", "theme"):
        setattr(product, key, values.pop(key))
    product.metadata_ = values
    product.modified_at = datetime.now(timezone.utc)

def serialize(product):
    return {"id": str(product.id), "uri": f"{BASE_URL}/id/products/{product.id}",
            "title": product.title, "description": product.description,
            "provider": product.provider, "providerOrganizationId": str(product.provider_organization_id), "theme": product.theme,
            **product.metadata_, "modifiedAt": product.modified_at.isoformat(), "demo": True}

def get_product(session, product_id):
    product = session.get(Product, product_id)
    if product is None:
        raise HTTPException(404, "Tietotuotetta ei löydy")
    return product

def jsonld(product):
    p = product if isinstance(product, dict) else serialize(product)
    return {"@context": {"dcat": "http://www.w3.org/ns/dcat#", "dct": "http://purl.org/dc/terms/",
            "demo": "https://example.org/metatietovaranto/demo/", "xsd": "http://www.w3.org/2001/XMLSchema#"},
            "@id": p.get("versionUri",p["uri"]), "@type": "dcat:Dataset",
            "dcat:version": p.get("version", "unpublished"),
            "dct:title": {"@value": p["title"], "@language": "fi"},
            "dct:description": {"@value": p["description"], "@language": "fi"},
            "dct:publisher": {"@id": f"{BASE_URL}/id/organizations/{p['providerOrganizationId']}", "@type": "dct:Agent", "dct:title": p["provider"]},
            "dcat:keyword": p["theme"], "dct:source": p["source"],
            "dct:modified": {"@value": p["modifiedAt"], "@type": "xsd:dateTime"},
            "dct:accessRights": p["accessConditions"], "demo:synthetic": True,
            "demo:primaryDelivery": p.get("issuance", {}).get("primaryDelivery", "w3cVc"),
            "demo:serviceAvailability": p.get("issuance", {}).get("serviceAvailability", "planned"),
            "demo:vcMetadata": json.dumps(p.get("issuance",{}), ensure_ascii=False),
            "demo:purpose": p["purpose"], "demo:limitations": p["limitations"],
            "demo:availability": p["availability"],
            "demo:dataElement": [{"demo:name": e["name"], "dct:description": e["description"],
                                  **({"dct:conformsTo": {"@id": e["semanticUri"]}} if e.get("semanticUri") else {})} for e in p["dataElements"]]}

@asynccontextmanager
async def lifespan(app):
    if os.getenv("DEMO_MODE") != "true":
        raise RuntimeError("Demo vaatii DEMO_MODE=true; vain paikalliseen demokäyttöön")
    # Fail startup before readiness/fixtures if adoption or upgrade is unsafe.
    upgrade_database(engine)
    with Session(engine) as session:
        # Transaction lock makes first initialization safe even with concurrent starts.
        session.execute(text("SELECT pg_advisory_xact_lock(17294001)"))
        if session.get(DemoInitialization, "phase-1-fixtures") is None:
            for fixture in json.loads((ROOT / "fixtures/products.json").read_text()):
                product_id = UUID(fixture["id"])
                if session.get(Product, product_id) is not None:
                    continue
                organization_id = uuid5(NAMESPACE_URL, f"https://example.org/metatietovaranto/legacy-provider/{product_id}")
                organization = session.get(Organization, organization_id)
                if organization is None:
                    session.add(Organization(id=organization_id, legal_name=fixture["provider"],
                                country="FI", identifiers=[{"scheme": "demo", "value": str(product_id)}],
                                synthetic=True, legacy_product_id=None))
                    session.flush()
                product = Product(id=product_id, owner_organization_id=organization_id)
                payload = {k: v for k, v in fixture.items() if k not in ("id", "provider")}
                payload["providerOrganizationId"] = organization_id
                assign(product, ProductInput(**payload), session)
                session.add(product)
            session.add(DemoInitialization(name="phase-1-fixtures"))
        seed_memberships(session)
        seed_review_memberships(session)
        initialize_drafts(session)
        session.commit()
    yield

app = FastAPI(title="Metatietovaranto — paikallinen demo", lifespan=lifespan)
app.include_router(build_router(engine, BASE_URL))

@app.middleware("http")
async def private_auth_responses(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith(("/auth/", "/identity/", "/api/")):
        response.headers["Cache-Control"] = "no-store"
        response.headers["Referrer-Policy"] = "no-referrer"
    return response

def serialize_organization(organization):
    return {"id": str(organization.id), "legalName": organization.legal_name,
            "country": organization.country, "identifiers": organization.identifiers,
            "synthetic": organization.synthetic,
            "legacyProductId": str(organization.legacy_product_id) if organization.legacy_product_id else None}

@app.get("/api/v1/organizations")
def organizations():
    with Session(engine) as session:
        items = session.scalars(select(Organization).order_by(Organization.legal_name, Organization.id)).all()
        return {"items": [serialize_organization(item) for item in items]}

@app.get("/api/v1/organizations/{organization_id}")
def organization_detail(organization_id: UUID):
    with Session(engine) as session:
        organization = session.get(Organization, organization_id)
        if organization is None:
            raise HTTPException(404, "Organisaatiota ei löydy")
        return serialize_organization(organization)

@app.get("/health/live")
def live():
    return {"status":"ok","demo":True}

@app.get("/health/ready")
def ready():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1 FROM drafts LIMIT 1"))
        return {"status":"ready","database":"postgresql"}
    except Exception:
        return JSONResponse({"status":"unavailable"},status_code=503)

app.include_router(build_profile_router(engine))
app.include_router(build_publication_router(engine, BASE_URL, jsonld))

# Static React build is served from the same origin; no CORS configuration is needed.
WEB = ROOT / "apps/web/dist"
if WEB.exists():
    app.mount("/", StaticFiles(directory=WEB, html=True), name="web")

