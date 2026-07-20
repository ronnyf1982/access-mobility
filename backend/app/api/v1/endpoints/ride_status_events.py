import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.crud import crud_ride_status_event
from app.crud.crud_driver_shift import get_driver_profile_for_user
from app.models.transport_request import TransportRequest, TransportRequestStatus
from app.models.user import User, UserRole
from app.schemas.ride_status_event import RideStatusEventCreate, RideStatusEventRead

router = APIRouter(tags=["ride-status-events"])

_READ_ROLES = {UserRole.driver, UserRole.dispatcher, UserRole.provider_admin, UserRole.platform_admin, UserRole.organization_coordinator}


def _get_request_or_404(db: Session, request_id: uuid.UUID) -> TransportRequest:
    tr = db.get(TransportRequest, request_id)
    if not tr:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transportanfrage nicht gefunden.")
    return tr


@router.post(
    "/driver/transport-requests/{request_id}/status-events",
    response_model=RideStatusEventRead,
    status_code=status.HTTP_201_CREATED,
)
def create_status_event(
    request_id: uuid.UUID,
    body: RideStatusEventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RideStatusEventRead:
    if current_user.role != UserRole.driver:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Nur Fahrer dürfen Statusereignisse setzen.")

    profile = get_driver_profile_for_user(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kein Fahrerprofil gefunden.")

    tr = _get_request_or_404(db, request_id)

    # Fahrer darf nur Status für ihm zugewiesene Fahrten setzen
    if tr.assigned_driver_profile_id != profile.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Diese Fahrt ist Ihnen nicht zugewiesen.",
        )

    if tr.status not in (TransportRequestStatus.assigned, TransportRequestStatus.completed, TransportRequestStatus.cancelled):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Statusereignisse können nur für zugewiesene Fahrten gesetzt werden.",
        )

    event = crud_ride_status_event.create_event(
        db,
        transport_request_id=request_id,
        status=body.status,
        created_by_user_id=current_user.id,
        note=body.note,
    )
    db.commit()
    db.refresh(event)
    return RideStatusEventRead.model_validate(event)


@router.get(
    "/transport-requests/{request_id}/status-events",
    response_model=list[RideStatusEventRead],
)
def list_status_events(
    request_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[RideStatusEventRead]:
    tr = _get_request_or_404(db, request_id)

    # Fahrer: nur eigene zugewiesene Fahrten
    if current_user.role == UserRole.driver:
        profile = get_driver_profile_for_user(db, current_user.id)
        if not profile or tr.assigned_driver_profile_id != profile.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Zugriff verweigert.")
    # Fahrgast: nur eigene Fahrten
    elif current_user.role == UserRole.passenger:
        if tr.passenger_user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Zugriff verweigert.")
    # Staff-Rollen
    elif current_user.role not in _READ_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Zugriff verweigert.")

    events = crud_ride_status_event.list_events(db, request_id)
    return [RideStatusEventRead.model_validate(e) for e in events]
