from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.categories import Category
from app.models.banners import Banner
from app.models.menu_items import Menu_Items
from app.models.tenants import Tenant
from app.schemas.public import PublicCategory, PublicItem, PublicMenu


def get_menu(db: Session, slug: str) -> PublicMenu:
    tenants = list(db.scalars(select(Tenant).where(Tenant.slug == slug, Tenant.is_published.is_(True)).limit(2)))
    if not tenants:
        raise HTTPException(status_code=404, detail="Menu not found")
    if len(tenants) > 1:
        raise HTTPException(status_code=409, detail="Menu slug is not unique")
    tenant = tenants[0]
    banners = list(db.scalars(select(Banner).where(Banner.tenant_id == tenant.id, Banner.is_active.is_(True)).order_by(Banner.sort_order, Banner.id)))
    categories = list(db.scalars(select(Category).where(Category.tenant_id == tenant.id, Category.is_active.is_(True)).order_by(Category.sort_order, Category.id)))
    items = list(db.scalars(select(Menu_Items).where(Menu_Items.tenant_id == tenant.id, Menu_Items.is_active.is_(True), Menu_Items.is_available.is_(True)).order_by(Menu_Items.sort_order, Menu_Items.id)))
    grouped: dict[int, list[PublicItem]] = {category.id: [] for category in categories}
    for item in items:
        if item.category_id in grouped:
            grouped[item.category_id].append(PublicItem.model_validate(item))
    return PublicMenu(name=tenant.name, slug=slug, logo_url=tenant.logo_url, currency_code=tenant.currency_code, display_template=tenant.display_template, banners=banners, categories=[PublicCategory(id=category.id, name=category.name, description=category.description, items=grouped[category.id]) for category in categories])
