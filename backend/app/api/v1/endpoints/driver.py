from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.crud import crud_driver_shift
from app.models.driver_shift import ShiftStatus
from app.models.transport_request import TransportRequest, TransportRequestStatus
from app.models.user import User, UserRole
from app.models.vehicle import Vehicle
from app.schemas.driver_shift import (
    DriverDashboardContext,
    DriverProfileBrief,
    DriverShiftPublic,
    DriverShiftStartRequest,
    DriverShiftWithVehicle,
    VehicleBrief,
)
from app.schemas.transport_request import TransportRequestListItem

router = APIRouter(prefix="/driver", tags=["driver"])

_ALLOWED_ROLES = {UserRole.driver}
_READ_ROLES = {UserRole.driver, UserRole.provider_admin, UserRole.dispatcher, UserRole.platform_admin}


def _require_driver(current_user: User) -> None:
    if current_user.role not in _ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nur Fahrer dürfen eigene Schichten verwalten.",
        )


def _get_driver_profile_or_404(db: Session, user_id):
    profile = crud_driver_shift.get_driver_profile_for_user(db, user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kein aktives Fahrerprofil für diesen Nutzer gefunden.",
        )
    return profile


def _vehicle_brief(vehicle: Vehicle) -> VehicleBrief:
    return VehicleBrief.model_validate(vehicle)


def _shift_with_vehicle(shift, db: Session) -> DriverShiftWithVehicle:
    vehicle = db.get(Vehicle, shift.vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=500, detail="Fahrzeug nicht gefunden.")
    return DriverShiftWithVehicle(
        shift=DriverShiftPublic.model_validate(shift),
        vehicle=_vehicle_brief(vehicle),
    )


# ── Dashboard-Kontext (Profil + Standardfahrzeug + aktive Schicht) ────────────

@router.get("/me", response_model=DriverDashboardContext)
def get_driver_context(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DriverDashboardContext:
    _require_driver(current_user)
    profile = _get_driver_profile_or_404(db, current_user.id)

    default_vehicle: VehicleBrief | None = None
    if profile.default_vehicle_id:
        v = db.get(Vehicle, profile.default_vehicle_id)
        if v and v.is_active:
            default_vehicle = _vehicle_brief(v)

    shift = crud_driver_shift.get_active_shift(db, profile.id)
    active_shift: DriverShiftWithVehicle | None = None
    if shift:
        active_shift = _shift_with_vehicle(shift, db)

    return DriverDashboardContext(
        profile=DriverProfileBrief.model_validate(profile),
        default_vehicle=default_vehicle,
        active_shift=active_shift,
    )


# ── Aktuelle Schicht ──────────────────────────────────────────────────────────

@router.get("/shift/current", response_model=DriverShiftWithVehicle | None)
def get_current_shift(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DriverShiftWithVehicle | None:
    _require_driver(current_user)
    profile = _get_driver_profile_or_404(db, current_user.id)
    shift = crud_driver_shift.get_active_shift(db, profile.id)
    if not shift:
        return None
    return _shift_with_vehicle(shift, db)


# ── Schicht starten ───────────────────────────────────────────────────────────

@router.post("/shift/start", response_model=DriverShiftWithVehicle, status_code=status.HTTP_201_CREATED)
def start_shift(
    body: DriverShiftStartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DriverShiftWithVehicle:
    _require_driver(current_user)
    profile = _get_driver_profile_or_404(db, current_user.id)

    existing = crud_driver_shift.get_active_shift(db, profile.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Es läuft bereits eine aktive oder pausierte Schicht. Bitte beenden Sie diese zuerst.",
        )

    # Fahrzeug ermitteln: vehicle_id > license_plate > Standardfahrzeug des Profils
    if body.vehicle_id:
        vehicle = db.get(Vehicle, body.vehicle_id)
        if not vehicle or not vehicle.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fahrzeug nicht gefunden oder nicht aktiv.",
            )
    elif body.license_plate:
        matches = crud_driver_shift.find_vehicles_by_license_plate(db, body.license_plate)
        if not matches:
            normalized = crud_driver_shift.normalize_license_plate(body.license_plate)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Kein aktives Fahrzeug mit Kennzeichen '{normalized}' gefunden.",
            )
        if len(matches) > 1:
            plates = ", ".join(v.license_plate for v in matches)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Mehrere Fahrzeuge mit diesem Kennzeichen gefunden: {plates}. Bitte vehicle_id verwenden.",
            )
        vehicle = matches[0]
    elif profile.default_vehicle_id:
        vehicle = db.get(Vehicle, profile.default_vehicle_id)
        if not vehicle or not vehicle.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Standardfahrzeug des Profils nicht gefunden oder nicht aktiv.",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Bitte vehicle_id, license_plate oder ein hinterlegtes Standardfahrzeug angeben.",
        )

    shift = crud_driver_shift.start_shift(db, profile.id, vehicle.id, body.notes)
    return DriverShiftWithVehicle(
        shift=DriverShiftPublic.model_validate(shift),
        vehicle=_vehicle_brief(vehicle),
    )


# ── Schicht beenden ───────────────────────────────────────────────────────────

@router.post("/shift/end", response_model=DriverShiftPublic)
def end_shift(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DriverShiftPublic:
    _require_driver(current_user)
    profile = _get_driver_profile_or_404(db, current_user.id)
    shift = crud_driver_shift.get_active_shift(db, profile.id)
    if not shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keine aktive Schicht gefunden.",
        )
    shift = crud_driver_shift.end_shift(db, shift)
    return DriverShiftPublic.model_validate(shift)


# ── Pause beginnen ────────────────────────────────────────────────────────────

@router.post("/shift/pause", response_model=DriverShiftPublic)
def pause_shift(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DriverShiftPublic:
    _require_driver(current_user)
    profile = _get_driver_profile_or_404(db, current_user.id)
    shift = crud_driver_shift.get_active_shift(db, profile.id)
    if not shift or shift.status != ShiftStatus.active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Keine aktive Schicht (kein Pausen-Start möglich).",
        )
    shift = crud_driver_shift.pause_shift(db, shift)
    return DriverShiftPublic.model_validate(shift)


# ── Pause beenden ─────────────────────────────────────────────────────────────

@router.post("/shift/resume", response_model=DriverShiftPublic)
def resume_shift(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DriverShiftPublic:
    _require_driver(current_user)
    profile = _get_driver_profile_or_404(db, current_user.id)
    shift = crud_driver_shift.get_active_shift(db, profile.id)
    if not shift or shift.status != ShiftStatus.paused:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Keine pausierte Schicht gefunden.",
        )
    shift = crud_driver_shift.resume_shift(db, shift)
    return DriverShiftPublic.model_validate(shift)


# ── Fahrzeugsuche per Kennzeichen ─────────────────────────────────────────────

@router.get("/vehicles/search")
def search_vehicle_by_license_plate(
    license_plate: str = Query(..., min_length=2, description="Kennzeichen (z. B. M-AM-1234)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[VehicleBrief]:
    if current_user.role not in _READ_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Zugriff verweigert.")
    matches = crud_driver_shift.find_vehicles_by_license_plate(db, license_plate)
    return [_vehicle_brief(v) for v in matches]


# ── Zugewiesene Aufträge ─────────────────────────────────────────────────────

@router.get("/assignments", response_model=list[TransportRequestListItem])
def get_driver_assignments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[TransportRequestListItem]:
    _require_driver(current_user)
    profile = _get_driver_profile_or_404(db, current_user.id)
    requests = (
        db.query(TransportRequest)
        .filter(
            TransportRequest.assigned_driver_profile_id == profile.id,
            TransportRequest.status == TransportRequestStatus.assigned,
        )
        .order_by(TransportRequest.pickup_date.asc(), TransportRequest.pickup_time.asc())
        .all()
    )
    return [TransportRequestListItem.model_validate(r) for r in requests]
