"""Add the tenant's selected display template.

Revision ID: 004_tenant_display_template
Revises: 003_banners
"""

from alembic import op
import sqlalchemy as sa

revision = "004_tenant_display_template"
down_revision = "003_banners"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tenants", sa.Column("display_template", sa.String(100), nullable=False, server_default="default_template"))


def downgrade() -> None:
    op.drop_column("tenants", "display_template")
