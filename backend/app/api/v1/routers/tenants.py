from fastapi import APIRouter, HTTPException, Response, status
import qrcode
from qrcode.image.svg import SvgPathFillImage

from app.dependencies import CurrentUser, Db
from app.schemas.tenants import TenantCreate, TenantRead, TenantUpdate
from app.services import tenants

router = APIRouter(prefix="/api/tenants", tags=["Tenants"])


@router.post("", response_model=TenantRead, status_code=status.HTTP_201_CREATED)
def create_tenant(data: TenantCreate, db: Db, user: CurrentUser):
    return tenants.create(db, data, user)


@router.get("", response_model=list[TenantRead])
def list_tenants(db: Db, user: CurrentUser):
    return tenants.list_for_user(db, user)


@router.get("/{tenant_id}", response_model=TenantRead)
def get_tenant(tenant_id: int, db: Db, user: CurrentUser):
    return tenants.require_membership(db, tenant_id, user)


@router.get("/{tenant_id}/qr-code", response_class=Response, responses={200: {"content": {"image/svg+xml": {}}}})
def get_menu_qr_code(tenant_id: int, db: Db, user: CurrentUser):
    tenant = tenants.require_membership(db, tenant_id, user)
    menu_url = TenantRead.model_validate(tenant).menu_url
    if not menu_url:
        raise HTTPException(status_code=422, detail="The shop needs a valid slug before a QR code can be generated")
    image = qrcode.make(menu_url, image_factory=SvgPathFillImage, border=4, box_size=10)
    return Response(content=image.to_string(), media_type="image/svg+xml", headers={"Cache-Control": "private, no-store"})


@router.patch("/{tenant_id}", response_model=TenantRead)
def update_tenant(tenant_id: int, data: TenantUpdate, db: Db, user: CurrentUser):
    return tenants.update(db, tenants.require_membership(db, tenant_id, user, manage=True), data)
