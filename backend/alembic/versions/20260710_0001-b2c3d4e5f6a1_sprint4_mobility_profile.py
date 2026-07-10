"""sprint4 mobility profile

Revision ID: b2c3d4e5f6a1
Revises: a1b2c3d4e5f6
Create Date: 2026-07-10 00:01:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b2c3d4e5f6a1"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "mobility_profiles",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        # Persönliche Angaben
        sa.Column("display_name", sa.String(200), nullable=True),
        sa.Column("date_of_birth", sa.String(20), nullable=True),
        # Notfallkontakt
        sa.Column("emergency_contact_name", sa.String(200), nullable=True),
        sa.Column("emergency_contact_phone", sa.String(50), nullable=True),
        # Mobilitätsbedarf
        sa.Column("uses_wheelchair", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column(
            "wheelchair_type",
            sa.Enum("manual", "electric", "unknown", name="wheelchairtype"),
            nullable=True,
        ),
        sa.Column("uses_rollator", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("uses_crutches", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column(
            "is_blind_or_visually_impaired",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "is_deaf_or_hard_of_hearing",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column("needs_escort", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column(
            "needs_entry_assistance",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "needs_door_to_door_assistance",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column("needs_ramp", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("needs_lift", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column(
            "needs_stretcher_transport",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        # Fahrzeug- / Service-Hinweise
        sa.Column("can_transfer_to_seat", sa.Boolean(), nullable=True),
        sa.Column("has_own_wheelchair", sa.Boolean(), nullable=True),
        sa.Column(
            "requires_wheelchair_space",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "requires_extra_time", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        # Freitextfelder
        sa.Column("communication_notes", sa.Text(), nullable=True),
        sa.Column("medical_notes", sa.Text(), nullable=True),
        sa.Column("general_notes", sa.Text(), nullable=True),
        # Systemfelder
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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_mobility_profiles_user_id"),
    )


def downgrade() -> None:
    op.drop_table("mobility_profiles")
    sa.Enum(name="wheelchairtype").drop(op.get_bind())
