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
