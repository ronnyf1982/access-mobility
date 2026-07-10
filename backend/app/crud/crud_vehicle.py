import uuid

from sqlalchemy.orm import Session

from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleUpdate


def get_all(db: Session, active_only: bool = False) -> list[Vehicle]:
    q = db.query(Vehicle)
    if active_only:
        q = q.filter(Vehicle.is_active == True)  # noqa: E712
    return q.order_by(Vehicle.name).all()


def get_by_org(
    db: Session, organization_id: uuid.UUID, active_only: bool = False
) -> list[Vehicle]:
    q = db.query(Vehicle).filter(Vehicle.organization_id == organization_id)
    if active_only:
        q = q.filter(Vehicle.is_active == True)  # noqa: E712
    return q.order_by(Vehicle.name).all()


def get_by_id(db: Session, vehicle_id: uuid.UUID) -> Vehicle | None:
    return db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()


def create(db: Session, payload: VehicleCreate) -> Vehicle:
    vehicle = Vehicle(**payload.model_dump())
    db.add(vehicle)
    db.flush()
    return vehicle


def update(db: Session, vehicle: Vehicle, payload: VehicleUpdate) -> Vehicle:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(vehicle, key, value)
    db.flush()
    return vehicle


def soft_delete(db: Session, vehicle: Vehicle) -> Vehicle:
    vehicle.is_active = False
    db.flush()
    return vehicle


def hard_delete(db: Session, vehicle: Vehicle) -> None:
    db.delete(vehicle)
    db.flush()
