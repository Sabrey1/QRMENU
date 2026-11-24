import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from dotenv import dotenv_values

import configure_aiven


class ConfigureAivenTests(unittest.TestCase):
    def test_saves_quoted_credentials_and_preserves_existing_secret(self):
        with tempfile.TemporaryDirectory() as temp:
            env_file = Path(temp) / ".env"
            env_file.write_text("SECRET_KEY='existing-secret'\nDB_SSL_CA_PEM='old-cert'\n", encoding="utf-8")
            answers = ["example.aivencloud.com", "12345", "defaultdb", "db_user"]
            with patch.object(configure_aiven, "ENV_FILE", env_file), \
                 patch("configure_aiven.ssl.create_default_context"), \
                 patch("builtins.input", side_effect=answers), \
                 patch("configure_aiven.getpass.getpass", return_value="special#'password"), \
                 patch("configure_aiven.subprocess.run") as run, \
                 contextlib.redirect_stdout(io.StringIO()) as output:
                run.return_value.returncode = 0
                self.assertEqual(configure_aiven.main(), 0)
            values = dotenv_values(env_file)
            self.assertEqual(values["DB_HOST"], "example.aivencloud.com")
            self.assertEqual(values["DB_PORT"], "12345")
            self.assertEqual(values["DB_PASSWORD"], "special#'password")
            self.assertEqual(values["DB_SSL_ENABLED"], "true")
            self.assertEqual(values["DB_SSL_CA_FILE"], "certs/aiven-ca.pem")
            self.assertEqual(values["SECRET_KEY"], "existing-secret")
            self.assertNotIn("DB_SSL_CA_PEM", values)
            self.assertNotIn("special#'password", output.getvalue())
            run.assert_called_once()

    def test_missing_password_does_not_change_existing_file(self):
        with tempfile.TemporaryDirectory() as temp:
            env_file = Path(temp) / ".env"
            env_file.write_text("DB_HOST=original\n", encoding="utf-8")
            with patch.object(configure_aiven, "ENV_FILE", env_file), \
                 patch("configure_aiven.ssl.create_default_context"), \
                 patch("builtins.input", side_effect=["example.aivencloud.com", "12345", "db", "user"]), \
                 patch("configure_aiven.getpass.getpass", return_value=""), \
                 contextlib.redirect_stdout(io.StringIO()), \
                 contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(configure_aiven.main(), 1)
            self.assertEqual(env_file.read_text(encoding="utf-8"), "DB_HOST=original\n")
