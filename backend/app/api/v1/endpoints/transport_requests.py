import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.crud import crud_transport_request
from app.models.driver_profile import DriverProfile
from app.models.mobility_profile import MobilityProfile
from app.models.transport_request import TransportRequest, TransportRequestStatus
from app.models.user import User, UserRole
from app.models.vehicle import Vehicle
from app.schemas.transport_request import (
    MatchingOptionsResponse,
    TransportRequestAssign,
    TransportRequestCreate,
    TransportRequestListItem,
    TransportRequestRead,
    TransportRequestUpdate,
)
from app.services import manual_matching

router = APIRouter(prefix="/transport-requests", tags=["transport-requests"])

_SUBMIT_REQUIRED_FIELDS = [
    "passenger_user_id",
    "transport_type_id",
    "pickup_address",
    "destination_address",
    "pickup_date",
    "pickup_time",
]

_DISPOSITION_ROLES = {UserRole.dispatcher, UserRole.provider_admin, UserRole.platform_admin}


def _enrich_list_items(items: list[TransportRequest], db: Session) -> list[TransportRequestListItem]:
    """Ergänzt Fahrgast-Kontaktfelder in der Listenansicht (Batch-Query, kein N+1)."""
    if not items:
        return []
    passenger_ids = {req.passenger_user_id for req in items}
    users: dict = {
        u.id: u
        for u in db.query(User).filter(User.id.in_(passenger_ids)).all()
    }
    result = []
    for req in items:
        item = TransportRequestListItem.model_validate(req)
        user = users.get(req.passenger_user_id)
        if user:
            item = item.model_copy(update={
                "passenger_display_name": f"{user.first_name} {user.last_name}".strip(),
                "passenger_email": user.email,
                "passenger_phone": user.phone,
            })
        result.append(item)
    return result


def _enrich_read(req: TransportRequest, db: Session) -> TransportRequestRead:
    """Ergänzt Fahrgast-Kontaktfelder inkl. Notfallkontakt für Detailansicht."""
    data = TransportRequestRead.model_validate(req)
    passenger = db.query(User).filter(User.id == req.passenger_user_id).first()
    if passenger:
        update: dict = {
            "passenger_display_name": f"{passenger.first_name} {passenger.last_name}".strip(),
            "passenger_email": passenger.email,
            "passenger_phone": passenger.phone,
        }
        profile = (
            db.query(MobilityProfile)
            .filter(MobilityProfile.user_id == req.passenger_user_id)
            .first()
        )
        if profile:
            update["passenger_emergency_contact_name"] = profile.emergency_contact_name
            update["passenger_emergency_contact_phone"] = profile.emergency_contact_phone
        data = data.model_copy(update=update)
    return data


def _own_or_404(db: Session, request_id: uuid.UUID, current_user: User) -> TransportRequest:
    req = crud_transport_request.get(db, request_id)
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anfrage nicht gefunden")
    if current_user.role not in _DISPOSITION_ROLES:
        if req.requester_user_id != current_user.id and req.passenger_user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Kein Zugriff auf diese Anfrage")
    return req


@router.get("", response_model=list[TransportRequestListItem])
def list_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role in _DISPOSITION_ROLES:
        items = crud_transport_request.get_for_disposition(db)
    else:
        items = crud_transport_request.get_for_user(db, current_user.id)
    return _enrich_list_items(items, db)


@router.post("", response_model=TransportRequestRead, status_code=status.HTTP_201_CREATED)
def create_request(
    payload: TransportRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    req = crud_transport_request.create(db, payload, current_user.id)
    db.commit()
    db.refresh(req)
    return _enrich_read(req, db)


@router.get("/{request_id}", response_model=TransportRequestRead)
def get_request(
    request_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    req = _own_or_404(db, request_id, current_user)
    return _enrich_read(req, db)


@router.put("/{request_id}", response_model=TransportRequestRead)
def update_request(
    request_id: uuid.UUID,
    payload: TransportRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    req = _own_or_404(db, request_id, current_user)
    if req.status == TransportRequestStatus.cancelled:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Stornierte Anfragen können nicht bearbeitet werden",
        )
    req = crud_transport_request.update(db, req, payload)
    db.commit()
    db.refresh(req)
    return _enrich_read(req, db)


@router.post("/{request_id}/submit", response_model=TransportRequestRead)
def submit_request(
    request_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    req = _own_or_404(db, request_id, current_user)
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
    return _enrich_read(req, db)


@router.post("/{request_id}/cancel", response_model=TransportRequestRead)
def cancel_request(
    request_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    req = _own_or_404(db, request_id, current_user)
    if req.status == TransportRequestStatus.cancelled:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Anfrage ist bereits storniert",
        )
    req = crud_transport_request.cancel(db, req)
    db.commit()
    db.refresh(req)
    return _enrich_read(req, db)


@router.get("/{request_id}/matching-options", response_model=MatchingOptionsResponse)
def get_matching_options(
    request_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fahrzeug- und Fahrerbewertung für eine Anfrage. Nur Entscheidungshilfe."""
    req = _own_or_404(db, request_id, current_user)
    vehicles = db.query(Vehicle).filter(Vehicle.is_active.is_(True)).all()
    drivers = db.query(DriverProfile).filter(DriverProfile.is_active.is_(True)).all()
    return manual_matching.evaluate_request_options(req, vehicles, drivers)


@router.post("/{request_id}/assign", response_model=TransportRequestRead)
def assign_request(
    request_id: uuid.UUID,
    payload: TransportRequestAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fahrzeug und Fahrer manuell zuweisen. Disponent entscheidet — Matching ist nur Hinweis."""
    req = _own_or_404(db, request_id, current_user)
    if req.status == TransportRequestStatus.cancelled:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Stornierte Anfragen können nicht zugewiesen werden",
        )
    if req.status == TransportRequestStatus.draft:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Entwürfe können nicht zugewiesen werden — erst absenden",
        )
    vehicle = (
        db.query(Vehicle)
        .filter(Vehicle.id == payload.vehicle_id, Vehicle.is_active.is_(True))
        .first()
    )
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Fahrzeug nicht gefunden oder nicht aktiv",
        )
    driver = (
        db.query(DriverProfile)
        .filter(DriverProfile.id == payload.driver_profile_id, DriverProfile.is_active.is_(True))
        .first()
    )
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Fahrerprofil nicht gefunden oder nicht aktiv",
        )
    req = crud_transport_request.assign(
        db, req,
        payload.vehicle_id,
        payload.driver_profile_id,
        current_user.id,
        payload.assignment_notes,
    )
    db.commit()
    db.refresh(req)
    return _enrich_read(req, db)


@router.post("/{request_id}/unassign", response_model=TransportRequestRead)
def unassign_request(
    request_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Zuweisung aufheben — setzt Status zurück auf requested."""
    req = _own_or_404(db, request_id, current_user)
    if req.status != TransportRequestStatus.assigned:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Nur zugewiesene Anfragen können zurückgesetzt werden",
        )
    req = crud_transport_request.unassign(db, req)
    db.commit()
    db.refresh(req)
    return _enrich_read(req, db)
