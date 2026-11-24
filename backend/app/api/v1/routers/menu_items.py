from fastapi import APIRouter, Response, status

from app.dependencies import CurrentUser, Db
from app.schemas.menu_items import MenuItemCreate, MenuItemRead, MenuItemUpdate
from app.services import menu_items, tenants

router = APIRouter(prefix="/api/tenants/{tenant_id}/menu-items", tags=["Menu items"])


@router.get("", response_model=list[MenuItemRead])
def list_menu_items(tenant_id: int, db: Db, user: CurrentUser):
    tenants.require_membership(db, tenant_id, user)
    return menu_items.list_for_tenant(db, tenant_id)


@router.post("", response_model=MenuItemRead, status_code=status.HTTP_201_CREATED)
def create_menu_item(tenant_id: int, data: MenuItemCreate, db: Db, user: CurrentUser):
    tenants.require_membership(db, tenant_id, user, manage=True)
    return menu_items.create(db, tenant_id, data)


@router.get("/{item_id}", response_model=MenuItemRead)
def get_menu_item(tenant_id: int, item_id: int, db: Db, user: CurrentUser):
    tenants.require_membership(db, tenant_id, user)
    return menu_items.get(db, tenant_id, item_id)


@router.patch("/{item_id}", response_model=MenuItemRead)
def update_menu_item(tenant_id: int, item_id: int, data: MenuItemUpdate, db: Db, user: CurrentUser):
    tenants.require_membership(db, tenant_id, user, manage=True)
    return menu_items.update(db, tenant_id, menu_items.get(db, tenant_id, item_id), data)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu_item(tenant_id: int, item_id: int, db: Db, user: CurrentUser):
    tenants.require_membership(db, tenant_id, user, manage=True)
    menu_items.delete(db, menu_items.get(db, tenant_id, item_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
