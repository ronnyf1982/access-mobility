"""sprint5 medical fields

Revision ID: d4e5f6a1b2c3
Revises: c3d4e5f6a1b2
Create Date: 2026-07-10 00:03:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d4e5f6a1b2c3"
down_revision: Union[str, None] = "c3d4e5f6a1b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Vehicles — medizinische Ausstattung ──────────────────────────────────
    op.add_column("vehicles", sa.Column("has_stretcher", sa.Boolean(), server_default=sa.text("false"), nullable=False))
    op.add_column("vehicles", sa.Column("has_stretcher_mount", sa.Boolean(), server_default=sa.text("false"), nullable=False))
    op.add_column("vehicles", sa.Column("has_medical_equipment_storage", sa.Boolean(), server_default=sa.text("false"), nullable=False))
    op.add_column("vehicles", sa.Column("has_oxygen_mount", sa.Boolean(), server_default=sa.text("false"), nullable=False))
    op.add_column("vehicles", sa.Column("has_first_aid_kit", sa.Boolean(), server_default=sa.text("false"), nullable=False))
    op.add_column("vehicles", sa.Column("has_hygiene_equipment", sa.Boolean(), server_default=sa.text("false"), nullable=False))
    op.add_column("vehicles", sa.Column("supports_non_emergency_medical_transport", sa.Boolean(), server_default=sa.text("false"), nullable=False))

    # ── Driver Profiles — med. Krankentransport ───────────────────────────────
    op.add_column("driver_profiles", sa.Column("can_support_medical_transport", sa.Boolean(), server_default=sa.text("false"), nullable=False))


def downgrade() -> None:
    op.drop_column("driver_profiles", "can_support_medical_transport")

    for col in [
        "supports_non_emergency_medical_transport",
        "has_hygiene_equipment",
        "has_first_aid_kit",
        "has_oxygen_mount",
        "has_medical_equipment_storage",
        "has_stretcher_mount",
        "has_stretcher",
    ]:
        op.drop_column("vehicles", col)
