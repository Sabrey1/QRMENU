"""Interactively configure an Aiven MySQL connection without printing its password."""

import getpass
import os
import secrets
import ssl
import subprocess
import sys
from pathlib import Path

from dotenv import dotenv_values, set_key, unset_key

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"
CA_FILE = BASE_DIR / "certs" / "aiven-ca.pem"


def prompt_required(label: str) -> str:
    while True:
        value = input(f"{label}: ").strip()
        if value:
            return value
        print("This value is required.")


def main() -> int:
    try:
        ssl.create_default_context(cafile=str(CA_FILE))
    except (OSError, ssl.SSLError):
        print("Aiven CA certificate is missing or invalid. Save it as backend/certs/aiven-ca.pem first.", file=sys.stderr)
        return 1

    print("Enter the values from Aiven's MySQL service Overview > Connection information.")
    print("Enter the host only, not the service URI. Your password will not be displayed.")
    try:
        while True:
            host = prompt_required("Host")
            if not any(char.isspace() or char in "/:@" for char in host):
                break
            print("Enter just the hostname, without a URL, port or credentials.")

        while True:
            port = prompt_required("Port")
            if port.isascii() and port.isdecimal() and 1 <= int(port) <= 65535:
                break
            print("Enter a valid port number between 1 and 65535.")

        database = prompt_required("Database name")
        user = prompt_required("Username")
        password = getpass.getpass("Password (hidden): ")
        if not password:
            print("No password entered; configuration was not changed.", file=sys.stderr)
            return 1
    except (EOFError, KeyboardInterrupt):
        print("\nSetup cancelled; configuration was not changed.", file=sys.stderr)
        return 1

    existing = dotenv_values(ENV_FILE) if ENV_FILE.exists() else {}
    values = {
        "DB_HOST": host,
        "DB_PORT": port,
        "DB_NAME": database,
        "DB_USER": user,
        "DB_PASSWORD": password,
        "DB_SSL_ENABLED": "true",
        "DB_SSL_CA_FILE": "certs/aiven-ca.pem",
    }
    if not existing.get("SECRET_KEY"):
        values["SECRET_KEY"] = secrets.token_urlsafe(48)
    for key, value in values.items():
        set_key(str(ENV_FILE), key, value)
    if existing.get("DB_SSL_CA_PEM"):
        unset_key(str(ENV_FILE), "DB_SSL_CA_PEM")

    overridden = [key for key in (*values, "DB_SSL_CA_PEM") if key in os.environ]
    if overridden:
        print("Note: active environment variables override .env: " + ", ".join(overridden))
    print("Configuration saved. Checking the connection...")
    return subprocess.run([sys.executable, str(BASE_DIR / "test_connection.py")], cwd=BASE_DIR, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
