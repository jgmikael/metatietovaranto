"""Persistent phase 2A models. Schema changes belong in Alembic revisions."""
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Organization(Base):
    __tablename__ = "organizations"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    legal_name: Mapped[str] = mapped_column(String(200))
    country: Mapped[str] = mapped_column(String(2))
    identifiers: Mapped[list[dict]] = mapped_column(JSONB)
    synthetic: Mapped[bool] = mapped_column(Boolean)
    # Provenance only: do not cascade-delete the organization when a product is removed.
    legacy_product_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), unique=True)


class Product(Base):
    __tablename__ = "products"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(200), index=True)
    description: Mapped[str] = mapped_column(String(5000))
    # Retained compatibility label, never used to resolve an organization identity.
    provider: Mapped[str] = mapped_column(String(200), index=True)
    provider_organization_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("organizations.id", ondelete="RESTRICT"), index=True)
    theme: Mapped[str] = mapped_column(String(100), index=True)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB)
    modified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class DemoInitialization(Base):
    __tablename__ = "demo_initialization"
    name: Mapped[str] = mapped_column(String(100), primary_key=True)
