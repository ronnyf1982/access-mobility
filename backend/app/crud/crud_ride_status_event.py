import uuid
from typing import List

from sqlalchemy.orm import Session

from app.models.ride_status_event import RideStatusEvent, RideStatusEventType
from app.models.transport_request import TransportRequest, TransportRequestStatus


def create_event(
    db: Session,
    transport_request_id: uuid.UUID,
    status: RideStatusEventType,
    created_by_user_id: uuid.UUID | None = None,
    note: str | None = None,
) -> RideStatusEvent:
    event = RideStatusEvent(
        transport_request_id=transport_request_id,
        status=status,
        note=note,
        created_by_user_id=created_by_user_id,
    )
    db.add(event)

    # Spiegel auf TransportRequest.status
    tr = db.get(TransportRequest, transport_request_id)
    if tr:
        if status == RideStatusEventType.ride_completed:
            tr.status = TransportRequestStatus.completed
        elif status == RideStatusEventType.ride_cancelled:
            tr.status = TransportRequestStatus.cancelled

    db.flush()
    return event


def list_events(db: Session, transport_request_id: uuid.UUID) -> List[RideStatusEvent]:
    return (
        db.query(RideStatusEvent)
        .filter(RideStatusEvent.transport_request_id == transport_request_id)
        .order_by(RideStatusEvent.created_at.asc())
        .all()
    )
