from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.menu_items import Menu_Items
from app.schemas.menu_items import MenuItemCreate, MenuItemUpdate
from app.services import categories
from app.services.common import commit


def get(db: Session, tenant_id: int, item_id: int) -> Menu_Items:
    item = db.scalar(select(Menu_Items).where(Menu_Items.id == item_id, Menu_Items.tenant_id == tenant_id))
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return item


def list_for_tenant(db: Session, tenant_id: int) -> list[Menu_Items]:
    return list(db.scalars(select(Menu_Items).where(Menu_Items.tenant_id == tenant_id).order_by(Menu_Items.sort_order, Menu_Items.id)))


def create(db: Session, tenant_id: int, data: MenuItemCreate) -> Menu_Items:
    if data.tenant_id != tenant_id:
        raise HTTPException(status_code=422, detail="Body tenant_id must match the URL")
    categories.get(db, tenant_id, data.category_id)
    item = Menu_Items(**data.model_dump())
    db.add(item)
    commit(db)
    db.refresh(item)
    return item


def update(db: Session, tenant_id: int, item: Menu_Items, data: MenuItemUpdate) -> Menu_Items:
    values = data.model_dump(exclude_unset=True)
    if "category_id" in values:
        categories.get(db, tenant_id, values["category_id"])
    for key, value in values.items():
        setattr(item, key, value)
    commit(db)
    db.refresh(item)
    return item


def delete(db: Session, item: Menu_Items) -> None:
    db.delete(item)
    commit(db)
