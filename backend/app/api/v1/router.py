"""Collect all version 1 routes in one router."""

from fastapi import APIRouter

from app.api.v1.routers import auth, banners, categories, menu_items, public, tenant_members, tenants

router = APIRouter()
router.include_router(public.routers)
router.include_router(auth.router)
router.include_router(banners.router)
router.include_router(tenants.router)
router.include_router(tenant_members.router)
router.include_router(categories.router)
router.include_router(menu_items.router)
