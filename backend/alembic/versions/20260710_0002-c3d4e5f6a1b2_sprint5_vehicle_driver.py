"""sprint5 vehicle driver

Revision ID: c3d4e5f6a1b2
Revises: b2c3d4e5f6a1
Create Date: 2026-07-10 00:02:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c3d4e5f6a1b2"
down_revision: Union[str, None] = "b2c3d4e5f6a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Organization-Erweiterung ──────────────────────────────────────────────
    op.add_column("organizations", sa.Column("address_line", sa.String(500), nullable=True))
    op.add_column("organizations", sa.Column("postal_code", sa.String(20), nullable=True))
    op.add_column("organizations", sa.Column("city", sa.String(100), nullable=True))
    op.add_column("organizations", sa.Column("country", sa.String(10), nullable=True))
    op.add_column("organizations", sa.Column("dispatch_phone", sa.String(50), nullable=True))
    op.add_column("organizations", sa.Column("dispatch_email", sa.String(255), nullable=True))
    op.add_column("organizations", sa.Column("operating_area_notes", sa.Text(), nullable=True))
    op.add_column("organizations", sa.Column("notes", sa.Text(), nullable=True))

    # ── Vehicles ──────────────────────────────────────────────────────────────
    op.create_table(
        "vehicles",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("organization_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("license_plate", sa.String(20), nullable=False),
        sa.Column(
            "vehicle_type",
            sa.Enum(
                "standard_car",
                "comfort_car",
                "wheelchair_van",
                "wheelchair_bus",
                "multi_passenger_van",
                "stretcher_vehicle",
                "other",
                name="vehicletype",
            ),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        # Kapazität
        sa.Column("seat_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("wheelchair_space_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("escort_seat_count", sa.Integer(), nullable=True),
        # Ausstattung
        sa.Column("has_ramp", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("has_lift", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("has_wheelchair_restraint", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("supports_electric_wheelchair", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("supports_stretcher_transport", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("has_child_seat", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("has_low_entry", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("has_extra_wide_door", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        # Betrieb
        sa.Column("home_base_address", sa.String(500), nullable=True),
        sa.Column("current_location_notes", sa.Text(), nullable=True),
        sa.Column("equipment_notes", sa.Text(), nullable=True),
        sa.Column("general_notes", sa.Text(), nullable=True),
        # Systemfelder
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_vehicles_organization_id", "vehicles", ["organization_id"])

    # ── Driver Profiles ───────────────────────────────────────────────────────
    op.create_table(
        "driver_profiles",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("organization_id", sa.UUID(), nullable=False),
        sa.Column("display_name", sa.String(200), nullable=False),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        # Qualifikationen
        sa.Column("can_assist_wheelchair", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("can_secure_wheelchair", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("can_operate_lift", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("can_assist_blind_passengers", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("can_assist_deaf_passengers", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("can_handle_stretcher", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("has_first_aid_training", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("has_passenger_transport_license", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        # Betrieb
        sa.Column("home_base_address", sa.String(500), nullable=True),
        sa.Column("availability_notes", sa.Text(), nullable=True),
        sa.Column("qualification_notes", sa.Text(), nullable=True),
        sa.Column("general_notes", sa.Text(), nullable=True),
        # Systemfelder
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_driver_profiles_user_id", "driver_profiles", ["user_id"])
    op.create_index("ix_driver_profiles_organization_id", "driver_profiles", ["organization_id"])


def downgrade() -> None:
    op.drop_index("ix_driver_profiles_organization_id", "driver_profiles")
    op.drop_index("ix_driver_profiles_user_id", "driver_profiles")
    op.drop_table("driver_profiles")

    op.drop_index("ix_vehicles_organization_id", "vehicles")
    op.drop_table("vehicles")
    sa.Enum(name="vehicletype").drop(op.get_bind())

    for col in [
        "notes", "operating_area_notes", "dispatch_email", "dispatch_phone",
        "country", "city", "postal_code", "address_line",
    ]:
        op.drop_column("organizations", col)
