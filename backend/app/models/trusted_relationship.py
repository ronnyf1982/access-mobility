import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TrustStatus(str, Enum):
    pending = "pending"
    active = "active"
    revoked = "revoked"


class TrustedRelationship(Base):
    __tablename__ = "trusted_relationships"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    passenger_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    trusted_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    can_book_rides: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_view_rides: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_manage_profile: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[TrustStatus] = mapped_column(
        SAEnum(TrustStatus, name="truststatus"), default=TrustStatus.pending, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
