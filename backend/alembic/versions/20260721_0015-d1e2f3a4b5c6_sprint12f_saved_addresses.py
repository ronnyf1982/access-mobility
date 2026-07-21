"""sprint12f: passenger saved addresses

Revision ID: d1e2f3a4b5c6
Revises: c0d1e2f3a4b5
Create Date: 2026-07-21
"""
import sqlalchemy as sa
from alembic import op

revision = "d1e2f3a4b5c6"
down_revision = "c0d1e2f3a4b5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Idempotenz: Enum-Typ ggf. zuerst entfernen
    op.execute(sa.text("DROP TYPE IF EXISTS addresstype CASCADE"))

    op.create_table(
        "passenger_saved_addresses",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("mobility_profile_id", sa.UUID(), nullable=False),
        sa.Column("label", sa.String(200), nullable=False),
        sa.Column(
            "address_type",
            sa.Enum(
                "home", "school", "work_workshop", "daycare", "doctor", "other",
                name="addresstype",
            ),
            nullable=False,
            server_default="other",
        ),
        sa.Column("street_address", sa.String(500), nullable=False),
        sa.Column("postal_code", sa.String(20), nullable=False),
        sa.Column("city", sa.String(200), nullable=False),
        sa.Column("additional_info", sa.String(500), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("is_default_pickup", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_default_destination", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["mobility_profile_id"], ["mobility_profiles.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_passenger_saved_addresses_profile_id",
        "passenger_saved_addresses",
        ["mobility_profile_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_passenger_saved_addresses_profile_id",
        table_name="passenger_saved_addresses",
    )
    op.drop_table("passenger_saved_addresses")
    op.execute(sa.text("DROP TYPE IF EXISTS addresstype CASCADE"))
