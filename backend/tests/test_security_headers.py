import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("DB_USER", "test_user")
os.environ.setdefault("DB_PASSWORD", "test_password")

from fastapi.testclient import TestClient

from app.config import settings
from main import app, create_app


class SecurityHeaderTests(unittest.TestCase):
    def test_api_responses_carry_security_headers(self):
        with TestClient(app) as client:
            response = client.get("/healthz")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers.get("x-content-type-options"), "nosniff")
            self.assertEqual(response.headers.get("x-frame-options"), "DENY")
            self.assertEqual(response.headers.get("referrer-policy"), "strict-origin-when-cross-origin")
            self.assertIn("camera=()", response.headers.get("permissions-policy", ""))
            self.assertEqual(
                response.headers.get("strict-transport-security"),
                "max-age=31536000; includeSubDomains",
            )
            csp = response.headers.get("content-security-policy", "")
            self.assertIn("default-src 'none'", csp)
            self.assertIn("frame-ancestors 'none'", csp)

    def test_html_frontend_gets_spa_csp(self):
        previous_enabled = settings.serve_frontend
        previous_path = settings.frontend_dist_dir
        try:
            with tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                (root / "assets").mkdir()
                (root / "index.html").write_text("<html>app</html>", encoding="utf-8")
                (root / "assets" / "app.js").write_text("// asset", encoding="utf-8")
                settings.serve_frontend = True
                settings.frontend_dist_dir = root
                with TestClient(create_app()) as client:
                    response = client.get("/", headers={"Host": "shop.sabrey.xyz"})
            self.assertEqual(response.status_code, 200)
            csp = response.headers.get("content-security-policy", "")
            self.assertIn("script-src 'self'", csp)
            self.assertIn("frame-ancestors 'none'", csp)
            self.assertNotIn("default-src 'none'", csp)
        finally:
            settings.serve_frontend = previous_enabled
            settings.frontend_dist_dir = previous_path

    def test_docs_and_openapi_disabled_by_default(self):
        with TestClient(app) as client:
            self.assertEqual(client.get("/openapi.json").status_code, 404)
            self.assertEqual(client.get("/docs").status_code, 404)
            self.assertEqual(client.get("/redoc").status_code, 404)

    def test_docs_can_be_enabled_explicitly(self):
        previous = settings.enable_docs
        try:
            settings.enable_docs = True
            with TestClient(create_app()) as client:
                self.assertEqual(client.get("/openapi.json").status_code, 200)
        finally:
            settings.enable_docs = previous

    def test_auth_endpoints_are_not_cacheable(self):
        with TestClient(app) as client:
            login = client.post("/v1/api/auth/login", json={})
            self.assertEqual(login.status_code, 422)
            self.assertEqual(login.headers.get("cache-control"), "no-store")

            me = client.get("/v1/api/auth/me")
            self.assertEqual(me.status_code, 401)
            self.assertEqual(me.headers.get("cache-control"), "no-store")

    def test_cors_methods_are_explicit(self):
        with TestClient(app) as client:
            preflight = client.options(
                "/v1/api/auth/login",
                headers={
                    "Origin": "https://emenu.sabrey.xyz",
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "authorization,content-type",
                },
            )
            self.assertEqual(preflight.status_code, 200)
            allow = preflight.headers.get("access-control-allow-methods", "")
            self.assertNotIn("*", allow)
            self.assertIn("POST", allow)
            self.assertIn("GET", allow)


if __name__ == "__main__":
    unittest.main()
