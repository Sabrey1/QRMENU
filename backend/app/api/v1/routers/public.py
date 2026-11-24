from fastapi import APIRouter, HTTPException, Request

from app.dependencies import Db
from app.schemas.public import PublicMenu
from app.services import public

routers = APIRouter(prefix="/api/public", tags=["Public Menu"])


def slug_from_request(request: Request) -> str | None:
    hostname = (request.url.hostname or "").lower().rstrip(".")
    suffix = ".sabrey.xyz"
    if not hostname.endswith(suffix):
        return None
    slug = hostname[:-len(suffix)]
    if not slug or "." in slug:
        return None
    return slug


@routers.get("/menu", response_model=PublicMenu)
def get_menu_for_domain(request: Request, db: Db):
    slug = slug_from_request(request)
    if not slug:
        raise HTTPException(status_code=404, detail="Menu not found")
    return public.get_menu(db, slug)


@routers.get("/menus/{shop_slug}", response_model=PublicMenu)
def get_menu(shop_slug: str, db: Db):
    return public.get_menu(db, shop_slug)
