import os
import unittest
from unittest.mock import AsyncMock, patch

os.environ.setdefault("DB_USER", "test_user")
os.environ.setdefault("DB_PASSWORD", "test_password")

from fastapi.testclient import TestClient

from main import app


class RateLimitTests(unittest.TestCase):
    def test_cors_allows_emenu_frontend(self):
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
            self.assertEqual(preflight.headers["access-control-allow-origin"], "https://emenu.sabrey.xyz")

            response = client.get("/healthz", headers={"Origin": "https://emenu.sabrey.xyz"})
            self.assertEqual(response.headers["access-control-allow-origin"], "https://emenu.sabrey.xyz")

            other_origin = client.get("/healthz", headers={"Origin": "https://other.example"})
            self.assertNotIn("access-control-allow-origin", other_origin.headers)

    def test_login_limit_covers_both_url_versions_and_ignores_spoofed_headers(self):
        with TestClient(app, client=("198.51.100.10", 5000)) as client:
            for index in range(10):
                path = "/v1/api/auth/login" if index % 2 else "/api/auth/login"
                response = client.post(path, json={}, headers={"X-Forwarded-For": f"203.0.113.{index}"})
                self.assertEqual(response.status_code, 422)
            response = client.post("/v1/api/auth/login", json={}, headers={"X-Forwarded-For": "203.0.113.250"})
            self.assertEqual(response.status_code, 429)
            self.assertGreater(int(response.headers["Retry-After"]), 0)
            self.assertEqual(response.headers["Cache-Control"], "no-store")
        with TestClient(app, client=("198.51.100.11", 5000)) as client:
            self.assertEqual(client.post("/v1/api/auth/login", json={}).status_code, 422)

    def test_registration_limit_covers_both_url_versions(self):
        with TestClient(app, client=("198.51.100.12", 5000)) as client:
            for _ in range(5):
                self.assertEqual(client.post("/api/auth/register", json={}).status_code, 422)
            response = client.post("/v1/api/auth/register", json={})
            self.assertEqual(response.status_code, 429)
            self.assertGreater(int(response.headers["Retry-After"]), 0)

    def test_general_limit(self):
        with TestClient(app, client=("198.51.100.13", 5000)) as client:
            for _ in range(120):
                self.assertEqual(client.get("/v1/api/nonexistent").status_code, 404)
            self.assertEqual(client.get("/api/nonexistent").status_code, 429)

    def test_storage_failure_does_not_disable_limits(self):
        with TestClient(app, client=("198.51.100.14", 5000)) as client:
            with patch("app.rate_limit.limiter.hit", new=AsyncMock(side_effect=RuntimeError("storage unavailable"))):
                response = client.get("/v1/api/nonexistent")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"], "Service temporarily unavailable.")


if __name__ == "__main__":
    unittest.main()
