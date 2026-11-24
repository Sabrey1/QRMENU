from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tenant_members import Tenant_Member
from app.models.users import User
from app.schemas.tenant_members import TenantMemberCreate, TenantMemberUpdate
from app.services.common import commit
from app.services.tenants import require_membership


def require_owner(db: Session, tenant_id: int, user: User) -> None:
    require_membership(db, tenant_id, user)
    member = db.scalar(select(Tenant_Member).where(Tenant_Member.tenant_id == tenant_id, Tenant_Member.user_id == user.id))
    if member.role != "owner":
        raise HTTPException(status_code=403, detail="Tenant owner access required")


def get(db: Session, tenant_id: int, member_id: int) -> Tenant_Member:
    member = db.scalar(select(Tenant_Member).where(Tenant_Member.tenant_id == tenant_id, Tenant_Member.id == member_id))
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


def validate_role(role: str) -> None:
    if role not in {"admin", "member"}:
        raise HTTPException(status_code=422, detail="Role must be admin or member")


def list_for_tenant(db: Session, tenant_id: int) -> list[Tenant_Member]:
    return list(db.scalars(select(Tenant_Member).where(Tenant_Member.tenant_id == tenant_id).order_by(Tenant_Member.id)))


def create(db: Session, tenant_id: int, data: TenantMemberCreate) -> Tenant_Member:
    if data.tenant_id != tenant_id:
        raise HTTPException(status_code=422, detail="Body tenant_id must match the URL")
    validate_role(data.role)
    if not db.get(User, data.user_id):
        raise HTTPException(status_code=404, detail="User not found")
    member = Tenant_Member(**data.model_dump())
    db.add(member)
    commit(db)
    db.refresh(member)
    return member


def update(db: Session, member: Tenant_Member, data: TenantMemberUpdate) -> Tenant_Member:
    if member.role == "owner":
        raise HTTPException(status_code=403, detail="The owner cannot be changed here")
    if "role" in data.model_fields_set:
        validate_role(data.role)
        member.role = data.role
    commit(db)
    db.refresh(member)
    return member


def delete(db: Session, member: Tenant_Member) -> None:
    if member.role == "owner":
        raise HTTPException(status_code=403, detail="The owner cannot be removed")
    db.delete(member)
    commit(db)
