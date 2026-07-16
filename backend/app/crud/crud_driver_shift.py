import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.driver_profile import DriverProfile
from app.models.driver_shift import DriverShift, ShiftStatus
from app.models.vehicle import Vehicle


def normalize_license_plate(plate: str) -> str:
    """Normalisiert ein Kennzeichen: Trim, Großbuchstaben, Leerzeichen → Bindestrich."""
    return plate.strip().upper().replace("  ", " ").replace(" ", "-")


def get_driver_profile_for_user(db: Session, user_id: uuid.UUID) -> DriverProfile | None:
    return (
        db.query(DriverProfile)
        .filter(DriverProfile.user_id == user_id, DriverProfile.is_active == True)  # noqa: E712
        .first()
    )


def get_active_shift(db: Session, driver_profile_id: uuid.UUID) -> DriverShift | None:
    return (
        db.query(DriverShift)
        .filter(
            DriverShift.driver_profile_id == driver_profile_id,
            DriverShift.status.in_([ShiftStatus.active, ShiftStatus.paused]),
        )
        .first()
    )


def find_vehicles_by_license_plate(db: Session, license_plate: str) -> list[Vehicle]:
    normalized = normalize_license_plate(license_plate)
    return (
        db.query(Vehicle)
        .filter(Vehicle.is_active == True, Vehicle.license_plate.ilike(f"%{normalized}%"))  # noqa: E712
        .limit(20)
        .all()
    )


def start_shift(
    db: Session,
    driver_profile_id: uuid.UUID,
    vehicle_id: uuid.UUID,
    notes: str | None = None,
) -> DriverShift:
    shift = DriverShift(
        driver_profile_id=driver_profile_id,
        vehicle_id=vehicle_id,
        status=ShiftStatus.active,
        started_at=datetime.now(timezone.utc),
        notes=notes,
    )
    db.add(shift)
    db.commit()
    db.refresh(shift)
    return shift


def end_shift(db: Session, shift: DriverShift) -> DriverShift:
    shift.status = ShiftStatus.ended
    shift.ended_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(shift)
    return shift


def pause_shift(db: Session, shift: DriverShift) -> DriverShift:
    shift.status = ShiftStatus.paused
    shift.break_started_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(shift)
    return shift


def resume_shift(db: Session, shift: DriverShift) -> DriverShift:
    shift.status = ShiftStatus.active
    shift.break_started_at = None
    db.commit()
    db.refresh(shift)
    return shift
