"""sprint12c: spontaneous booking — new status values + transport_request columns

Revision ID: b9c0d1e2f3a4
Revises: a8b9c0d1e2f3
Create Date: 2026-07-20
"""
import sqlalchemy as sa
from alembic import op

revision = "b9c0d1e2f3a4"
down_revision = "a8b9c0d1e2f3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(sa.text("ALTER TYPE transportrequeststatus ADD VALUE IF NOT EXISTS 'spontaneous_requested'"))
    op.execute(sa.text("ALTER TYPE transportrequeststatus ADD VALUE IF NOT EXISTS 'driver_declined'"))
    op.add_column(
        "transport_requests",
        sa.Column("is_spontaneous", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.add_column("transport_requests", sa.Column("pickup_latitude", sa.Float(), nullable=True))
    op.add_column("transport_requests", sa.Column("pickup_longitude", sa.Float(), nullable=True))
    op.add_column("transport_requests", sa.Column("destination_latitude", sa.Float(), nullable=True))
    op.add_column("transport_requests", sa.Column("destination_longitude", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("transport_requests", "destination_longitude")
    op.drop_column("transport_requests", "destination_latitude")
    op.drop_column("transport_requests", "pickup_longitude")
    op.drop_column("transport_requests", "pickup_latitude")
    op.drop_column("transport_requests", "is_spontaneous")
    # Note: PostgreSQL does not support removing enum values.
    # spontaneous_requested and driver_declined remain in the enum type after downgrade.
