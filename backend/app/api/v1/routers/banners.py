from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import select

from app.dependencies import CurrentUser, Db
from app.models.banners import Banner
from app.schemas.banners import BannerCreate, BannerRead, BannerUpdate
from app.services import tenants
from app.services.common import commit

router = APIRouter(prefix="/api/tenants/{tenant_id}/banners", tags=["Banners"])


def get_banner(db, tenant_id: int, banner_id: int) -> Banner:
    banner = db.scalar(select(Banner).where(Banner.tenant_id == tenant_id, Banner.id == banner_id))
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")
    return banner


@router.get("", response_model=list[BannerRead])
def list_banners(tenant_id: int, db: Db, user: CurrentUser):
    tenants.require_membership(db, tenant_id, user)
    return list(db.scalars(select(Banner).where(Banner.tenant_id == tenant_id).order_by(Banner.sort_order, Banner.id)))


@router.post("", response_model=BannerRead, status_code=status.HTTP_201_CREATED)
def create_banner(tenant_id: int, data: BannerCreate, db: Db, user: CurrentUser):
    tenants.require_membership(db, tenant_id, user, manage=True)
    banner = Banner(tenant_id=tenant_id, **data.model_dump())
    db.add(banner)
    commit(db)
    db.refresh(banner)
    return banner


@router.patch("/{banner_id}", response_model=BannerRead)
def update_banner(tenant_id: int, banner_id: int, data: BannerUpdate, db: Db, user: CurrentUser):
    tenants.require_membership(db, tenant_id, user, manage=True)
    banner = get_banner(db, tenant_id, banner_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(banner, key, value)
    commit(db)
    db.refresh(banner)
    return banner


@router.delete("/{banner_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_banner(tenant_id: int, banner_id: int, db: Db, user: CurrentUser):
    tenants.require_membership(db, tenant_id, user, manage=True)
    db.delete(get_banner(db, tenant_id, banner_id))
    commit(db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
