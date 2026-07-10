import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.transport_request import TransportRequest, TransportRequestStatus
from app.schemas.transport_request import TransportRequestCreate, TransportRequestUpdate


def get(db: Session, request_id: uuid.UUID) -> TransportRequest | None:
    return db.query(TransportRequest).filter(TransportRequest.id == request_id).first()


def get_for_user(
    db: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> list[TransportRequest]:
    return (
        db.query(TransportRequest)
        .filter(
            (TransportRequest.requester_user_id == user_id)
            | (TransportRequest.passenger_user_id == user_id)
        )
        .order_by(TransportRequest.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_for_disposition(
    db: Session, skip: int = 0, limit: int = 200
) -> list[TransportRequest]:
    """Alle requested/assigned Anfragen — für Disponenten und Provider."""
    return (
        db.query(TransportRequest)
        .filter(
            TransportRequest.status.in_([
                TransportRequestStatus.requested,
                TransportRequestStatus.assigned,
            ])
        )
        .order_by(TransportRequest.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create(
    db: Session, payload: TransportRequestCreate, requester_user_id: uuid.UUID
) -> TransportRequest:
    data = payload.model_dump()
    if not data.get("passenger_user_id"):
        data["passenger_user_id"] = requester_user_id
    req = TransportRequest(requester_user_id=requester_user_id, **data)
    db.add(req)
    db.flush()
    return req


def update(
    db: Session, request: TransportRequest, payload: TransportRequestUpdate
) -> TransportRequest:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(request, key, value)
    db.flush()
    return request


def submit(db: Session, request: TransportRequest) -> TransportRequest:
    request.status = TransportRequestStatus.requested
    request.submitted_at = datetime.now(timezone.utc)
    db.flush()
    return request


def cancel(db: Session, request: TransportRequest) -> TransportRequest:
    request.status = TransportRequestStatus.cancelled
    request.cancelled_at = datetime.now(timezone.utc)
    db.flush()
    return request


def assign(
    db: Session,
    request: TransportRequest,
    vehicle_id: uuid.UUID,
    driver_profile_id: uuid.UUID,
    assigned_by_user_id: uuid.UUID,
    notes: str | None = None,
) -> TransportRequest:
    request.assigned_vehicle_id = vehicle_id
    request.assigned_driver_profile_id = driver_profile_id
    request.assigned_by_user_id = assigned_by_user_id
    request.assigned_at = datetime.now(timezone.utc)
    request.assignment_notes = notes
    request.status = TransportRequestStatus.assigned
    db.flush()
    return request


def unassign(db: Session, request: TransportRequest) -> TransportRequest:
    request.assigned_vehicle_id = None
    request.assigned_driver_profile_id = None
    request.assigned_by_user_id = None
    request.assigned_at = None
    request.assignment_notes = None
    request.status = TransportRequestStatus.requested
    db.flush()
    return request
