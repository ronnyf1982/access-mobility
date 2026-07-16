"""sprint10b: add default_vehicle_id to driver_profiles

Revision ID: d5e6f7a8b9c0
Revises: c4d5e6f7a8b9
Create Date: 2026-07-16
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "d5e6f7a8b9c0"
down_revision = "c4d5e6f7a8b9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "driver_profiles",
        sa.Column(
            "default_vehicle_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("vehicles.id"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("driver_profiles", "default_vehicle_id")
