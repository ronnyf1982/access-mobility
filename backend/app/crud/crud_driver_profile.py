import uuid

from sqlalchemy.orm import Session

from app.models.driver_profile import DriverProfile
from app.schemas.driver_profile import DriverProfileCreate, DriverProfileUpdate


def get_all(db: Session, active_only: bool = False) -> list[DriverProfile]:
    q = db.query(DriverProfile)
    if active_only:
        q = q.filter(DriverProfile.is_active == True)  # noqa: E712
    return q.order_by(DriverProfile.display_name).all()


def get_by_org(
    db: Session, organization_id: uuid.UUID, active_only: bool = False
) -> list[DriverProfile]:
    q = db.query(DriverProfile).filter(DriverProfile.organization_id == organization_id)
    if active_only:
        q = q.filter(DriverProfile.is_active == True)  # noqa: E712
    return q.order_by(DriverProfile.display_name).all()


def get_by_id(db: Session, driver_id: uuid.UUID) -> DriverProfile | None:
    return db.query(DriverProfile).filter(DriverProfile.id == driver_id).first()


def get_by_user_id(db: Session, user_id: uuid.UUID) -> DriverProfile | None:
    return db.query(DriverProfile).filter(DriverProfile.user_id == user_id).first()


def create(db: Session, payload: DriverProfileCreate) -> DriverProfile:
    driver = DriverProfile(**payload.model_dump())
    db.add(driver)
    db.flush()
    return driver


def update(db: Session, driver: DriverProfile, payload: DriverProfileUpdate) -> DriverProfile:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(driver, key, value)
    db.flush()
    return driver


def soft_delete(db: Session, driver: DriverProfile) -> DriverProfile:
    driver.is_active = False
    db.flush()
    return driver


def hard_delete(db: Session, driver: DriverProfile) -> None:
    db.delete(driver)
    db.flush()
