"""add user verification flags and codes

Revision ID: 0003_user_verification_and_flags
Revises: 0002_admin_reset_codes
Create Date: 2025-03-11 12:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0003_user_verification_and_flags"
down_revision = "0002_admin_reset_codes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("nickname", sa.String(length=50), nullable=True))
    op.add_column(
        "users",
        sa.Column("is_email_confirmed", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
    )
    op.add_column(
        "users",
        sa.Column("is_verified_account", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
    )
    op.add_column(
        "users",
        sa.Column("is_banned", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
    )
    op.add_column("users", sa.Column("first_name", sa.String(length=100), nullable=True))
    op.add_column("users", sa.Column("last_name", sa.String(length=100), nullable=True))
    op.add_column("users", sa.Column("bank_account", sa.String(length=34), nullable=True))
    op.add_column("users", sa.Column("billing_address", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("pesel", sa.String(length=20), nullable=True))
    op.add_column("users", sa.Column("kyc_submitted_at", sa.DateTime(), nullable=True))
    op.add_column("users", sa.Column("kyc_verified_at", sa.DateTime(), nullable=True))

    users_table = sa.Table(
        "users",
        sa.MetaData(),
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("nickname", sa.String(50)),
    )
    conn = op.get_bind()
    rows = conn.execute(sa.select(users_table.c.id)).fetchall()
    for row in rows:
        conn.execute(
            sa.update(users_table)
            .where(users_table.c.id == row.id)
            .values(nickname=f"user{row.id}")
        )

    with op.batch_alter_table("users") as batch:
        batch.alter_column("nickname", existing_type=sa.String(length=50), nullable=False)
        batch.create_index(op.f("ix_users_nickname"), ["nickname"], unique=True)

    op.create_table(
        "user_verification_codes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=12), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("used", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_user_verification_codes_user_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_user_verification_codes_id"),
        "user_verification_codes",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_verification_codes_user_id"),
        "user_verification_codes",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_verification_codes_code"),
        "user_verification_codes",
        ["code"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_user_verification_codes_code"), table_name="user_verification_codes")
    op.drop_index(op.f("ix_user_verification_codes_user_id"), table_name="user_verification_codes")
    op.drop_index(op.f("ix_user_verification_codes_id"), table_name="user_verification_codes")
    op.drop_table("user_verification_codes")
    op.drop_index(op.f("ix_users_nickname"), table_name="users")
    op.drop_column("users", "kyc_verified_at")
    op.drop_column("users", "kyc_submitted_at")
    op.drop_column("users", "pesel")
    op.drop_column("users", "billing_address")
    op.drop_column("users", "bank_account")
    op.drop_column("users", "last_name")
    op.drop_column("users", "first_name")
    op.drop_column("users", "is_banned")
    op.drop_column("users", "is_verified_account")
    op.drop_column("users", "is_email_confirmed")
    op.drop_column("users", "nickname")
