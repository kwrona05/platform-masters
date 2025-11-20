"""add admin reset codes

Revision ID: 0002_admin_reset_codes
Revises: 0001_initial
Create Date: 2024-11-20 10:40:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0002_admin_reset_codes"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "admin_reset_codes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=12), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("used", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_admin_reset_codes_id", "admin_reset_codes", ["id"], unique=False)
    op.create_index("ix_admin_reset_codes_user_id", "admin_reset_codes", ["user_id"], unique=False)
    op.create_index("ix_admin_reset_codes_code", "admin_reset_codes", ["code"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_admin_reset_codes_code", table_name="admin_reset_codes")
    op.drop_index("ix_admin_reset_codes_user_id", table_name="admin_reset_codes")
    op.drop_index("ix_admin_reset_codes_id", table_name="admin_reset_codes")
    op.drop_table("admin_reset_codes")
