import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class NotificationEventType(str, Enum):
    driver_on_way = "driver_on_way"
    driver_arrived = "driver_arrived"
    passenger_picked_up = "passenger_picked_up"
    ride_started = "ride_started"
    ride_completed = "ride_completed"
    ride_cancelled = "ride_cancelled"
    issue_reported = "issue_reported"


class PassengerNotificationPreference(Base):
    __tablename__ = "passenger_notification_preferences"
    __table_args__ = (
        Index(
            "ix_notif_pref_mobility_profile_id",
            "mobility_profile_id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    mobility_profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("mobility_profiles.id"), nullable=False
    )
    event_type: Mapped[NotificationEventType] = mapped_column(
        SAEnum(NotificationEventType, name="notificationeventtype"), nullable=False
    )
    notify_trusted_persons: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    channel_in_app: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    channel_email: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    channel_sms: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
