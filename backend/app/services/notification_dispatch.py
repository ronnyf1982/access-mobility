"""Placeholder for notification dispatch logic (Sprint 12A).

Reads PassengerNotificationPreference to determine targets.
No actual sending happens here — dispatch will be wired in Sprint 12B.
"""
import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.mobility_profile import MobilityProfile
from app.models.notification_preference import NotificationEventType, PassengerNotificationPreference


@dataclass
class NotificationTarget:
    event_type: NotificationEventType
    passenger_user_id: uuid.UUID
    notify_trusted_persons: bool
    channel_in_app: bool
    channel_email: bool
    channel_sms: bool


def collect_notification_targets_for_status_event(
    db: Session,
    transport_request_id: uuid.UUID,
    event_type: NotificationEventType,
) -> list[NotificationTarget]:
    """Returns notification targets for a ride status event.

    Looks up the passenger's preferences for the given event type and returns
    a descriptor. The caller is responsible for actual dispatch (Sprint 12B).
    """
    from app.models.transport_request import TransportRequest

    tr = db.get(TransportRequest, transport_request_id)
    if not tr:
        return []

    mp = (
        db.query(MobilityProfile)
        .filter(MobilityProfile.user_id == tr.passenger_user_id)
        .first()
    )
    if not mp:
        return []

    pref = (
        db.query(PassengerNotificationPreference)
        .filter(
            PassengerNotificationPreference.mobility_profile_id == mp.id,
            PassengerNotificationPreference.event_type == event_type,
        )
        .first()
    )
    if not pref:
        return []

    return [
        NotificationTarget(
            event_type=pref.event_type,
            passenger_user_id=tr.passenger_user_id,
            notify_trusted_persons=pref.notify_trusted_persons,
            channel_in_app=pref.channel_in_app,
            channel_email=pref.channel_email,
            channel_sms=pref.channel_sms,
        )
    ]
