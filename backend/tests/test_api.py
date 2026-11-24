import os
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import jwt
os.environ.setdefault("DB_USER", "test_user")
os.environ.setdefault("DB_PASSWORD", "test_password")

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.database import Base, get_db
from app.models.users import User
from app.schemas.auth import RegisterRequest
from app.services import auth
from bootstrap_user import bootstrap_first_user
from main import app, create_app


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.original_secret = settings.secret_key
        settings.secret_key = "test-signing-key-with-at-least-32-characters"
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)

        @event.listens_for(self.engine, "connect")
        def enable_foreign_keys(connection, _):
            connection.execute("PRAGMA foreign_keys=ON")

        Base.metadata.create_all(self.engine)
        sessions = sessionmaker(bind=self.engine)
        with sessions() as session:
            bootstrap_first_user(session, RegisterRequest(name="Bootstrap", email="bootstrap@example.com", password="password123"))
            token = auth.login(session, "bootstrap@example.com", "password123")
        self.bootstrap = {"Authorization": "Bearer " + token}

        def override_db():
            with sessions() as session:
                yield session

        app.dependency_overrides[get_db] = override_db
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        self.engine.dispose()
        settings.secret_key = self.original_secret

    def register_and_login(self, email):
        response = self.client.post("/api/auth/register", headers=self.bootstrap, json={"name": "Test", "email": email, "password": "password123"})
        self.assertEqual(response.status_code, 201, response.text)
        self.assertNotIn("password_hash", response.json())
        user_id = response.json()["id"]
        response = self.client.post("/api/auth/login", json={"email": email, "password": "password123"})
        self.assertEqual(response.status_code, 200, response.text)
        return user_id, {"Authorization": "Bearer " + response.json()["access_token"]}

    def test_all_write_methods_require_a_valid_login(self):
        guarded_app = create_app()
        guarded_app.dependency_overrides[get_db] = app.dependency_overrides[get_db]

        @guarded_app.api_route("/test-write", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
        def test_write():
            return {"ok": True}

        with TestClient(guarded_app, client=("198.51.100.52", 5000)) as client:
            self.assertEqual(client.get("/test-write").status_code, 200)
            now = datetime.now(timezone.utc)
            expired = jwt.encode({"sub": "1", "iat": now - timedelta(hours=2), "exp": now - timedelta(hours=1)}, settings.secret_key, algorithm="HS256")
            for method in ("POST", "PUT", "PATCH", "DELETE"):
                with self.subTest(method=method):
                    response = client.request(method, "/test-write")
                    self.assertEqual(response.status_code, 401)
                    self.assertEqual(response.headers["www-authenticate"], "Bearer")
                    self.assertEqual(client.request(method, "/test-write", headers={"Authorization": "Bearer invalid"}).status_code, 401)
                    self.assertEqual(client.request(method, "/test-write", headers={"Authorization": f"Bearer {expired}"}).status_code, 401)
                    self.assertEqual(client.request(method, "/test-write", headers=self.bootstrap).status_code, 200)
            for prefix in ("/api", "/v1/api"):
                self.assertEqual(client.post(prefix + "/auth/register", json={}).status_code, 401)
                self.assertEqual(client.post(prefix + "/auth/register", headers=self.bootstrap, json={}).status_code, 422)
                self.assertEqual(client.post(prefix + "/auth/login", json={}).status_code, 422)

    def test_bootstrap_rejects_databases_that_already_have_a_user(self):
        with sessionmaker(bind=self.engine)() as session:
            with self.assertRaisesRegex(ValueError, "already contains a user"):
                bootstrap_first_user(session, RegisterRequest(name="Other", email="other@example.com", password="password123"))

    def test_tenant_menu_and_public_visibility(self):
        _, owner = self.register_and_login("owner@example.com")
        self.assertEqual(self.client.get("/api/tenants").status_code, 401)
        self.assertEqual(self.client.post("/api/auth/login", json={"email": "owner@example.com", "password": "wrong"}).status_code, 401)
        tenant = self.client.post("/api/tenants", headers=owner, json={"name": "Shop", "slug": "shop", "currency_code": "THB"})
        self.assertEqual(tenant.status_code, 201, tenant.text)
        tenant_id = tenant.json()["id"]
        self.assertEqual(tenant.json()["display_template"], "default_template")
        base = f"/api/tenants/{tenant_id}"
        category = self.client.post(base + "/categories", headers=owner, json={"tenant_id": tenant_id, "name": "Drinks"})
        self.assertEqual(category.status_code, 201, category.text)
        category_id = category.json()["id"]
        item = self.client.post(base + "/menu-items", headers=owner, json={"tenant_id": tenant_id, "category_id": category_id, "name": "Tea", "price": "35.00"})
        self.assertEqual(item.status_code, 201, item.text)
        item_id = item.json()["id"]
        public = self.client.get("/api/public/menus/shop")
        self.assertEqual(public.status_code, 200, public.text)
        self.assertEqual(public.json()["display_template"], "default_template")
        self.assertEqual(public.json()["categories"][0]["items"][0]["name"], "Tea")
        versioned = self.client.get("/v1/api/public/menus/shop")
        self.assertEqual(versioned.status_code, 200, versioned.text)
        self.assertEqual(versioned.json(), public.json())
        changed = self.client.patch(base, headers=owner, json={"display_template": "modern_template"})
        self.assertEqual(changed.status_code, 200, changed.text)
        self.assertEqual(changed.json()["display_template"], "modern_template")
        self.assertEqual(self.client.get("/v1/api/public/menus/shop").json()["display_template"], "modern_template")
        self.assertEqual(self.client.patch(base, headers=owner, json={"display_template": None}).status_code, 422)
        self.assertEqual(self.client.patch(base, headers=owner, json={"display_template": "../invalid"}).status_code, 422)
        self.assertEqual(self.client.get(f"/v1/api/tenants/{tenant_id}/menu-items", headers=owner).status_code, 200)
        self.assertEqual(self.client.get(f"/v1/api/tenants/{tenant_id}/menu-items").status_code, 401)
        self.assertEqual(self.client.delete(base + f"/categories/{category_id}", headers=owner).status_code, 409)
        self.assertEqual(self.client.patch(base + f"/menu-items/{item_id}", headers=owner, json={"is_available": False}).status_code, 200)
        self.assertEqual(self.client.get("/api/public/menus/shop").json()["categories"][0]["items"], [])
        self.assertEqual(self.client.patch(base, headers=owner, json={"is_published": False}).status_code, 200)
        self.assertEqual(self.client.get("/api/public/menus/shop").status_code, 404)
        self.assertEqual(self.client.get("/v1/api/public/menus/shop").status_code, 404)
        self.assertEqual(self.client.delete(base + f"/menu-items/{item_id}", headers=owner).status_code, 204)
        self.assertEqual(self.client.delete(base + f"/categories/{category_id}", headers=owner).status_code, 204)

    def test_tenant_isolation_and_roles(self):
        _, owner = self.register_and_login("owner@example.com")
        member_id, member = self.register_and_login("member@example.com")
        _, other = self.register_and_login("other@example.com")
        tenant = self.client.post("/api/tenants", headers=owner, json={"name": "A", "slug": "a", "currency_code": "THB"}).json()
        other_tenant = self.client.post("/api/tenants", headers=other, json={"name": "B", "slug": "b", "currency_code": "THB"}).json()
        base = f"/api/tenants/{tenant['id']}"
        self.assertEqual(self.client.get(base, headers=member).status_code, 404)
        membership = self.client.post(base + "/members", headers=owner, json={"tenant_id": tenant["id"], "user_id": member_id, "role": "member"})
        self.assertEqual(membership.status_code, 201, membership.text)
        self.assertEqual(self.client.patch(base, headers=member, json={"display_template": "other"}).status_code, 403)
        banner_body = {"image_url": "https://example.com/banner.jpg", "alt_text": "Shop banner"}
        self.assertEqual(self.client.post(base + "/banners", headers=member, json=banner_body).status_code, 403)
        banner = self.client.post(base + "/banners", headers=owner, json=banner_body)
        self.assertEqual(banner.status_code, 201, banner.text)
        banner_id = banner.json()["id"]
        self.assertEqual(self.client.get("/v1/api/public/menus/a").json()["banners"][0]["id"], banner_id)
        self.assertEqual(self.client.patch(f"/api/tenants/{other_tenant['id']}/banners/{banner_id}", headers=other, json={"is_active": False}).status_code, 404)
        self.assertEqual(self.client.patch(base + f"/banners/{banner_id}", headers=owner, json={"is_active": False}).status_code, 200)
        self.assertEqual(self.client.get("/v1/api/public/menus/a").json()["banners"], [])
        self.assertEqual(self.client.post(base + "/banners", headers=owner, json={"image_url": "javascript:alert(1)"}).status_code, 422)
        self.assertEqual(self.client.delete(base + f"/banners/{banner_id}", headers=owner).status_code, 204)
        self.assertEqual(self.client.get(base + "/categories", headers=member).status_code, 200)
        self.assertEqual(self.client.post(base + "/categories", headers=member, json={"tenant_id": tenant["id"], "name": "No"}).status_code, 403)
        self.assertEqual(self.client.get(base + "/members", headers=member).status_code, 403)
        foreign_category = self.client.post(f"/api/tenants/{other_tenant['id']}/categories", headers=other, json={"tenant_id": other_tenant["id"], "name": "Other"}).json()
        response = self.client.post(base + "/menu-items", headers=owner, json={"tenant_id": tenant["id"], "category_id": foreign_category["id"], "name": "No", "price": "10.00"})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.client.patch(base + f"/members/{membership.json()['id']}", headers=owner, json={"role": "owner"}).status_code, 422)
        self.assertEqual(self.client.delete(base + f"/members/{membership.json()['id']}", headers=owner).status_code, 204)
        self.assertEqual(self.client.get(base, headers=member).status_code, 404)

    def test_generated_shop_domains(self):
        _, owner = self.register_and_login("domains@example.com")
        body = {"name": "My Cafe", "currency_code": "THB"}
        first = self.client.post("/v1/api/tenants", headers=owner, json=body)
        second = self.client.post("/v1/api/tenants", headers=owner, json=body)
        self.assertEqual(first.status_code, 201, first.text)
        self.assertEqual(first.json()["slug"], "my-cafe")
        self.assertEqual(first.json()["menu_url"], "https://my-cafe.sabrey.xyz")
        self.assertEqual(second.json()["slug"], "my-cafe-2")
        menu = self.client.get("/v1/api/public/menu", headers={"Host": "my-cafe.sabrey.xyz"})
        self.assertEqual(menu.status_code, 200, menu.text)
        self.assertEqual(menu.json()["name"], "My Cafe")
        self.assertEqual(self.client.get("/", headers={"Host": "my-cafe.sabrey.xyz"}).json()["name"], "My Cafe")
        self.assertEqual(self.client.get("/v1/api/public/menu", headers={"Host": "my-cafe.sabrey.xyz.evil.com"}).status_code, 404)
        self.assertEqual(self.client.get("/v1/api/public/menu", headers={"Host": "missing.sabrey.xyz"}).status_code, 404)
        self.assertEqual(self.client.post("/v1/api/tenants", headers=owner, json={**body, "slug": "api"}).status_code, 422)
        self.assertEqual(self.client.post("/v1/api/tenants", headers=owner, json={**body, "slug": "my-cafe"}).status_code, 409)
        tenant_id = first.json()["id"]
        self.assertEqual(self.client.patch(f"/v1/api/tenants/{tenant_id}", headers=owner, json={"is_published": False}).status_code, 200)
        self.assertEqual(self.client.get("/", headers={"Host": "my-cafe.sabrey.xyz"}).status_code, 404)

    def test_registration_creates_shop_and_qr_uses_public_domain(self):
        with TestClient(app, client=("198.51.100.50", 5000)) as client:
            body = {"name": "Sabrey", "email": "sabrey@example.com", "password": "password123"}
            first = client.post("/v1/api/auth/register", headers=self.bootstrap, json=body)
            self.assertEqual(first.status_code, 201, first.text)
            tenant = first.json()["tenant"]
            self.assertEqual(tenant["slug"], "sabrey")
            self.assertEqual(tenant["menu_url"], "https://sabrey.sabrey.xyz")
            self.assertEqual(tenant["currency_code"], "KHR")
            self.assertNotIn("password_hash", first.json())
            second = client.post("/v1/api/auth/register", headers=self.bootstrap, json={**body, "email": "other@example.com", "currency_code": "USD"})
            self.assertEqual(second.status_code, 201, second.text)
            self.assertEqual(second.json()["tenant"]["slug"], "sabrey-2")
            self.assertEqual(second.json()["tenant"]["currency_code"], "USD")
            login = client.post("/v1/api/auth/login", json={"email": body["email"], "password": body["password"]})
            self.assertEqual(login.status_code, 200, login.text)
            headers = {"Authorization": "Bearer " + login.json()["access_token"]}
            self.assertEqual(client.get("/v1/api/tenants", headers=headers).json()[0]["id"], tenant["id"])
            self.assertEqual(client.get("/v1/api/public/menu", headers={"Host": "sabrey.sabrey.xyz"}).status_code, 200)
            self.assertEqual(client.get(f"/v1/api/tenants/{tenant['id']}/qr-code").status_code, 401)
            with patch("app.api.v1.routers.tenants.qrcode.make", wraps=__import__("qrcode").make) as make_qr:
                qr = client.get(f"/v1/api/tenants/{tenant['id']}/qr-code", headers=headers)
            self.assertEqual(qr.status_code, 200)
            self.assertEqual(qr.headers["content-type"], "image/svg+xml")
            self.assertIn(b"<svg", qr.content)
            self.assertEqual(make_qr.call_args.args[0], "https://sabrey.sabrey.xyz")
            self.assertEqual(client.get(f"/v1/api/tenants/{second.json()['tenant']['id']}/qr-code", headers=headers).status_code, 404)
            self.assertEqual(client.post("/v1/api/auth/register", headers=self.bootstrap, json=body).status_code, 409)

    def test_registration_rolls_back_user_when_shop_creation_fails(self):
        with TestClient(app, client=("198.51.100.51", 5000)) as client:
            with patch("app.services.auth.add_for_owner", side_effect=IntegrityError("insert", {}, Exception("conflict"))):
                response = client.post("/v1/api/auth/register", headers=self.bootstrap, json={"name": "Failed Shop", "email": "failed@example.com", "password": "password123"})
            self.assertEqual(response.status_code, 409)
        with sessionmaker(bind=self.engine)() as session:
            self.assertIsNone(session.scalar(select(User).where(User.email == "failed@example.com")))


if __name__ == "__main__":
    unittest.main()
