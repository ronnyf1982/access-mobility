import uuid
from typing import List

from sqlalchemy.orm import Session

from app.models.notification_preference import NotificationEventType, PassengerNotificationPreference


def get_preferences(db: Session, mobility_profile_id: uuid.UUID) -> List[PassengerNotificationPreference]:
    return (
        db.query(PassengerNotificationPreference)
        .filter(PassengerNotificationPreference.mobility_profile_id == mobility_profile_id)
        .order_by(PassengerNotificationPreference.event_type)
        .all()
    )


def upsert_preference(
    db: Session,
    mobility_profile_id: uuid.UUID,
    event_type: NotificationEventType,
    notify_trusted_persons: bool,
    channel_in_app: bool,
    channel_email: bool,
    channel_sms: bool,
) -> PassengerNotificationPreference:
    existing = (
        db.query(PassengerNotificationPreference)
        .filter(
            PassengerNotificationPreference.mobility_profile_id == mobility_profile_id,
            PassengerNotificationPreference.event_type == event_type,
        )
        .first()
    )
    if existing:
        existing.notify_trusted_persons = notify_trusted_persons
        existing.channel_in_app = channel_in_app
        existing.channel_email = channel_email
        existing.channel_sms = channel_sms
        db.flush()
        return existing

    pref = PassengerNotificationPreference(
        mobility_profile_id=mobility_profile_id,
        event_type=event_type,
        notify_trusted_persons=notify_trusted_persons,
        channel_in_app=channel_in_app,
        channel_email=channel_email,
        channel_sms=channel_sms,
    )
    db.add(pref)
    db.flush()
    return pref
