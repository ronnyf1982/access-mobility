from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.notification_preference import NotificationEventType


class NotificationPreferenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    mobility_profile_id: uuid.UUID
    event_type: NotificationEventType
    notify_trusted_persons: bool
    channel_in_app: bool
    channel_email: bool
    channel_sms: bool
    created_at: datetime
    updated_at: datetime


class NotificationPreferenceUpsert(BaseModel):
    event_type: NotificationEventType
    notify_trusted_persons: bool = True
    channel_in_app: bool = True
    channel_email: bool = False
    channel_sms: bool = False
