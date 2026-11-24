import re
import unicodedata
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.tenants import Tenant
from app.models.tenant_members import Tenant_Member
from app.models.users import User
from app.schemas.tenants import TenantCreate, TenantUpdate
from app.services.common import commit

RESERVED_SLUGS = {"www", "api", "admin", "app", "mail", "ftp", "support"}
SLUG_PATTERN = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?")


def validate_slug(slug: str) -> str:
    if not SLUG_PATTERN.fullmatch(slug) or slug in RESERVED_SLUGS:
        raise HTTPException(status_code=422, detail="Slug must be 1-63 lowercase letters, numbers, or hyphens, start and end with a letter or number, and not be reserved")
    return slug


def generate_slug(db: Session, name: str) -> str:
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    base = re.sub(r"[^a-z0-9]+", "-", ascii_name).strip("-")[:63].rstrip("-")
    if not base:
        base = f"shop-{uuid4().hex[:8]}"
    if base in RESERVED_SLUGS:
        base = f"{base}-shop"
    candidate = base
    suffix = 2
    while db.scalar(select(Tenant.id).where(Tenant.slug == candidate)) is not None:
        ending = f"-{suffix}"
        candidate = base[:63 - len(ending)].rstrip("-") + ending
        suffix += 1
    return candidate


def require_membership(db: Session, tenant_id: int, user: User, *, manage: bool = False) -> Tenant:
    tenant = db.get(Tenant, tenant_id)
    member = db.scalar(select(Tenant_Member).where(Tenant_Member.tenant_id == tenant_id, Tenant_Member.user_id == user.id))
    if not tenant or not member:
        raise HTTPException(status_code=404, detail="Tenant not found")
    if manage and member.role not in {"owner", "admin"}:
        raise HTTPException(status_code=403, detail="Tenant manager access required")
    return tenant


def ensure_slug_available(db: Session, slug: str | None, tenant_id: int | None = None) -> None:
    if slug is None:
        return
    query = select(Tenant.id).where(Tenant.slug == slug)
    if tenant_id is not None:
        query = query.where(Tenant.id != tenant_id)
    if db.scalar(query) is not None:
        raise HTTPException(status_code=409, detail="Slug is already in use")


def add_for_owner(db: Session, data: TenantCreate, user: User) -> Tenant:
    values = data.model_dump()
    values["slug"] = validate_slug(data.slug) if data.slug is not None else generate_slug(db, data.name)
    ensure_slug_available(db, values["slug"])
    tenant = Tenant(**values)
    db.add(tenant)
    db.flush()
    db.add(Tenant_Member(tenant_id=tenant.id, user_id=user.id, role="owner"))
    return tenant


def create(db: Session, data: TenantCreate, user: User) -> Tenant:
    try:
        tenant = add_for_owner(db, data, user)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Tenant data conflicts with an existing record; try another slug") from exc
    commit(db)
    db.refresh(tenant)
    return tenant


def list_for_user(db: Session, user: User) -> list[Tenant]:
    return list(db.scalars(select(Tenant).join(Tenant_Member, Tenant.id == Tenant_Member.tenant_id).where(Tenant_Member.user_id == user.id).order_by(Tenant.id)))


def update(db: Session, tenant: Tenant, data: TenantUpdate) -> Tenant:
    values = data.model_dump(exclude_unset=True)
    if "slug" in values:
        if values["slug"] is None:
            raise HTTPException(status_code=422, detail="Slug cannot be null")
        validate_slug(values["slug"])
        ensure_slug_available(db, values["slug"], tenant.id)
    for key, value in values.items():
        setattr(tenant, key, value)
    commit(db)
    db.refresh(tenant)
    return tenant
