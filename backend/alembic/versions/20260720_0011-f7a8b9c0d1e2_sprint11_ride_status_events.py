"""sprint11: add ride_status_events, passenger_notification_preferences, completed status

Revision ID: f7a8b9c0d1e2
Revises: e6f7a8b9c0d1
Create Date: 2026-07-20
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import ENUM as PGEnum

_ridestatuseventtype = PGEnum(
    "driver_on_way", "driver_arrived", "passenger_picked_up",
    "ride_started", "ride_completed", "ride_cancelled", "issue_reported",
    name="ridestatuseventtype", create_type=False,
)

_notificationeventtype = PGEnum(
    "driver_on_way", "driver_arrived", "passenger_picked_up",
    "ride_started", "ride_completed", "ride_cancelled", "issue_reported",
    name="notificationeventtype", create_type=False,
)

revision = "f7a8b9c0d1e2"
down_revision = "e6f7a8b9c0d1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. transportrequeststatus um 'completed' erweitern (idempotent)
    op.execute("""
        DO $$ BEGIN
            ALTER TYPE transportrequeststatus ADD VALUE IF NOT EXISTS 'completed';
        EXCEPTION WHEN others THEN NULL;
        END $$;
    """)

    # 2. ridestatuseventtype anlegen (idempotent)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE ridestatuseventtype AS ENUM (
                'driver_on_way', 'driver_arrived', 'passenger_picked_up',
                'ride_started', 'ride_completed', 'ride_cancelled', 'issue_reported'
            );
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)

    # 3. ride_status_events Tabelle
    op.create_table(
        "ride_status_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "transport_request_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("transport_requests.id"),
            nullable=False,
        ),
        sa.Column("status", _ridestatuseventtype, nullable=False),
        sa.Column("note", sa.Text, nullable=True),
        sa.Column(
            "created_by_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_ride_status_events_transport_request_id", "ride_status_events", ["transport_request_id"])
    op.create_index("ix_ride_status_events_created_at", "ride_status_events", ["created_at"])

    # 4. notificationeventtype anlegen (idempotent)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE notificationeventtype AS ENUM (
                'driver_on_way', 'driver_arrived', 'passenger_picked_up',
                'ride_started', 'ride_completed', 'ride_cancelled', 'issue_reported'
            );
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)

    # 5. passenger_notification_preferences Tabelle
    op.create_table(
        "passenger_notification_preferences",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "mobility_profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("mobility_profiles.id"),
            nullable=False,
        ),
        sa.Column("event_type", _notificationeventtype, nullable=False),
        sa.Column("notify_trusted_persons", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("channel_in_app", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("channel_email", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("channel_sms", sa.Boolean, nullable=False, server_default="false"),
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
    op.create_index(
        "ix_notif_pref_mobility_profile_id",
        "passenger_notification_preferences",
        ["mobility_profile_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_notif_pref_mobility_profile_id", table_name="passenger_notification_preferences")
    op.drop_table("passenger_notification_preferences")
    op.execute("DROP TYPE IF EXISTS notificationeventtype")

    op.drop_index("ix_ride_status_events_created_at", table_name="ride_status_events")
    op.drop_index("ix_ride_status_events_transport_request_id", table_name="ride_status_events")
    op.drop_table("ride_status_events")
    op.execute("DROP TYPE IF EXISTS ridestatuseventtype")

    # transportrequeststatus: 'completed' kann in PostgreSQL nicht rückgängig gemacht werden
    # ohne Tabellen-Rebuild — downgrade lässt den Wert stehen
