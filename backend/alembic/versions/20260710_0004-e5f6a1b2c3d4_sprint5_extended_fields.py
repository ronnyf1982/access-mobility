"""sprint5_extended_fields: vehicle dimensions/weight/access, vehicle medical extras,
mobility profile medical detail fields + AttendantType enum,
driver profile medical qualifications + technical training fields

Revision ID: e5f6a1b2c3d4
Revises: d4e5f6a1b2c3
Create Date: 2026-07-10
"""
from alembic import op
import sqlalchemy as sa

revision = "e5f6a1b2c3d4"
down_revision = "d4e5f6a1b2c3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Vehicle: additional medical fields ──────────────────────────────────
    op.add_column("vehicles", sa.Column("has_transport_chair", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("vehicles", sa.Column("has_infusion_mount", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("vehicles", sa.Column("supports_two_person_crew", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("vehicles", sa.Column("patient_compartment_notes", sa.Text(), nullable=True))

    # ── Vehicle: dimension / weight / access fields ──────────────────────────
    op.add_column("vehicles", sa.Column("vehicle_length_cm", sa.Integer(), nullable=True))
    op.add_column("vehicles", sa.Column("vehicle_width_cm", sa.Integer(), nullable=True))
    op.add_column("vehicles", sa.Column("vehicle_width_with_mirrors_cm", sa.Integer(), nullable=True))
    op.add_column("vehicles", sa.Column("vehicle_height_cm", sa.Integer(), nullable=True))
    op.add_column("vehicles", sa.Column("wheelbase_cm", sa.Integer(), nullable=True))
    op.add_column("vehicles", sa.Column("turning_circle_m", sa.Float(), nullable=True))
    op.add_column("vehicles", sa.Column("empty_weight_kg", sa.Integer(), nullable=True))
    op.add_column("vehicles", sa.Column("gross_vehicle_weight_kg", sa.Integer(), nullable=True))
    op.add_column("vehicles", sa.Column("payload_capacity_kg", sa.Integer(), nullable=True))
    op.add_column("vehicles", sa.Column("requires_large_parking_space", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("vehicles", sa.Column("suitable_for_narrow_streets", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("vehicles", sa.Column("suitable_for_underground_parking", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("vehicles", sa.Column("has_parking_assist", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("vehicles", sa.Column("access_restriction_notes", sa.Text(), nullable=True))

    # ── MobilityProfile: AttendantType enum + medical detail fields ──────────
    attendanttype = sa.Enum(
        "none", "escort_person", "second_assistant", "paramedic",
        "medical_professional", "unknown",
        name="attendanttype",
    )
    attendanttype.create(op.get_bind(), checkfirst=True)

    op.add_column("mobility_profiles", sa.Column("requires_transport_chair", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("mobility_profiles", sa.Column("requires_two_person_assistance", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("mobility_profiles", sa.Column("requires_medical_transport", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("mobility_profiles", sa.Column("brings_oxygen", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("mobility_profiles", sa.Column("requires_oxygen_mount", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("mobility_profiles", sa.Column("brings_medical_device", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("mobility_profiles", sa.Column("requires_medical_equipment_storage", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("mobility_profiles", sa.Column("requires_infusion_mount", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("mobility_profiles", sa.Column("requires_special_positioning", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("mobility_profiles", sa.Column("infection_or_hygiene_note", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("mobility_profiles", sa.Column("requires_medical_attendant", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("mobility_profiles", sa.Column("attendant_type_required", attendanttype, nullable=False, server_default="none"))
    op.add_column("mobility_profiles", sa.Column("medical_device_notes", sa.Text(), nullable=True))
    op.add_column("mobility_profiles", sa.Column("medical_transport_notes", sa.Text(), nullable=True))

    # ── DriverProfile: medical qualifications ───────────────────────────────
    op.add_column("driver_profiles", sa.Column("has_sanitaetshelfer_training", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("driver_profiles", sa.Column("has_rettungshelfer_qualification", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("driver_profiles", sa.Column("has_rettungssanitaeter_qualification", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("driver_profiles", sa.Column("has_rettungsassistent_qualification", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("driver_profiles", sa.Column("has_notfallsanitaeter_qualification", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("driver_profiles", sa.Column("has_nursing_qualification", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("driver_profiles", sa.Column("has_medical_assistant_qualification", sa.Boolean(), nullable=False, server_default="false"))

    # ── DriverProfile: technical training ───────────────────────────────────
    op.add_column("driver_profiles", sa.Column("has_hygiene_training", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("driver_profiles", sa.Column("has_infection_protection_training", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("driver_profiles", sa.Column("has_wheelchair_restraint_training", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("driver_profiles", sa.Column("has_lift_operation_training", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("driver_profiles", sa.Column("has_stretcher_handling_training", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("driver_profiles", sa.Column("has_transport_chair_training", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("driver_profiles", sa.Column("has_oxygen_equipment_training", sa.Boolean(), nullable=False, server_default="false"))


def downgrade() -> None:
    # DriverProfile
    for col in [
        "has_oxygen_equipment_training", "has_transport_chair_training",
        "has_stretcher_handling_training", "has_lift_operation_training",
        "has_wheelchair_restraint_training", "has_infection_protection_training",
        "has_hygiene_training", "has_medical_assistant_qualification",
        "has_nursing_qualification", "has_notfallsanitaeter_qualification",
        "has_rettungsassistent_qualification", "has_rettungssanitaeter_qualification",
        "has_rettungshelfer_qualification", "has_sanitaetshelfer_training",
    ]:
        op.drop_column("driver_profiles", col)

    # MobilityProfile
    for col in [
        "medical_transport_notes", "medical_device_notes", "attendant_type_required",
        "requires_medical_attendant", "infection_or_hygiene_note",
        "requires_special_positioning", "requires_infusion_mount",
        "requires_medical_equipment_storage", "brings_medical_device",
        "requires_oxygen_mount", "brings_oxygen", "requires_medical_transport",
        "requires_two_person_assistance", "requires_transport_chair",
    ]:
        op.drop_column("mobility_profiles", col)
    sa.Enum(name="attendanttype").drop(op.get_bind(), checkfirst=True)

    # Vehicle: dimensions
    for col in [
        "access_restriction_notes", "has_parking_assist",
        "suitable_for_underground_parking", "suitable_for_narrow_streets",
        "requires_large_parking_space", "payload_capacity_kg",
        "gross_vehicle_weight_kg", "empty_weight_kg", "turning_circle_m",
        "wheelbase_cm", "vehicle_height_cm", "vehicle_width_with_mirrors_cm",
        "vehicle_width_cm", "vehicle_length_cm",
    ]:
        op.drop_column("vehicles", col)

    # Vehicle: additional medical
    for col in [
        "patient_compartment_notes", "supports_two_person_crew",
        "has_infusion_mount", "has_transport_chair",
    ]:
        op.drop_column("vehicles", col)
