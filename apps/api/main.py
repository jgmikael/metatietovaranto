"""Phase 1 local catalogue. No authentication or publication workflow."""
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
from uuid import UUID, uuid4
import json

from fastapi import FastAPI, HTTPException, Query, Response, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator
from sqlalchemy import DateTime, String, create_engine, func, or_, select, text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from apps.api.public_url import public_base_url

ROOT = Path(__file__).resolve().parents[2]
BASE_URL = public_base_url()
engine = create_engine(os.getenv("DATABASE_URL", "postgresql+psycopg://demo:demo@localhost:5432/catalog"), pool_pre_ping=True)

class Base(DeclarativeBase):
    pass

class Product(Base):
    __tablename__ = "products"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(200), index=True)
    description: Mapped[str] = mapped_column(String(5000))
    provider: Mapped[str] = mapped_column(String(200), index=True)
    theme: Mapped[str] = mapped_column(String(100), index=True)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB)
    modified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class DemoInitialization(Base):
    __tablename__ = "demo_initialization"
    name: Mapped[str] = mapped_column(String(100), primary_key=True)

class Element(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=500)
    semanticUri: HttpUrl

class ProductInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=5000)
    provider: str = Field(min_length=1, max_length=200)
    theme: str = Field(min_length=1, max_length=100)
    source: str = Field(min_length=1, max_length=500)
    purpose: str = Field(min_length=1, max_length=2000)
    limitations: str = Field(min_length=1, max_length=2000)
    accessConditions: str = Field(min_length=1, max_length=2000)
    availability: Literal["planned", "sandbox"] = "sandbox"
    dataElements: list[Element] = Field(min_length=1, max_length=50)
    synthetic: Literal[True] = True

    @field_validator("title", "description", "provider", "theme", "source", "purpose", "limitations", "accessConditions")
    @classmethod
    def not_blank(cls, value):
        if not value.strip():
            raise ValueError("Kenttä ei saa olla tyhjä")
        return value

def assign(product, data):
    values = data.model_dump(mode="json")
    for key in ("title", "description", "provider", "theme"):
        setattr(product, key, values.pop(key))
    product.metadata_ = values
    product.modified_at = datetime.now(timezone.utc)

def serialize(product):
    return {"id": str(product.id), "uri": f"{BASE_URL}/id/products/{product.id}",
            "title": product.title, "description": product.description,
            "provider": product.provider, "theme": product.theme,
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
            "dct:publisher": {"@type": "dct:Agent", "dct:title": p["provider"]},
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
        raise RuntimeError("Vaihe 1 vaatii DEMO_MODE=true; vain paikalliseen demokäyttöön")
    # Phase 1 has one initial schema; migration history is introduced before schema evolution.
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        # Transaction lock makes first initialization safe even with concurrent starts.
        session.execute(text("SELECT pg_advisory_xact_lock(17294001)"))
        if session.get(DemoInitialization, "phase-1-fixtures") is None:
            for fixture in json.loads((ROOT / "fixtures/products.json").read_text()):
                product_id = UUID(fixture["id"])
                if session.get(Product, product_id) is not None:
                    continue
                product = Product(id=product_id)
                assign(product, ProductInput(**{k: v for k, v in fixture.items() if k != "id"}))
                session.add(product)
            session.add(DemoInitialization(name="phase-1-fixtures"))
        session.commit()
    yield

app = FastAPI(title="Metatietovaranto — paikallinen demo", lifespan=lifespan)

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
def create(data: ProductInput, response: Response):
    with Session(engine) as session:
        product = Product()
        assign(product, data)
        session.add(product)
        session.commit()
        response.headers["Location"] = f"/api/v1/products/{product.id}"
        return serialize(product)

@app.put("/api/v1/products/{product_id}")
def update(product_id: UUID, data: ProductInput):
    with Session(engine) as session:
        product = get_product(session, product_id)
        assign(product, data)
        session.commit()
        return serialize(product)

@app.delete("/api/v1/products/{product_id}", status_code=204)
def delete(product_id: UUID):
    with Session(engine) as session:
        session.delete(get_product(session, product_id))
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

