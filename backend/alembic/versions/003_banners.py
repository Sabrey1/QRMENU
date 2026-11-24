"""Add tenant banner images.

Revision ID: 003_banners
Revises: 002_unique_tenant_slug
"""
from alembic import op
import sqlalchemy as sa

revision = "003_banners"
down_revision = "002_unique_tenant_slug"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "banners",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("image_url", sa.String(500), nullable=False),
        sa.Column("alt_text", sa.String(200), server_default="", nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="1", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_banners_tenant_id", "banners", ["tenant_id"])


def downgrade() -> None:
    op.drop_index("ix_banners_tenant_id", table_name="banners")
    op.drop_table("banners")
