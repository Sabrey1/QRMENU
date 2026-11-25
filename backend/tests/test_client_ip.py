import os
import unittest

os.environ.setdefault("DB_USER", "test_user")
os.environ.setdefault("DB_PASSWORD", "test_password")

from fastapi.testclient import TestClient
from starlette.requests import Request

from app.config import settings
from app.security import client_ip
from main import app


def request_from(peer, headers=None):
    raw_headers = [(key.lower().encode(), value.encode()) for key, value in (headers or {}).items()]
    return Request(
        {
            "type": "http",
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": "/",
            "raw_path": b"/",
            "query_string": b"",
            "root_path": "",
            "headers": raw_headers,
            "client": (peer, 1234),
            "server": ("testserver", 80),
        }
    )


class ClientIpTests(unittest.TestCase):
    def setUp(self):
        self.previous_trusted = settings.trusted_proxy_ips
        self.previous_login_limit = settings.rate_limit_login_per_minute

    def tearDown(self):
        settings.trusted_proxy_ips = self.previous_trusted
        settings.rate_limit_login_per_minute = self.previous_login_limit

    def test_untrusted_peer_ignores_forwarded_headers(self):
        settings.trusted_proxy_ips = "173.245.48.0/20"
        request = request_from(
            "198.51.100.10",
            {"X-Forwarded-For": "1.2.3.4", "CF-Connecting-IP": "5.6.7.8"},
        )
        self.assertEqual(client_ip(request), "198.51.100.10")

    def test_trusted_peer_uses_cf_connecting_ip(self):
        settings.trusted_proxy_ips = "173.245.48.0/20"
        request = request_from(
            "173.245.48.5",
            {"CF-Connecting-IP": "203.0.113.7", "X-Forwarded-For": "1.2.3.4"},
        )
        self.assertEqual(client_ip(request), "203.0.113.7")

    def test_trusted_peer_falls_back_to_rightmost_xff(self):
        settings.trusted_proxy_ips = "173.245.48.0/20"
        request = request_from("173.245.48.5", {"X-Forwarded-For": "1.2.3.4, 203.0.113.9"})
        self.assertEqual(client_ip(request), "203.0.113.9")

    def test_trusted_peer_invalid_cf_header_falls_back(self):
        settings.trusted_proxy_ips = "173.245.48.0/20"
        request = request_from(
            "173.245.48.5",
            {"CF-Connecting-IP": "not-an-ip", "X-Forwarded-For": "203.0.113.9"},
        )
        self.assertEqual(client_ip(request), "203.0.113.9")

    def test_no_trusted_proxies_configured_ignores_headers(self):
        settings.trusted_proxy_ips = ""
        request = request_from("173.245.48.5", {"CF-Connecting-IP": "203.0.113.7"})
        self.assertEqual(client_ip(request), "173.245.48.5")

    def test_rate_limit_uses_trusted_client_ip(self):
        settings.trusted_proxy_ips = "173.245.48.0/20"
        settings.rate_limit_login_per_minute = 2
        with TestClient(app, client=("173.245.48.5", 5000)) as client:
            for _ in range(2):
                response = client.post(
                    "/v1/api/auth/login",
                    json={},
                    headers={"CF-Connecting-IP": "203.0.113.1"},
                )
                self.assertEqual(response.status_code, 422)
            self.assertEqual(
                client.post(
                    "/v1/api/auth/login",
                    json={},
                    headers={"CF-Connecting-IP": "203.0.113.1"},
                ).status_code,
                429,
            )
            self.assertEqual(
                client.post(
                    "/v1/api/auth/login",
                    json={},
                    headers={"CF-Connecting-IP": "203.0.113.2"},
                ).status_code,
                422,
            )


if __name__ == "__main__":
    unittest.main()
