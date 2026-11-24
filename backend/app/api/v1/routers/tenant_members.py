from fastapi import APIRouter, Response, status

from app.dependencies import CurrentUser, Db
from app.schemas.tenant_members import TenantMemberCreate, TenantMemberRead, TenantMemberUpdate
from app.services import tenant_members

router = APIRouter(prefix="/api/tenants/{tenant_id}/members", tags=["Tenant members"])


@router.get("", response_model=list[TenantMemberRead])
def list_members(tenant_id: int, db: Db, user: CurrentUser):
    tenant_members.require_owner(db, tenant_id, user)
    return tenant_members.list_for_tenant(db, tenant_id)


@router.post("", response_model=TenantMemberRead, status_code=status.HTTP_201_CREATED)
def create_member(tenant_id: int, data: TenantMemberCreate, db: Db, user: CurrentUser):
    tenant_members.require_owner(db, tenant_id, user)
    return tenant_members.create(db, tenant_id, data)


@router.patch("/{member_id}", response_model=TenantMemberRead)
def update_member(tenant_id: int, member_id: int, data: TenantMemberUpdate, db: Db, user: CurrentUser):
    tenant_members.require_owner(db, tenant_id, user)
    return tenant_members.update(db, tenant_members.get(db, tenant_id, member_id), data)


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(tenant_id: int, member_id: int, db: Db, user: CurrentUser):
    tenant_members.require_owner(db, tenant_id, user)
    tenant_members.delete(db, tenant_members.get(db, tenant_id, member_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
