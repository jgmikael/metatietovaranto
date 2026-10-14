"""Phase 2B catalogue: OIDC sessions and organization-scoped editing."""
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
from apps.api.auth import build_router, seed_memberships, require_session, require_editor

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
    p = serialize(product)
    return {"@context": {"dcat": "http://www.w3.org/ns/dcat#", "dct": "http://purl.org/dc/terms/",
            "demo": "https://example.org/metatietovaranto/demo/", "xsd": "http://www.w3.org/2001/XMLSchema#"},
            "@id": p["uri"], "@type": "dcat:Dataset",
            "dct:title": {"@value": p["title"], "@language": "fi"},
            "dct:description": {"@value": p["description"], "@language": "fi"},
            "dct:publisher": {"@id": f"{BASE_URL}/id/organizations/{p['providerOrganizationId']}", "@type": "dct:Agent", "dct:title": p["provider"]},
            "dcat:keyword": p["theme"], "dct:source": p["source"],
            "dct:modified": {"@value": p["modifiedAt"], "@type": "xsd:dateTime"},
            "dct:accessRights": p["accessConditions"], "demo:synthetic": True,
            "demo:purpose": p["purpose"], "demo:limitations": p["limitations"],
            "demo:availability": p["availability"],
            "demo:dataElement": [{"demo:name": e["name"], "dct:description": e["description"],
                                  "dct:conformsTo": {"@id": e["semanticUri"]}} for e in p["dataElements"]]}

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
                product = Product(id=product_id)
                payload = {k: v for k, v in fixture.items() if k not in ("id", "provider")}
                payload["providerOrganizationId"] = organization_id
                assign(product, ProductInput(**payload), session)
                session.add(product)
            session.add(DemoInitialization(name="phase-1-fixtures"))
        seed_memberships(session)
        session.commit()
    yield

app = FastAPI(title="Metatietovaranto — paikallinen demo", lifespan=lifespan)
app.include_router(build_router(engine, BASE_URL))

@app.middleware("http")
async def private_auth_responses(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith(("/auth/", "/identity/")):
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

@app.get("/id/products/{product_id}")
def product_uri(product_id: UUID, request: Request):
    with Session(engine) as session:
        product = get_product(session, product_id)
        accept = request.headers.get("accept", "text/html")
        headers = {"Vary": "Accept"}
        if "application/ld+json" in accept:
            return JSONResponse(jsonld(product), media_type="application/ld+json", headers=headers)
        if "application/json" in accept:
            return JSONResponse(serialize(product), headers=headers)
        return RedirectResponse(f"/#{product_id}", status_code=303, headers=headers)

@app.get("/health/live")
def live():
    return {"status": "ok", "demo": True}

@app.get("/health/ready")
def ready():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1 FROM products LIMIT 1"))
        return {"status": "ready", "database": "postgresql"}
    except Exception:
        return JSONResponse({"status": "unavailable"}, status_code=503)

@app.get("/api/v1/products")
def search(q: str = Query("", max_length=200), theme: str = Query("", max_length=100),
           provider: str = Query("", max_length=200), limit: int = Query(20, ge=1, le=100),
           offset: int = Query(0, ge=0)):
    statement = select(Product)
    if q.strip():
        pattern = "%" + q.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
        statement = statement.where(or_(*(column.ilike(pattern, escape="\\") for column in
                                          (Product.title, Product.description, Product.provider))))
    if theme:
        statement = statement.where(Product.theme == theme)
    if provider:
        statement = statement.where(Product.provider == provider)
    with Session(engine) as session:
        total = session.scalar(select(func.count()).select_from(statement.subquery()))
        items = session.scalars(statement.order_by(Product.title, Product.id).offset(offset).limit(limit)).all()
        return {"items": [serialize(p) for p in items], "total": total, "offset": offset, "limit": limit}

@app.get("/api/v1/products/{product_id}")
def detail(product_id: UUID):
    with Session(engine) as session:
        return serialize(get_product(session, product_id))

@app.post("/api/v1/products", status_code=201)
def create(data: ProductInput, response: Response, request: Request):
    with Session(engine) as session:
        identity = require_session(request, session)
        require_editor(session, identity, data.providerOrganizationId)
        product = Product()
        assign(product, data, session)
        session.add(product)
        session.commit()
        response.headers["Location"] = f"/api/v1/products/{product.id}"
        return serialize(product)

@app.put("/api/v1/products/{product_id}")
def update(product_id: UUID, data: ProductInput, request: Request):
    with Session(engine) as session:
        identity = require_session(request, session)
        product = get_product(session, product_id)
        require_editor(session, identity, product.provider_organization_id)
        require_editor(session, identity, data.providerOrganizationId)
        assign(product, data, session)
        session.commit()
        return serialize(product)

@app.delete("/api/v1/products/{product_id}", status_code=204)
def delete(product_id: UUID, request: Request):
    with Session(engine) as session:
        identity = require_session(request, session)
        product = get_product(session, product_id)
        require_editor(session, identity, product.provider_organization_id)
        session.delete(product)
        session.commit()

@app.get("/api/v1/products/{product_id}/export")
def export(product_id: UUID, format: Literal["json", "jsonld"] = "json"):
    with Session(engine) as session:
        product = get_product(session, product_id)
        return JSONResponse(jsonld(product) if format == "jsonld" else serialize(product),
                            media_type="application/ld+json" if format == "jsonld" else "application/json")

@app.get("/api/v1/catalog/export")
def catalog_export(format: Literal["json", "jsonld"] = "json"):
    with Session(engine) as session:
        products = session.scalars(select(Product).order_by(Product.id)).all()
        if format == "json":
            return {"demo": True, "items": [serialize(p) for p in products]}
        return JSONResponse({"@context": {"dcat": "http://www.w3.org/ns/dcat#"},
                             "@id": f"{BASE_URL}/id/catalog", "@type": "dcat:Catalog",
                             "dcat:dataset": [jsonld(p) for p in products]}, media_type="application/ld+json")

# Static React build is served from the same origin; no CORS configuration is needed.
WEB = ROOT / "apps/web/dist"
if WEB.exists():
    app.mount("/", StaticFiles(directory=WEB, html=True), name="web")

