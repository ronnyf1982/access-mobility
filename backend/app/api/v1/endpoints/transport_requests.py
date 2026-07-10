import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.crud import crud_transport_request
from app.models.transport_request import TransportRequest, TransportRequestStatus
from app.models.user import User
from app.schemas.transport_request import (
    TransportRequestCreate,
    TransportRequestListItem,
    TransportRequestRead,
    TransportRequestUpdate,
)

router = APIRouter(prefix="/transport-requests", tags=["transport-requests"])

_SUBMIT_REQUIRED_FIELDS = [
    "passenger_user_id",
    "transport_type_id",
    "pickup_address",
    "destination_address",
    "pickup_date",
    "pickup_time",
]


def _own_or_404(db: Session, request_id: uuid.UUID, user_id: uuid.UUID) -> TransportRequest:
    req = crud_transport_request.get(db, request_id)
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anfrage nicht gefunden")
    if req.requester_user_id != user_id and req.passenger_user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Kein Zugriff auf diese Anfrage")
    return req


@router.get("", response_model=list[TransportRequestListItem])
def list_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Eigene Anfragen — als Steller oder Fahrgast."""
    return crud_transport_request.get_for_user(db, current_user.id)


@router.post("", response_model=TransportRequestRead, status_code=status.HTTP_201_CREATED)
def create_request(
    payload: TransportRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Neue Transportanfrage erstellen (Standard: draft)."""
    req = crud_transport_request.create(db, payload, current_user.id)
    db.commit()
    db.refresh(req)
    return req


@router.get("/{request_id}", response_model=TransportRequestRead)
def get_request(
    request_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _own_or_404(db, request_id, current_user.id)


@router.put("/{request_id}", response_model=TransportRequestRead)
def update_request(
    request_id: uuid.UUID,
    payload: TransportRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    req = _own_or_404(db, request_id, current_user.id)
    if req.status == TransportRequestStatus.cancelled:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Stornierte Anfragen können nicht bearbeitet werden",
        )
    req = crud_transport_request.update(db, req, payload)
    db.commit()
    db.refresh(req)
    return req


@router.post("/{request_id}/submit", response_model=TransportRequestRead)
def submit_request(
    request_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Entwurf absenden → status requested."""
    req = _own_or_404(db, request_id, current_user.id)
    if req.status != TransportRequestStatus.draft:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Nur Entwürfe können abgesendet werden",
        )
    missing = [f for f in _SUBMIT_REQUIRED_FIELDS if not getattr(req, f, None)]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Pflichtfelder fehlen: {', '.join(missing)}",
        )
    req = crud_transport_request.submit(db, req)
    db.commit()
    db.refresh(req)
    return req


@router.post("/{request_id}/cancel", response_model=TransportRequestRead)
def cancel_request(
    request_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Anfrage stornieren (draft oder requested)."""
    req = _own_or_404(db, request_id, current_user.id)
    if req.status == TransportRequestStatus.cancelled:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Anfrage ist bereits storniert",
        )
    req = crud_transport_request.cancel(db, req)
    db.commit()
    db.refresh(req)
    return req
