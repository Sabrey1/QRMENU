"""Create the first account in an empty database from a local terminal."""

from getpass import getpass

from pydantic import ValidationError
from sqlalchemy import select

from app.database import SessionLocal
from app.models.users import User
from app.schemas.auth import RegisterRequest
from app.services import auth


def bootstrap_first_user(db, data):
    if db.scalar(select(User.id).limit(1)) is not None:
        raise ValueError("The database already contains a user; sign in to register another account.")
    return auth.register(db, data)


def main():
    print("Create the first shop owner. This only works when no users exist.")
    name = input("Name: ").strip()
    email = input("Email: ").strip()
    currency = input("Currency code [KHR]: ").strip().upper() or "KHR"
    password = getpass("Password: ")
    if password != getpass("Confirm password: "):
        raise SystemExit("Passwords do not match.")
    try:
        data = RegisterRequest(name=name, email=email, password=password, currency_code=currency)
        with SessionLocal() as db:
            _, tenant = bootstrap_first_user(db, data)
            print(f"Created owner and shop: {tenant.name} ({tenant.slug}).")
    except (ValueError, ValidationError) as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
