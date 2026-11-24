"""Enforce unique shop slugs, including during concurrent creation.

Revision ID: 002_unique_tenant_slug
Revises: 001_initial_models
"""

from alembic import op

revision = "002_unique_tenant_slug"
down_revision = "001_initial_models"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Existing duplicate slugs must be resolved before applying this migration.
    op.create_unique_constraint("uq_tenants_slug", "tenants", ["slug"])


def downgrade() -> None:
    op.drop_constraint("uq_tenants_slug", "tenants", type_="unique")
