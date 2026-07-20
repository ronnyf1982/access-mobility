"""sprint12b: add current_latitude/longitude to driver_shifts

Revision ID: a8b9c0d1e2f3
Revises: f7a8b9c0d1e2
Create Date: 2026-07-20
"""
import sqlalchemy as sa
from alembic import op

revision = "a8b9c0d1e2f3"
down_revision = "f7a8b9c0d1e2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("driver_shifts", sa.Column("current_latitude", sa.Float(), nullable=True))
    op.add_column("driver_shifts", sa.Column("current_longitude", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("driver_shifts", "current_longitude")
    op.drop_column("driver_shifts", "current_latitude")
