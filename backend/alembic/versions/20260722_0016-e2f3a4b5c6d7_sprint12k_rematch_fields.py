"""Sprint 12K: add rematch_group_id and rematch_attempt to transport_requests.

Enables auto-rematch of spontaneous rides after driver decline or timeout.
rematch_group_id links all retry-attempts of a ride chain together.
rematch_attempt tracks how many rematches have occurred (max enforced in code).

Revision ID: e2f3a4b5c6d7
Revises: d1e2f3a4b5c6
Create Date: 2026-07-22
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "e2f3a4b5c6d7"
down_revision = "d1e2f3a4b5c6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "transport_requests",
        sa.Column("rematch_group_id", sa.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "transport_requests",
        sa.Column(
            "rematch_attempt",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )
    op.create_index(
        "ix_transport_requests_rematch_group_id",
        "transport_requests",
        ["rematch_group_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_transport_requests_rematch_group_id", table_name="transport_requests")
    op.drop_column("transport_requests", "rematch_attempt")
    op.drop_column("transport_requests", "rematch_group_id")
