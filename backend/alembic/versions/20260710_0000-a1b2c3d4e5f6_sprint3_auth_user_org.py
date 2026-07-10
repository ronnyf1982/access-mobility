"""sprint3 auth user org

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-07-10 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column(
            "role",
            sa.Enum(
                "passenger",
                "trusted_person",
                "organization_admin",
                "organization_coordinator",
                "provider_admin",
                "dispatcher",
                "driver",
                "platform_admin",
                name="userrole",
            ),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "organizations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column(
            "type",
            sa.Enum(
                "employer",
                "school",
                "facility",
                "medical_practice",
                "insurer",
                "transport_provider",
                "other",
                name="organizationtype",
            ),
            nullable=False,
        ),
        sa.Column("contact_email", sa.String(255), nullable=True),
        sa.Column("contact_phone", sa.String(50), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "organization_memberships",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("organization_id", sa.UUID(), nullable=False),
        sa.Column("organization_role", sa.String(100), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "trusted_relationships",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("passenger_user_id", sa.UUID(), nullable=False),
        sa.Column("trusted_user_id", sa.UUID(), nullable=False),
        sa.Column("can_book_rides", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("can_view_rides", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("can_manage_profile", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "active", "revoked", name="truststatus"),
            server_default="pending",
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["passenger_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["trusted_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("trusted_relationships")
    op.drop_table("organization_memberships")
    op.drop_table("organizations")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    sa.Enum(name="truststatus").drop(op.get_bind())
    sa.Enum(name="organizationtype").drop(op.get_bind())
    sa.Enum(name="userrole").drop(op.get_bind())
