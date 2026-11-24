from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.categories import Category
from app.models.menu_items import Menu_Items
from app.schemas.categories import CategoryCreate, CategoryUpdate
from app.services.common import commit


def get(db: Session, tenant_id: int, category_id: int) -> Category:
    category = db.scalar(select(Category).where(Category.id == category_id, Category.tenant_id == tenant_id))
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


def list_for_tenant(db: Session, tenant_id: int) -> list[Category]:
    return list(db.scalars(select(Category).where(Category.tenant_id == tenant_id).order_by(Category.sort_order, Category.id)))


def create(db: Session, tenant_id: int, data: CategoryCreate) -> Category:
    if data.tenant_id != tenant_id:
        raise HTTPException(status_code=422, detail="Body tenant_id must match the URL")
    category = Category(**data.model_dump())
    db.add(category)
    commit(db)
    db.refresh(category)
    return category


def update(db: Session, category: Category, data: CategoryUpdate) -> Category:
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(category, key, value)
    commit(db)
    db.refresh(category)
    return category


def delete(db: Session, category: Category) -> None:
    if db.scalar(select(Menu_Items.id).where(Menu_Items.category_id == category.id).limit(1)) is not None:
        raise HTTPException(status_code=409, detail="Delete or move this category's menu items first")
    db.delete(category)
    commit(db)
