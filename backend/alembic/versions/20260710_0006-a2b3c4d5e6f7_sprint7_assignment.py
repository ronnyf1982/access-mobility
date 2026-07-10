"""sprint7: add assignment fields + assigned status to transport_requests

Revision ID: a2b3c4d5e6f7
Revises: f6a1b2c3d4e5
Create Date: 2026-07-10
"""
import sqlalchemy as sa
from alembic import op

revision = "a2b3c4d5e6f7"
down_revision = "f6a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ALTER TYPE … ADD VALUE is transactional in PostgreSQL 12+
    op.execute("ALTER TYPE transportrequeststatus ADD VALUE IF NOT EXISTS 'assigned'")

    op.add_column("transport_requests", sa.Column("assigned_vehicle_id", sa.UUID(), nullable=True))
    op.add_column("transport_requests", sa.Column("assigned_driver_profile_id", sa.UUID(), nullable=True))
    op.add_column("transport_requests", sa.Column("assigned_by_user_id", sa.UUID(), nullable=True))
    op.add_column("transport_requests", sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("transport_requests", sa.Column("assignment_notes", sa.Text(), nullable=True))

    op.create_foreign_key(
        "fk_tr_assigned_vehicle_id",
        "transport_requests", "vehicles",
        ["assigned_vehicle_id"], ["id"],
    )
    op.create_foreign_key(
        "fk_tr_assigned_driver_profile_id",
        "transport_requests", "driver_profiles",
        ["assigned_driver_profile_id"], ["id"],
    )
    op.create_foreign_key(
        "fk_tr_assigned_by_user_id",
        "transport_requests", "users",
        ["assigned_by_user_id"], ["id"],
    )

    op.create_index(
        "ix_transport_requests_assigned_vehicle_id",
        "transport_requests", ["assigned_vehicle_id"],
    )
    op.create_index(
        "ix_transport_requests_assigned_driver_profile_id",
        "transport_requests", ["assigned_driver_profile_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_transport_requests_assigned_vehicle_id", table_name="transport_requests")
    op.drop_index("ix_transport_requests_assigned_driver_profile_id", table_name="transport_requests")

    op.drop_constraint("fk_tr_assigned_vehicle_id", "transport_requests", type_="foreignkey")
    op.drop_constraint("fk_tr_assigned_driver_profile_id", "transport_requests", type_="foreignkey")
    op.drop_constraint("fk_tr_assigned_by_user_id", "transport_requests", type_="foreignkey")

    op.drop_column("transport_requests", "assignment_notes")
    op.drop_column("transport_requests", "assigned_at")
    op.drop_column("transport_requests", "assigned_by_user_id")
    op.drop_column("transport_requests", "assigned_driver_profile_id")
    op.drop_column("transport_requests", "assigned_vehicle_id")
    # Note: PostgreSQL does not support removing enum values — 'assigned' remains in the type.
