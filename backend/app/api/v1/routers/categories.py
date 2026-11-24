from fastapi import APIRouter, Response, status

from app.dependencies import CurrentUser, Db
from app.schemas.categories import CategoryCreate, CategoryRead, CategoryUpdate
from app.services import categories, tenants

router = APIRouter(prefix="/api/tenants/{tenant_id}/categories", tags=["Categories"])


@router.get("", response_model=list[CategoryRead])
def list_categories(tenant_id: int, db: Db, user: CurrentUser):
    tenants.require_membership(db, tenant_id, user)
    return categories.list_for_tenant(db, tenant_id)


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(tenant_id: int, data: CategoryCreate, db: Db, user: CurrentUser):
    tenants.require_membership(db, tenant_id, user, manage=True)
    return categories.create(db, tenant_id, data)


@router.get("/{category_id}", response_model=CategoryRead)
def get_category(tenant_id: int, category_id: int, db: Db, user: CurrentUser):
    tenants.require_membership(db, tenant_id, user)
    return categories.get(db, tenant_id, category_id)


@router.patch("/{category_id}", response_model=CategoryRead)
def update_category(tenant_id: int, category_id: int, data: CategoryUpdate, db: Db, user: CurrentUser):
    tenants.require_membership(db, tenant_id, user, manage=True)
    return categories.update(db, categories.get(db, tenant_id, category_id), data)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(tenant_id: int, category_id: int, db: Db, user: CurrentUser):
    tenants.require_membership(db, tenant_id, user, manage=True)
    categories.delete(db, categories.get(db, tenant_id, category_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
