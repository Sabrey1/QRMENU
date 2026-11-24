"""Check the configured MySQL connection: python test_connection.py."""

import sys

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database import engine


def main() -> int:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        print(f"Database connection failed: {exc}", file=sys.stderr)
        return 1
    finally:
        engine.dispose()

    print("Database connection successful.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
