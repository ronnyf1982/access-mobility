"""sprint10: add driver_shifts table

Revision ID: c4d5e6f7a8b9
Revises: b3c4d5e6f7a8
Create Date: 2026-07-16
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import ENUM as PGEnum

# Referenz auf bereits existierenden Typ — kein CREATE TYPE durch SQLAlchemy
_shiftstatus = PGEnum("active", "paused", "ended", name="shiftstatus", create_type=False)

revision = "c4d5e6f7a8b9"
down_revision = "b3c4d5e6f7a8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Idempotent: CREATE TYPE nur wenn noch nicht vorhanden
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE shiftstatus AS ENUM ('active', 'paused', 'ended');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)
    op.create_table(
        "driver_shifts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "driver_profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("driver_profiles.id"),
            nullable=False,
        ),
        sa.Column(
            "vehicle_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("vehicles.id"),
            nullable=False,
        ),
        sa.Column("status", _shiftstatus, nullable=False, server_default="active"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("break_started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_driver_shifts_driver_profile_id", "driver_shifts", ["driver_profile_id"])
    op.create_index("ix_driver_shifts_vehicle_id", "driver_shifts", ["vehicle_id"])
    op.create_index("ix_driver_shifts_status", "driver_shifts", ["status"])


def downgrade() -> None:
    op.drop_index("ix_driver_shifts_status", table_name="driver_shifts")
    op.drop_index("ix_driver_shifts_vehicle_id", table_name="driver_shifts")
    op.drop_index("ix_driver_shifts_driver_profile_id", table_name="driver_shifts")
    op.drop_table("driver_shifts")
    op.execute("DROP TYPE IF EXISTS shiftstatus")
