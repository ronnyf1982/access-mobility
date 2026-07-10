"""sprint6_transport_request: TransportRequest Tabelle mit Status-Enum

Revision ID: f6a1b2c3d4e5
Revises: e5f6a1b2c3d4
Create Date: 2026-07-10
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "f6a1b2c3d4e5"
down_revision = "e5f6a1b2c3d4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enum via Raw-SQL anlegen — verhindert Doppel-CREATE durch SQLAlchemy-Internals.
    op.execute("CREATE TYPE transportrequeststatus AS ENUM ('draft', 'requested', 'cancelled')")

    op.create_table(
        "transport_requests",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("requester_user_id", sa.UUID(), nullable=False),
        sa.Column("passenger_user_id", sa.UUID(), nullable=False),
        sa.Column("organization_id", sa.UUID(), nullable=True),
        sa.Column("transport_type_id", sa.String(100), nullable=True),
        sa.Column(
            "status",
            # create_type=False: Typ wurde oben via Raw-SQL bereits angelegt.
            postgresql.ENUM(
                "draft", "requested", "cancelled",
                name="transportrequeststatus",
                create_type=False,
            ),
            nullable=False,
            server_default="draft",
        ),
        sa.Column("pickup_address", sa.Text(), nullable=True),
        sa.Column("pickup_details", sa.Text(), nullable=True),
        sa.Column("destination_address", sa.Text(), nullable=True),
        sa.Column("destination_details", sa.Text(), nullable=True),
        sa.Column("pickup_date", sa.Date(), nullable=True),
        sa.Column("pickup_time", sa.Time(), nullable=True),
        sa.Column("arrival_time", sa.Time(), nullable=True),
        sa.Column("is_round_trip", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("return_time_known", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("return_pickup_time", sa.Time(), nullable=True),
        sa.Column(
            "requirement_snapshot",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "mobility_profile_snapshot",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["requester_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["passenger_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_transport_requests_passenger_user_id",
        "transport_requests",
        ["passenger_user_id"],
    )
    op.create_index(
        "ix_transport_requests_requester_user_id",
        "transport_requests",
        ["requester_user_id"],
    )
    op.create_index("ix_transport_requests_status", "transport_requests", ["status"])
    op.create_index("ix_transport_requests_pickup_date", "transport_requests", ["pickup_date"])


def downgrade() -> None:
    op.drop_index("ix_transport_requests_pickup_date", table_name="transport_requests")
    op.drop_index("ix_transport_requests_status", table_name="transport_requests")
    op.drop_index("ix_transport_requests_requester_user_id", table_name="transport_requests")
    op.drop_index("ix_transport_requests_passenger_user_id", table_name="transport_requests")
    op.drop_table("transport_requests")
    op.execute("DROP TYPE IF EXISTS transportrequeststatus")
