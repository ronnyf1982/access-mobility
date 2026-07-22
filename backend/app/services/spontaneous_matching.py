"""Spontaneous ride matching service (Sprint 12B).

Finds available drivers/vehicles near a pickup point that match the
passenger's mobility profile. No external routing API — Haversine
straight-line distance with a conservative ETA estimate.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from math import atan2, cos, radians, sin, sqrt

from sqlalchemy.orm import Session

from app.models.driver_profile import DriverProfile
from app.models.driver_shift import DriverShift, ShiftStatus
from app.models.mobility_profile import MobilityProfile, WheelchairType
from app.models.transport_request import TransportRequest, TransportRequestStatus
from app.models.vehicle import Vehicle
from app.schemas.spontaneous_ride import SpontaneousRideMatchResult

_MAX_REMATCH_ATTEMPT = 3

_BLOCKING_STATUSES = {TransportRequestStatus.assigned, TransportRequestStatus.spontaneous_requested}

_AVG_SPEED_KMH = 30.0
_ETA_MIN_MINUTES = 3


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlam = radians(lon2 - lon1)
    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlam / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(max(0.0, 1.0 - a)))


def _eta_minutes(distance_km: float) -> int:
    return max(_ETA_MIN_MINUTES, int(distance_km / _AVG_SPEED_KMH * 60))


def _check_capabilities(
    vehicle: Vehicle,
    profile: MobilityProfile | None,
) -> list[str] | None:
    """Returns matched capability labels, or None if a required capability is missing."""
    if profile is None:
        return []

    matched: list[str] = []

    if profile.needs_ramp:
        if not vehicle.has_ramp:
            return None
        matched.append("Rampe")

    if profile.needs_lift:
        if not vehicle.has_lift:
            return None
        matched.append("Lift")

    if profile.requires_wheelchair_space:
        if vehicle.wheelchair_space_count < 1:
            return None
        matched.append("Rollstuhlplatz")

    if profile.uses_wheelchair and profile.wheelchair_type == WheelchairType.electric:
        if not vehicle.supports_electric_wheelchair:
            return None
        matched.append("Elektro-Rollstuhl")

    if profile.needs_stretcher_transport:
        if not vehicle.supports_stretcher_transport:
            return None
        matched.append("Liegendtransport")

    if profile.requires_transport_chair:
        if not vehicle.has_transport_chair:
            return None
        matched.append("Transportrollstuhl")

    if profile.requires_oxygen_mount:
        if not vehicle.has_oxygen_mount:
            return None
        matched.append("Sauerstoffhalterung")

    if profile.requires_infusion_mount:
        if not vehicle.has_infusion_mount:
            return None
        matched.append("Infusionshalterung")

    if profile.requires_two_person_assistance:
        if not vehicle.supports_two_person_crew:
            return None
        matched.append("Zweimann-Besatzung")

    return matched


def find_matches(
    db: Session,
    pickup_lat: float,
    pickup_lon: float,
    passenger_user_id: uuid.UUID,
    excluded_driver_profile_ids: set[uuid.UUID] | None = None,
) -> list[SpontaneousRideMatchResult]:
    # Alle blocked vehicle_ids (aktive Fahrtanfragen)
    blocked_vehicle_ids: set[uuid.UUID] = {
        row[0]
        for row in db.query(TransportRequest.assigned_vehicle_id)
        .filter(
            TransportRequest.assigned_vehicle_id.isnot(None),
            TransportRequest.status.in_(list(_BLOCKING_STATUSES)),
        )
        .all()
    }

    # Fahrer mit angenommener spontaner Fahrt sind nicht verfügbar
    blocked_driver_profile_ids: set[uuid.UUID] = {
        row[0]
        for row in db.query(TransportRequest.assigned_driver_profile_id)
        .filter(
            TransportRequest.assigned_driver_profile_id.isnot(None),
            TransportRequest.is_spontaneous.is_(True),
            TransportRequest.status == TransportRequestStatus.assigned,
        )
        .all()
    }

    # Zusätzlich ausgeschlossene Fahrer (z. B. bereits abgelehnte bei Rematch)
    if excluded_driver_profile_ids:
        blocked_driver_profile_ids |= excluded_driver_profile_ids

    # Mobilitätsprofil des Fahrgasts
    profile: MobilityProfile | None = (
        db.query(MobilityProfile)
        .filter(MobilityProfile.user_id == passenger_user_id)
        .first()
    )

    # Aktive Schichten mit Standort
    active_shifts: list[DriverShift] = (
        db.query(DriverShift)
        .filter(
            DriverShift.status == ShiftStatus.active,
            DriverShift.current_latitude.isnot(None),
            DriverShift.current_longitude.isnot(None),
        )
        .all()
    )

    results: list[SpontaneousRideMatchResult] = []

    for shift in active_shifts:
        if shift.vehicle_id in blocked_vehicle_ids:
            continue
        if shift.driver_profile_id in blocked_driver_profile_ids:
            continue

        vehicle = db.get(Vehicle, shift.vehicle_id)
        if not vehicle or not vehicle.is_active:
            continue

        driver_profile = db.get(DriverProfile, shift.driver_profile_id)
        if not driver_profile or not driver_profile.is_active:
            continue

        caps = _check_capabilities(vehicle, profile)
        if caps is None:
            continue

        assert shift.current_latitude is not None
        assert shift.current_longitude is not None
        dist = haversine_km(
            pickup_lat, pickup_lon,
            shift.current_latitude, shift.current_longitude,
        )
        results.append(
            SpontaneousRideMatchResult(
                driver_id=driver_profile.user_id,
                driver_display_name=driver_profile.display_name,
                vehicle_id=vehicle.id,
                vehicle_label=vehicle.name,
                vehicle_type=vehicle.vehicle_type.value,
                vehicle_latitude=shift.current_latitude,
                vehicle_longitude=shift.current_longitude,
                distance_km=round(dist, 2),
                estimated_arrival_minutes=_eta_minutes(dist),
                matched_capabilities=caps,
                can_accept_now=True,
            )
        )

    results.sort(key=lambda r: r.distance_km)
    return results


def find_rematch_match(
    db: Session,
    original_tr: TransportRequest,
) -> SpontaneousRideMatchResult | None:
    """Find a replacement driver for a declined/timed-out spontaneous ride.

    Excludes all driver profiles that have already been tried in this rematch group.
    """
    excluded: set[uuid.UUID] = set()
    if original_tr.rematch_group_id:
        excluded = {
            row[0]
            for row in db.query(TransportRequest.assigned_driver_profile_id)
            .filter(
                TransportRequest.rematch_group_id == original_tr.rematch_group_id,
                TransportRequest.assigned_driver_profile_id.isnot(None),
            )
            .all()
        }
    elif original_tr.assigned_driver_profile_id:
        excluded = {original_tr.assigned_driver_profile_id}

    if original_tr.pickup_latitude is None or original_tr.pickup_longitude is None:
        return None

    results = find_matches(
        db=db,
        pickup_lat=original_tr.pickup_latitude,
        pickup_lon=original_tr.pickup_longitude,
        passenger_user_id=original_tr.passenger_user_id,
        excluded_driver_profile_ids=excluded,
    )
    return results[0] if results else None


def do_rematch(db: Session, original_tr: TransportRequest) -> TransportRequest | None:
    """Setzt alten TR auf driver_declined und erstellt neuen TR für Ersatzfahrer (falls verfügbar).

    Respektiert _MAX_REMATCH_ATTEMPT. Kein DB-Commit — Aufrufer muss committen.
    """
    if original_tr.rematch_group_id is None or original_tr.rematch_attempt >= _MAX_REMATCH_ATTEMPT:
        original_tr.status = TransportRequestStatus.driver_declined
        db.flush()
        return None

    match = find_rematch_match(db, original_tr)
    original_tr.status = TransportRequestStatus.driver_declined
    db.flush()

    if not match:
        return None

    new_profile = db.query(DriverProfile).filter(
        DriverProfile.user_id == match.driver_id,
        DriverProfile.is_active.is_(True),
    ).first()
    if not new_profile:
        return None

    new_tr = TransportRequest(
        requester_user_id=original_tr.requester_user_id,
        passenger_user_id=original_tr.passenger_user_id,
        status=TransportRequestStatus.spontaneous_requested,
        is_spontaneous=True,
        pickup_latitude=original_tr.pickup_latitude,
        pickup_longitude=original_tr.pickup_longitude,
        pickup_address=original_tr.pickup_address,
        destination_address=original_tr.destination_address,
        assigned_driver_profile_id=new_profile.id,
        assigned_vehicle_id=match.vehicle_id,
        assigned_at=datetime.now(timezone.utc),
        rematch_group_id=original_tr.rematch_group_id,
        rematch_attempt=original_tr.rematch_attempt + 1,
    )
    db.add(new_tr)
    db.flush()
    return new_tr
