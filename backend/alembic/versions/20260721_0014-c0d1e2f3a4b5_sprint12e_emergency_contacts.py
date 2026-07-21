"""sprint12e: emergency contacts + emergency fields + visibility flags

Revision ID: c0d1e2f3a4b5
Revises: b9c0d1e2f3a4
Create Date: 2026-07-21
"""
import sqlalchemy as sa
from alembic import op

revision = "c0d1e2f3a4b5"
down_revision = "b9c0d1e2f3a4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Dirty-State-Bereinigung: Falls eine vorherige Migration den Typ angelegt,
    # aber die Tabelle nicht erstellt hat, wird der Typ zunächst entfernt.
    op.execute(sa.text("DROP TYPE IF EXISTS contacttype CASCADE"))

    # passenger_contacts table (SQLAlchemy erstellt contacttype-ENUM automatisch)
    op.create_table(
        "passenger_contacts",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("mobility_profile_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("phone_number", sa.String(50), nullable=True),
        sa.Column("role_label", sa.String(200), nullable=True),
        sa.Column("contact_type", sa.Enum(
            "emergency_contact", "trusted_person", "caregiver",
            "school", "workshop", "daycare", "doctor",
            "nursing_service", "parent", "other",
            name="contacttype",
        ), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("is_emergency_contact", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("visible_to_driver", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("visible_in_emergency", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("callable_in_emergency", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("priority", sa.Integer(), nullable=False, server_default=sa.text("999")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["mobility_profile_id"], ["mobility_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_passenger_contacts_mobility_profile_id", "passenger_contacts", ["mobility_profile_id"])

    # New columns on mobility_profiles — Sprint 12E emergency info
    bool_false = sa.text("false")
    op.add_column("mobility_profiles", sa.Column("has_epilepsy", sa.Boolean(), nullable=False, server_default=bool_false))
    op.add_column("mobility_profiles", sa.Column("is_mute", sa.Boolean(), nullable=False, server_default=bool_false))
    op.add_column("mobility_profiles", sa.Column("other_disabilities_notes", sa.Text(), nullable=True))
    op.add_column("mobility_profiles", sa.Column("known_conditions", sa.Text(), nullable=True))
    op.add_column("mobility_profiles", sa.Column("medication_notes", sa.Text(), nullable=True))
    op.add_column("mobility_profiles", sa.Column("allergy_notes", sa.Text(), nullable=True))
    op.add_column("mobility_profiles", sa.Column("emergency_care_notes", sa.Text(), nullable=True))
    op.add_column("mobility_profiles", sa.Column("what_helps_notes", sa.Text(), nullable=True))
    op.add_column("mobility_profiles", sa.Column("what_to_avoid_notes", sa.Text(), nullable=True))
    op.add_column("mobility_profiles", sa.Column("additional_emergency_notes", sa.Text(), nullable=True))
    op.add_column("mobility_profiles", sa.Column("body_height_cm", sa.Integer(), nullable=True))
    op.add_column("mobility_profiles", sa.Column("body_weight_kg", sa.Integer(), nullable=True))
    op.add_column("mobility_profiles", sa.Column("gender", sa.String(20), nullable=True))

    # Visibility flags
    op.add_column("mobility_profiles", sa.Column("show_disabilities_to_driver", sa.Boolean(), nullable=False, server_default=bool_false))
    op.add_column("mobility_profiles", sa.Column("show_disabilities_in_emergency", sa.Boolean(), nullable=False, server_default=bool_false))
    op.add_column("mobility_profiles", sa.Column("show_medication_to_driver", sa.Boolean(), nullable=False, server_default=bool_false))
    op.add_column("mobility_profiles", sa.Column("show_medication_in_emergency", sa.Boolean(), nullable=False, server_default=bool_false))
    op.add_column("mobility_profiles", sa.Column("show_emergency_notes_to_driver", sa.Boolean(), nullable=False, server_default=bool_false))
    op.add_column("mobility_profiles", sa.Column("show_emergency_notes_in_emergency", sa.Boolean(), nullable=False, server_default=bool_false))
    op.add_column("mobility_profiles", sa.Column("show_communication_notes_to_driver", sa.Boolean(), nullable=False, server_default=bool_false))
    op.add_column("mobility_profiles", sa.Column("show_communication_notes_in_emergency", sa.Boolean(), nullable=False, server_default=bool_false))
    op.add_column("mobility_profiles", sa.Column("show_body_data_in_emergency", sa.Boolean(), nullable=False, server_default=bool_false))
    op.add_column("mobility_profiles", sa.Column("show_contacts_to_driver", sa.Boolean(), nullable=False, server_default=bool_false))
    op.add_column("mobility_profiles", sa.Column("show_contacts_in_emergency", sa.Boolean(), nullable=False, server_default=bool_false))


def downgrade() -> None:
    # Visibility flags
    for col in [
        "show_contacts_in_emergency", "show_contacts_to_driver",
        "show_body_data_in_emergency",
        "show_communication_notes_in_emergency", "show_communication_notes_to_driver",
        "show_emergency_notes_in_emergency", "show_emergency_notes_to_driver",
        "show_medication_in_emergency", "show_medication_to_driver",
        "show_disabilities_in_emergency", "show_disabilities_to_driver",
        "gender", "body_weight_kg", "body_height_cm",
        "additional_emergency_notes", "what_to_avoid_notes", "what_helps_notes",
        "emergency_care_notes", "allergy_notes", "medication_notes",
        "known_conditions", "other_disabilities_notes", "is_mute", "has_epilepsy",
    ]:
        op.drop_column("mobility_profiles", col)

    op.drop_index("ix_passenger_contacts_mobility_profile_id", "passenger_contacts")
    op.drop_table("passenger_contacts")
    op.execute(sa.text("DROP TYPE IF EXISTS contacttype"))
