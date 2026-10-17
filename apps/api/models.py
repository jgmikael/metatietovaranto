"""Persistent catalogue, membership and session models. Schema changes belong in Alembic revisions."""
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Boolean, DateTime, ForeignKey, String, UniqueConstraint
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
    owner_organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"))
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


class OrganizationMembership(Base):
    __tablename__ = "organization_memberships"
    subject: Mapped[str] = mapped_column(String(255), primary_key=True)
    organization_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("organizations.id", ondelete="RESTRICT"), primary_key=True)
    role: Mapped[str] = mapped_column(String(20))


class WebSession(Base):
    __tablename__ = "web_sessions"
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    subject: Mapped[str] = mapped_column(String(255))
    username: Mapped[str] = mapped_column(String(255))
    csrf_token: Mapped[str] = mapped_column(String(64))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class OAuthFlow(Base):
    __tablename__ = "oauth_flows"
    state_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    flow_hash: Mapped[str] = mapped_column(String(64))
    verifier: Mapped[str] = mapped_column(String(128))
    nonce: Mapped[str] = mapped_column(String(128))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class SemanticProfile(Base):
    __tablename__ = "semantic_profiles"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    profile_uri: Mapped[str | None] = mapped_column(String(2048), unique=True)


class ProfileSnapshot(Base):
    __tablename__ = "profile_snapshots"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    profile_id: Mapped[UUID] = mapped_column(ForeignKey("semantic_profiles.id"))
    owner_organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"))
    manifest: Mapped[dict] = mapped_column(JSONB)
    checksum: Mapped[str] = mapped_column(String(64))
    graph_hash: Mapped[str | None] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Draft(Base):
    __tablename__ = "drafts"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.id"), unique=True)
    content: Mapped[dict] = mapped_column(JSONB)
    profile_snapshot_id: Mapped[UUID | None] = mapped_column(ForeignKey("profile_snapshots.id"))
    revision: Mapped[int] = mapped_column(default=1)
    status: Mapped[str] = mapped_column(String(30), default="draft")
    checksum: Mapped[str] = mapped_column(String(64))
    contributors: Mapped[list[str]] = mapped_column(JSONB)
    approved_review_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True))
    modified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Review(Base):
    __tablename__ = "reviews"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    draft_id: Mapped[UUID] = mapped_column(ForeignKey("drafts.id"))
    revision: Mapped[int]
    checksum: Mapped[str] = mapped_column(String(64))
    reviewer: Mapped[str] = mapped_column(String(255))
    decision: Mapped[str] = mapped_column(String(30))
    reason: Mapped[str] = mapped_column(String(2000))
    source_reviewed: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ProductVersion(Base):
    __tablename__ = "product_versions"
    __table_args__ = (
        UniqueConstraint('product_id', 'version'),
        UniqueConstraint('product_id', 'sequence'),)
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.id"))
    version: Mapped[str] = mapped_column(String(50))
    sequence: Mapped[int]
    content: Mapped[dict] = mapped_column(JSONB)
    checksum: Mapped[str] = mapped_column(String(64))
    profile_snapshot_id: Mapped[UUID] = mapped_column(ForeignKey("profile_snapshots.id"))
    review_id: Mapped[UUID] = mapped_column(ForeignKey("reviews.id"))
    publisher: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"))
    product_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True))
    actor: Mapped[str] = mapped_column(String(255))
    action: Mapped[str] = mapped_column(String(50))
    before_hash: Mapped[str | None] = mapped_column(String(64))
    after_hash: Mapped[str | None] = mapped_column(String(64))
    reason: Mapped[str] = mapped_column(String(2000))
    details: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class IdempotentOperation(Base):
    __tablename__ = "idempotent_operations"
    subject: Mapped[str] = mapped_column(String(255), primary_key=True)
    operation: Mapped[str] = mapped_column(String(100), primary_key=True)
    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    request_hash: Mapped[str] = mapped_column(String(64))
    response: Mapped[dict] = mapped_column(JSONB)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class OutboxEvent(Base):
    __tablename__ = "outbox_events"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    version_id: Mapped[UUID] = mapped_column(ForeignKey("product_versions.id"), unique=True)
    payload: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class LifecycleEvent(Base):
    __tablename__ = 'lifecycle_events'
    __table_args__ = (
        UniqueConstraint('version_id', 'sequence'),
        CheckConstraint('sequence > 0', name='ck_lifecycle_sequence'),
        CheckConstraint("(previous_status = 'published' AND status IN ('deprecated','withdrawn')) OR (previous_status = 'deprecated' AND status = 'withdrawn')", name='ck_lifecycle_transition'),
        CheckConstraint("replacement_version_id IS NULL OR (status = 'deprecated' AND replacement_version_id <> version_id)", name='ck_lifecycle_replacement'),)
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    version_id: Mapped[UUID] = mapped_column(ForeignKey('product_versions.id'))
    sequence: Mapped[int]
    previous_status: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20))
    reason: Mapped[str] = mapped_column(String(2000))
    replacement_version_id: Mapped[UUID | None] = mapped_column(ForeignKey('product_versions.id'))
    actor: Mapped[str] = mapped_column(String(255))
    organization_id: Mapped[UUID] = mapped_column(ForeignKey('organizations.id'))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class LifecycleOutboxEvent(Base):
    __tablename__ = 'lifecycle_outbox_events'
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    event_id: Mapped[UUID] = mapped_column(ForeignKey('lifecycle_events.id'), unique=True)
    payload: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
