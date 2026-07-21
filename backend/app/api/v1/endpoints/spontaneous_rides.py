import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.crud import crud_driver_shift
from app.models.driver_profile import DriverProfile
from app.models.driver_shift import DriverShift, ShiftStatus
from app.models.ride_status_event import RideStatusEvent, RideStatusEventType
from app.models.transport_request import TransportRequest, TransportRequestStatus
from app.models.trusted_relationship import TrustedRelationship, TrustStatus
from app.models.user import User, UserRole
from app.models.vehicle import Vehicle
from app.schemas.spontaneous_ride import (
    SpontaneousRideBookRequest,
    SpontaneousRideBookResponse,
    SpontaneousRideMatchRequest,
    SpontaneousRideMatchResult,
    SpontaneousRideTracking,
)
from app.services import spontaneous_matching

router = APIRouter(prefix="/spontaneous-rides", tags=["spontaneous-rides"])

_STAFF_ROLES = {
    UserRole.dispatcher,
    UserRole.organization_coordinator,
    UserRole.provider_admin,
    UserRole.platform_admin,
}

_BOOKING_BLOCKED_STATUSES = [
    TransportRequestStatus.assigned,
    TransportRequestStatus.spontaneous_requested,
]


def _resolve_passenger_id(body, current_user: User, db: Session) -> uuid.UUID:
    """Resolve which passenger's profile to use for capability matching / booking."""
    if current_user.role == UserRole.passenger:
        if body.passenger_user_id and body.passenger_user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Fahrgäste können nur für sich selbst suchen.",
            )
        return current_user.id

    if current_user.role == UserRole.trusted_person:
        target_id = body.passenger_user_id
        if not target_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Vertrauenspersonen müssen passenger_user_id angeben.",
            )
        rel = (
            db.query(TrustedRelationship)
            .filter(
                TrustedRelationship.trusted_user_id == current_user.id,
                TrustedRelationship.passenger_user_id == target_id,
                TrustedRelationship.can_view_rides.is_(True),
                TrustedRelationship.status == TrustStatus.active,
            )
            .first()
        )
        if not rel:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Keine aktive Vertrauensbeziehung für diesen Fahrgast.",
            )
        return target_id

    if current_user.role in _STAFF_ROLES:
        return body.passenger_user_id or current_user.id

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Zugriff verweigert.")


@router.post(
    "/matches",
    response_model=list[SpontaneousRideMatchResult],
)
def find_spontaneous_matches(
    body: SpontaneousRideMatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[SpontaneousRideMatchResult]:
    passenger_id = _resolve_passenger_id(body, current_user, db)
    return spontaneous_matching.find_matches(
        db=db,
        pickup_lat=body.pickup_latitude,
        pickup_lon=body.pickup_longitude,
        passenger_user_id=passenger_id,
    )


@router.post(
    "/book",
    response_model=SpontaneousRideBookResponse,
    status_code=status.HTTP_201_CREATED,
)
def book_spontaneous_ride(
    body: SpontaneousRideBookRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SpontaneousRideBookResponse:
    passenger_id = _resolve_passenger_id(body, current_user, db)

    driver_profile: DriverProfile | None = (
        db.query(DriverProfile)
        .filter(DriverProfile.user_id == body.driver_id, DriverProfile.is_active.is_(True))
        .first()
    )
    if not driver_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fahrerprofil nicht gefunden.",
        )

    shift: DriverShift | None = (
        db.query(DriverShift)
        .filter(
            DriverShift.driver_profile_id == driver_profile.id,
            DriverShift.vehicle_id == body.vehicle_id,
            DriverShift.status == ShiftStatus.active,
        )
        .first()
    )
    if not shift:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Fahrer hat keine aktive Schicht mit diesem Fahrzeug.",
        )

    conflict = (
        db.query(TransportRequest.id)
        .filter(
            TransportRequest.assigned_vehicle_id == body.vehicle_id,
            TransportRequest.status.in_(_BOOKING_BLOCKED_STATUSES),
        )
        .first()
    )
    if conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Fahrzeug ist bereits gebucht oder zugewiesen.",
        )

    vehicle: Vehicle | None = db.get(Vehicle, body.vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fahrzeug nicht gefunden.")

    if shift.current_latitude is not None and shift.current_longitude is not None:
        dist_km = spontaneous_matching.haversine_km(
            body.pickup_latitude, body.pickup_longitude,
            shift.current_latitude, shift.current_longitude,
        )
        eta = spontaneous_matching._eta_minutes(dist_km)
    else:
        eta = spontaneous_matching._ETA_MIN_MINUTES

    now = datetime.now(timezone.utc)
    transport_request = TransportRequest(
        requester_user_id=current_user.id,
        passenger_user_id=passenger_id,
        status=TransportRequestStatus.spontaneous_requested,
        is_spontaneous=True,
        pickup_latitude=body.pickup_latitude,
        pickup_longitude=body.pickup_longitude,
        pickup_address=body.pickup_address,
        destination_address=body.destination_address,
        assigned_driver_profile_id=driver_profile.id,
        assigned_vehicle_id=body.vehicle_id,
        assigned_at=now,
    )
    db.add(transport_request)
    db.commit()
    db.refresh(transport_request)

    return SpontaneousRideBookResponse(
        request_id=transport_request.id,
        status=transport_request.status,
        driver_display_name=driver_profile.display_name,
        vehicle_label=vehicle.name,
        estimated_arrival_minutes=eta,
    )


# ── Sprint 12D: Live-Tracking ─────────────────────────────────────────────────

_RIDE_EVENT_LABELS: dict[RideStatusEventType, str] = {
    RideStatusEventType.driver_on_way:       "Fahrer ist unterwegs",
    RideStatusEventType.driver_arrived:      "Fahrer ist angekommen",
    RideStatusEventType.passenger_picked_up: "Fahrgast aufgenommen",
    RideStatusEventType.ride_started:        "Fahrt gestartet",
    RideStatusEventType.ride_completed:      "Fahrt abgeschlossen",
    RideStatusEventType.ride_cancelled:      "Fahrt storniert",
    RideStatusEventType.issue_reported:      "Problem gemeldet",
}

_TRACKING_STATUS_LABELS: dict[TransportRequestStatus, str] = {
    TransportRequestStatus.spontaneous_requested: "Warte auf Fahrerannahme",
    TransportRequestStatus.assigned: "Fahrer angenommen — unterwegs zu Ihnen",
    TransportRequestStatus.completed: "Fahrt abgeschlossen",
    TransportRequestStatus.cancelled: "Fahrt storniert",
    TransportRequestStatus.driver_declined: "Fahrer hat Anfrage abgelehnt",
    TransportRequestStatus.draft: "Entwurf",
    TransportRequestStatus.requested: "Anfrage gestellt",
}


@router.get("/{transport_request_id}/tracking", response_model=SpontaneousRideTracking)
def get_spontaneous_ride_tracking(
    transport_request_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SpontaneousRideTracking:
    tr = db.get(TransportRequest, transport_request_id)
    if not tr or not tr.is_spontaneous:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Spontane Fahrtanfrage nicht gefunden.")

    # Zugriffskontrolle: Fahrgast (eigene Fahrt), Fahrer (eigene Fahrt), Staff
    if current_user.role == UserRole.passenger:
        if tr.passenger_user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Zugriff verweigert.")
    elif current_user.role == UserRole.driver:
        profile = crud_driver_shift.get_driver_profile_for_user(db, current_user.id)
        if not profile or tr.assigned_driver_profile_id != profile.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Zugriff verweigert.")
    elif current_user.role == UserRole.trusted_person:
        rel = (
            db.query(TrustedRelationship)
            .filter(
                TrustedRelationship.trusted_user_id == current_user.id,
                TrustedRelationship.passenger_user_id == tr.passenger_user_id,
                TrustedRelationship.can_view_rides.is_(True),
                TrustedRelationship.status == TrustStatus.active,
            )
            .first()
        )
        if not rel:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Zugriff verweigert.")
    elif current_user.role not in _STAFF_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Zugriff verweigert.")

    label = _TRACKING_STATUS_LABELS.get(tr.status, tr.status.value)

    # Aktuellstes Statusereignis für detaillierteres Label
    latest_event: RideStatusEvent | None = (
        db.query(RideStatusEvent)
        .filter(RideStatusEvent.transport_request_id == transport_request_id)
        .order_by(RideStatusEvent.created_at.desc())
        .first()
    )
    if latest_event:
        label = _RIDE_EVENT_LABELS.get(latest_event.status, label)

    # Wenn Fahrt nicht angenommen: can_track=False, kein Fahrerstandort
    if tr.status != TransportRequestStatus.assigned or not tr.assigned_driver_profile_id:
        return SpontaneousRideTracking(
            transport_request_id=tr.id,
            status=tr.status,
            can_track=False,
            pickup_latitude=tr.pickup_latitude,
            pickup_longitude=tr.pickup_longitude,
            pickup_address=tr.pickup_address,
            destination_address=tr.destination_address,
            ride_status_label=label,
        )

    driver_profile: DriverProfile | None = db.get(DriverProfile, tr.assigned_driver_profile_id)
    vehicle: Vehicle | None = db.get(Vehicle, tr.assigned_vehicle_id) if tr.assigned_vehicle_id else None

    # Aktive Schicht des Fahrers für Standort
    shift: DriverShift | None = (
        db.query(DriverShift)
        .filter(
            DriverShift.driver_profile_id == tr.assigned_driver_profile_id,
            DriverShift.status == ShiftStatus.active,
        )
        .first()
    )

    driver_lat = shift.current_latitude if shift else None
    driver_lon = shift.current_longitude if shift else None
    last_update = shift.updated_at if shift else None
    can_track = driver_lat is not None and driver_lon is not None

    distance_km = None
    eta = None
    if can_track and tr.pickup_latitude is not None and tr.pickup_longitude is not None:
        assert driver_lat is not None and driver_lon is not None
        distance_km = round(
            spontaneous_matching.haversine_km(
                tr.pickup_latitude, tr.pickup_longitude,
                driver_lat, driver_lon,
            ),
            2,
        )
        eta = spontaneous_matching._eta_minutes(distance_km)

    return SpontaneousRideTracking(
        transport_request_id=tr.id,
        status=tr.status,
        can_track=can_track,
        # Kein Telefon, keine E-Mail, nur Anzeigename
        driver_id=driver_profile.user_id if driver_profile else None,
        driver_display_name=driver_profile.display_name if driver_profile else None,
        vehicle_id=vehicle.id if vehicle else None,
        vehicle_label=vehicle.name if vehicle else None,
        driver_latitude=driver_lat,
        driver_longitude=driver_lon,
        pickup_latitude=tr.pickup_latitude,
        pickup_longitude=tr.pickup_longitude,
        pickup_address=tr.pickup_address,
        destination_address=tr.destination_address,
        distance_km=distance_km,
        estimated_arrival_minutes=eta,
        last_location_update=last_update,
        ride_status_label=label,
    )
