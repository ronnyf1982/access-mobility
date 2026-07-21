import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.crud import crud_driver_shift, crud_passenger_contact
from app.models.driver_shift import DriverShift, ShiftStatus
from app.models.mobility_profile import MobilityProfile
from app.models.passenger_contact import PassengerContact
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
from app.schemas.emergency import EmergencyContactItem, EmergencyFileResponse
from app.schemas.spontaneous_ride import DriverLocationUpdate, SpontaneousRideRequestItem
from app.schemas.transport_request import TransportRequestListItem
from app.services import emergency_glossary

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


# ── Spontane Fahrtanfragen ────────────────────────────────────────────────────

def _build_spontaneous_request_item(req: TransportRequest, db: Session) -> SpontaneousRideRequestItem:
    passenger = db.get(User, req.passenger_user_id)
    display_name = f"{passenger.first_name} {passenger.last_name}" if passenger else None
    return SpontaneousRideRequestItem(
        id=req.id,
        passenger_user_id=req.passenger_user_id,
        passenger_display_name=display_name,
        pickup_latitude=req.pickup_latitude or 0.0,
        pickup_longitude=req.pickup_longitude or 0.0,
        pickup_address=req.pickup_address,
        destination_address=req.destination_address,
        status=req.status,
        created_at=req.created_at,
    )


@router.get("/spontaneous-ride-requests", response_model=list[SpontaneousRideRequestItem])
def get_spontaneous_ride_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[SpontaneousRideRequestItem]:
    _require_driver(current_user)
    profile = _get_driver_profile_or_404(db, current_user.id)
    requests = (
        db.query(TransportRequest)
        .filter(
            TransportRequest.assigned_driver_profile_id == profile.id,
            TransportRequest.status == TransportRequestStatus.spontaneous_requested,
        )
        .order_by(TransportRequest.created_at.desc())
        .all()
    )
    return [_build_spontaneous_request_item(r, db) for r in requests]


@router.post(
    "/spontaneous-ride-requests/{request_id}/accept",
    response_model=SpontaneousRideRequestItem,
)
def accept_spontaneous_ride_request(
    request_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SpontaneousRideRequestItem:
    _require_driver(current_user)
    profile = _get_driver_profile_or_404(db, current_user.id)
    req = db.get(TransportRequest, request_id)
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fahrtanfrage nicht gefunden.")
    if req.assigned_driver_profile_id != profile.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Diese Anfrage gehört nicht zu Ihrem Profil.")
    if req.status != TransportRequestStatus.spontaneous_requested:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Anfrage ist nicht mehr ausstehend.")
    req.status = TransportRequestStatus.assigned
    req.assigned_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(req)
    return _build_spontaneous_request_item(req, db)


@router.post(
    "/spontaneous-ride-requests/{request_id}/decline",
    response_model=SpontaneousRideRequestItem,
)
def decline_spontaneous_ride_request(
    request_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SpontaneousRideRequestItem:
    _require_driver(current_user)
    profile = _get_driver_profile_or_404(db, current_user.id)
    req = db.get(TransportRequest, request_id)
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fahrtanfrage nicht gefunden.")
    if req.assigned_driver_profile_id != profile.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Diese Anfrage gehört nicht zu Ihrem Profil.")
    if req.status != TransportRequestStatus.spontaneous_requested:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Anfrage ist nicht mehr ausstehend.")
    req.status = TransportRequestStatus.driver_declined
    db.commit()
    db.refresh(req)
    return _build_spontaneous_request_item(req, db)


# ── Fahrerstandort aktualisieren (Sprint 12D) ─────────────────────────────────
# Datenschutz: Standort wird NUR im DriverShift (current_latitude/longitude) gespeichert.
# Kein Standortverlauf, kein Logging, nur letzter bekannter Punkt.
# Fahrer teilt Standort ausschließlich während aktiver Schicht.

@router.post("/location", status_code=status.HTTP_204_NO_CONTENT)
def update_driver_location(
    body: DriverLocationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    _require_driver(current_user)
    profile = _get_driver_profile_or_404(db, current_user.id)

    shift: DriverShift | None = crud_driver_shift.get_active_shift(db, profile.id)
    if not shift:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Keine aktive Schicht. Standort kann nur während aktiver Schicht geteilt werden.",
        )

    if body.transport_request_id:
        tr = db.get(TransportRequest, body.transport_request_id)
        if not tr:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fahrtanfrage nicht gefunden.")
        if tr.assigned_driver_profile_id != profile.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Diese Fahrt ist Ihnen nicht zugewiesen.",
            )
        if tr.status not in (
            TransportRequestStatus.assigned,
            TransportRequestStatus.spontaneous_requested,
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Standort kann nur für aktive Fahrten geteilt werden.",
            )

    shift.current_latitude = body.latitude
    shift.current_longitude = body.longitude
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ── Notfallakte ───────────────────────────────────────────────────────────────

def _visibility(flag_to_driver: bool, flag_in_emergency: bool, emergency_mode: bool) -> bool:
    if emergency_mode:
        return flag_to_driver or flag_in_emergency
    return flag_to_driver


def _build_112_summary(
    profile: MobilityProfile,
    passenger_display_name: str | None,
    location_label: str | None,
    emergency_mode: bool,
    visible_contacts: list[PassengerContact],
) -> str:
    lines: list[str] = [
        "Ich bin Fahrer von Fahrando. Ich habe einen medizinischen Notfall während einer Fahrt.",
    ]
    if location_label:
        lines.append(f"Standort: {location_label}.")
    # Körperdaten
    body_visible = emergency_mode and profile.show_body_data_in_emergency
    gender_label = profile.gender or None
    body_parts: list[str] = []
    if gender_label:
        body_parts.append(gender_label)
    if body_visible and profile.body_height_cm:
        body_parts.append(f"ca. {profile.body_height_cm} cm")
    if body_visible and profile.body_weight_kg:
        body_parts.append(f"ca. {profile.body_weight_kg} kg")
    if body_parts:
        lines.append(f"Fahrgast: {', '.join(body_parts)}.")
    elif passenger_display_name:
        lines.append(f"Fahrgast: {passenger_display_name}.")
    # Behinderungen
    dis_visible = _visibility(
        profile.show_disabilities_to_driver,
        profile.show_disabilities_in_emergency,
        emergency_mode,
    )
    if dis_visible:
        conditions: list[str] = []
        if profile.has_epilepsy:
            conditions.append("Epilepsie")
        if profile.uses_wheelchair:
            conditions.append("Rollstuhlnutzung")
        if profile.is_blind_or_visually_impaired:
            conditions.append("Sehbehinderung")
        if profile.is_deaf_or_hard_of_hearing:
            conditions.append("Hörbehinderung")
        if profile.is_mute:
            conditions.append("Sprechbehinderung")
        if profile.known_conditions:
            conditions.append(profile.known_conditions[:80])
        if conditions:
            lines.append(f"Bekannte Informationen laut freigegebenem Profil: {', '.join(conditions)}.")
    # Medikamente
    med_visible = _visibility(
        profile.show_medication_to_driver,
        profile.show_medication_in_emergency,
        emergency_mode,
    )
    if med_visible and profile.medication_notes:
        lines.append(f"Medikamente laut freigegebenem Profil: {profile.medication_notes[:120]}.")
    # Notfallkontakt
    emergency_contacts = [c for c in visible_contacts if c.is_emergency_contact and c.phone_number]
    if emergency_contacts:
        c = emergency_contacts[0]
        label = c.role_label or "Notfallkontakt"
        lines.append(f"Notfallkontakt: {c.name} ({label}), Tel. {c.phone_number}.")
    return " ".join(lines)


@router.get(
    "/transport-requests/{request_id}/emergency-file",
    response_model=EmergencyFileResponse,
)
def get_emergency_file(
    request_id: uuid.UUID,
    emergency_mode: bool = Query(default=False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> EmergencyFileResponse:
    _require_driver(current_user)
    driver_profile = _get_driver_profile_or_404(db, current_user.id)

    tr = db.get(TransportRequest, request_id)
    if not tr:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fahrtanfrage nicht gefunden.")
    if tr.assigned_driver_profile_id != driver_profile.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Diese Fahrt ist Ihnen nicht zugewiesen.",
        )

    # Fahrgastprofil laden
    profile: MobilityProfile | None = (
        db.query(MobilityProfile)
        .filter(MobilityProfile.user_id == tr.passenger_user_id)
        .first()
    )

    passenger_user = db.get(User, tr.passenger_user_id)
    passenger_display_name: str | None = None
    if passenger_user:
        passenger_display_name = f"{passenger_user.first_name} {passenger_user.last_name}".strip() or None

    # Wenn kein Profil existiert, leere Notfallakte zurückgeben
    if not profile:
        return EmergencyFileResponse(
            transport_request_id=request_id,
            passenger_display_name=passenger_display_name,
            emergency_mode=emergency_mode,
            disabilities_visible=False,
            has_epilepsy=False,
            is_mute=False,
            is_deaf_or_hard_of_hearing=False,
            uses_wheelchair=False,
            is_blind_or_visually_impaired=False,
            other_disabilities_notes=None,
            known_conditions=None,
            medication_visible=False,
            medication_notes=None,
            allergy_notes=None,
            emergency_notes_visible=False,
            emergency_care_notes=None,
            what_helps_notes=None,
            what_to_avoid_notes=None,
            additional_emergency_notes=None,
            communication_notes_visible=False,
            communication_notes=None,
            body_data_visible=False,
            body_height_cm=None,
            body_weight_kg=None,
            gender=None,
            visible_contacts=[],
            primary_emergency_contact=None,
            has_callable_emergency_contact=False,
            emergency_summary_for_112=f"Ich bin Fahrer von Fahrando. Ich habe einen Notfall. Standort: {tr.pickup_address or 'unbekannt'}.",
            current_location_label=tr.pickup_address,
            pickup_latitude=tr.pickup_latitude,
            pickup_longitude=tr.pickup_longitude,
            glossary_entries=[],
            medical_disclaimer="Kein Mobilitätsprofil für diesen Fahrgast hinterlegt.",
        )

    # Sichtbarkeitsflags auswerten
    dis_visible = _visibility(
        profile.show_disabilities_to_driver,
        profile.show_disabilities_in_emergency,
        emergency_mode,
    )
    med_visible = _visibility(
        profile.show_medication_to_driver,
        profile.show_medication_in_emergency,
        emergency_mode,
    )
    emerg_visible = _visibility(
        profile.show_emergency_notes_to_driver,
        profile.show_emergency_notes_in_emergency,
        emergency_mode,
    )
    comm_visible = _visibility(
        profile.show_communication_notes_to_driver,
        profile.show_communication_notes_in_emergency,
        emergency_mode,
    )
    body_visible = emergency_mode and profile.show_body_data_in_emergency
    contacts_visible = _visibility(
        profile.show_contacts_to_driver,
        profile.show_contacts_in_emergency,
        emergency_mode,
    )

    # Kontakte laden
    all_contacts = crud_passenger_contact.get_profile_contacts(db, profile.id)
    visible_contacts: list[PassengerContact] = []
    if contacts_visible:
        visible_contacts = [
            c for c in all_contacts
            if (not emergency_mode and c.visible_to_driver)
            or (emergency_mode and (c.visible_to_driver or c.visible_in_emergency))
        ]

    def _contact_item(c: PassengerContact) -> EmergencyContactItem:
        return EmergencyContactItem(
            id=c.id,
            name=c.name,
            phone_number=c.phone_number,
            role_label=c.role_label,
            contact_type=c.contact_type.value,
            is_emergency_contact=c.is_emergency_contact,
            callable_in_emergency=c.callable_in_emergency,
            priority=c.priority,
        )

    contact_items = [_contact_item(c) for c in visible_contacts]
    primary_emergency = next(
        (item for item in contact_items if item.is_emergency_contact and item.phone_number),
        None,
    )
    has_callable = any(item.callable_in_emergency and item.phone_number for item in contact_items)

    location_label = tr.pickup_address
    if not location_label and tr.pickup_latitude and tr.pickup_longitude:
        location_label = f"GPS {tr.pickup_latitude:.4f}, {tr.pickup_longitude:.4f}"

    summary = _build_112_summary(
        profile=profile,
        passenger_display_name=passenger_display_name,
        location_label=location_label,
        emergency_mode=emergency_mode,
        visible_contacts=visible_contacts,
    )

    glossary_entries = emergency_glossary.get_relevant_entries_for_profile(profile, emergency_mode)

    return EmergencyFileResponse(
        transport_request_id=request_id,
        passenger_display_name=passenger_display_name,
        emergency_mode=emergency_mode,
        disabilities_visible=dis_visible,
        has_epilepsy=profile.has_epilepsy if dis_visible else False,
        is_mute=profile.is_mute if dis_visible else False,
        is_deaf_or_hard_of_hearing=profile.is_deaf_or_hard_of_hearing if dis_visible else False,
        uses_wheelchair=profile.uses_wheelchair if dis_visible else False,
        is_blind_or_visually_impaired=profile.is_blind_or_visually_impaired if dis_visible else False,
        other_disabilities_notes=profile.other_disabilities_notes if dis_visible else None,
        known_conditions=profile.known_conditions if dis_visible else None,
        medication_visible=med_visible,
        medication_notes=profile.medication_notes if med_visible else None,
        allergy_notes=profile.allergy_notes if med_visible else None,
        emergency_notes_visible=emerg_visible,
        emergency_care_notes=profile.emergency_care_notes if emerg_visible else None,
        what_helps_notes=profile.what_helps_notes if emerg_visible else None,
        what_to_avoid_notes=profile.what_to_avoid_notes if emerg_visible else None,
        additional_emergency_notes=profile.additional_emergency_notes if emerg_visible else None,
        communication_notes_visible=comm_visible,
        communication_notes=profile.communication_notes if comm_visible else None,
        body_data_visible=body_visible,
        body_height_cm=profile.body_height_cm if body_visible else None,
        body_weight_kg=profile.body_weight_kg if body_visible else None,
        gender=profile.gender if body_visible else None,
        visible_contacts=contact_items,
        primary_emergency_contact=primary_emergency,
        has_callable_emergency_contact=has_callable,
        emergency_summary_for_112=summary,
        current_location_label=location_label,
        pickup_latitude=tr.pickup_latitude,
        pickup_longitude=tr.pickup_longitude,
        glossary_entries=glossary_entries,
        medical_disclaimer=(
            "Diese Informationen basieren auf freiwilligen Angaben des Fahrgastes. "
            "Sie ersetzen keine professionelle medizinische Diagnose oder Behandlung. "
            "Im Zweifel immer Notruf 112 wählen."
        ),
    )
