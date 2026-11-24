from decimal import Decimal

from app.schemas.base import Schema


class PublicItem(Schema):
    id: int
    name: str
    description: str | None
    price: Decimal
    image_url: str | None


class PublicCategory(Schema):
    id: int
    name: str
    description: str | None
    items: list[PublicItem]


class PublicBanner(Schema):
    id: int
    image_url: str
    alt_text: str


class PublicMenu(Schema):
    name: str
    slug: str
    logo_url: str | None
    currency_code: str
    display_template: str
    banners: list[PublicBanner] = []
    categories: list[PublicCategory]
