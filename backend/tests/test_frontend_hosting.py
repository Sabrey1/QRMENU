import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("DB_USER", "test_user")
os.environ.setdefault("DB_PASSWORD", "test_password")

from fastapi.testclient import TestClient

from app.config import settings
from main import create_app


class FrontendHostingTests(unittest.TestCase):
    def test_frontend_and_api_share_shop_hostname(self):
        previous_enabled = settings.serve_frontend
        previous_path = settings.frontend_dist_dir
        try:
            with tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                (root / "assets").mkdir()
                (root / "index.html").write_text("<html>shop frontend</html>", encoding="utf-8")
                (root / "assets" / "app.js").write_text("// asset", encoding="utf-8")
                settings.serve_frontend = True
                settings.frontend_dist_dir = root
                with TestClient(create_app(), client=("198.51.100.60", 5000)) as client:
                    headers = {"Host": "sabrey.sabrey.xyz"}
                    page = client.get("/", headers=headers)
                    self.assertEqual(page.status_code, 200)
                    self.assertIn("shop frontend", page.text)
                    self.assertEqual(client.get("/assets/app.js", headers=headers).status_code, 200)
                    self.assertEqual(client.get("/healthz", headers=headers).json(), {"status": "ok"})
                    self.assertEqual(client.post("/v1/api/auth/login", headers=headers, json={}).status_code, 422)
        finally:
            settings.serve_frontend = previous_enabled
            settings.frontend_dist_dir = previous_path

    def test_missing_build_fails_fast(self):
        previous_enabled = settings.serve_frontend
        previous_path = settings.frontend_dist_dir
        try:
            with tempfile.TemporaryDirectory() as temp:
                settings.serve_frontend = True
                settings.frontend_dist_dir = Path(temp)
                with self.assertRaisesRegex(RuntimeError, "Frontend build missing"):
                    create_app()
        finally:
            settings.serve_frontend = previous_enabled
            settings.frontend_dist_dir = previous_path
