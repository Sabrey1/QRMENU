import os
import ssl
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("DB_USER", "test_user")
os.environ.setdefault("DB_PASSWORD", "test_password")

from app.config import BASE_DIR
from app.database import build_connect_args


def config(*, enabled=False, ca_file=None, ca_pem=""):
    return SimpleNamespace(db_ssl_enabled=enabled, db_ssl_ca_file=ca_file, db_ssl_ca_pem=ca_pem)


class DatabaseTlsTests(unittest.TestCase):
    def test_default_context_verifies_certificates_and_hostnames(self):
        context = build_connect_args(config(enabled=True))["ssl"]
        self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)
        self.assertTrue(context.check_hostname)

    def test_relative_ca_file_is_resolved_from_backend(self):
        with patch("app.database.ssl.create_default_context") as create_context:
            build_connect_args(config(enabled=True, ca_file=Path("certs/aiven-ca.pem")))
        create_context.assert_called_once_with(cafile=str(BASE_DIR / "certs/aiven-ca.pem"), cadata=None)

    def test_pem_is_passed_to_ssl_context(self):
        with patch("app.database.ssl.create_default_context") as create_context:
            build_connect_args(config(enabled=True, ca_pem="test-pem"))
        create_context.assert_called_once_with(cafile=None, cadata="test-pem")

    def test_ca_cannot_silently_be_ignored_or_ambiguous(self):
        with self.assertRaisesRegex(ValueError, "DB_SSL_ENABLED"):
            build_connect_args(config(ca_file=Path("ca.pem")))
        with self.assertRaisesRegex(ValueError, "either"):
            build_connect_args(config(enabled=True, ca_file=Path("ca.pem"), ca_pem="test-pem"))
        self.assertEqual(build_connect_args(config()), {})
