import uuid

from sqlalchemy.orm import Session

from app.models.passenger_saved_address import PassengerSavedAddress
from app.schemas.passenger_saved_address import (
    PassengerSavedAddressCreate,
    PassengerSavedAddressUpdate,
)


def get_profile_addresses(
    db: Session, mobility_profile_id: uuid.UUID
) -> list[PassengerSavedAddress]:
    return (
        db.query(PassengerSavedAddress)
        .filter(PassengerSavedAddress.mobility_profile_id == mobility_profile_id)
        .order_by(PassengerSavedAddress.created_at.asc())
        .all()
    )


def get_address(db: Session, address_id: uuid.UUID) -> PassengerSavedAddress | None:
    return db.get(PassengerSavedAddress, address_id)


def create_address(
    db: Session,
    mobility_profile_id: uuid.UUID,
    data: PassengerSavedAddressCreate,
) -> PassengerSavedAddress:
    addr = PassengerSavedAddress(
        id=uuid.uuid4(),
        mobility_profile_id=mobility_profile_id,
        **data.model_dump(),
    )
    db.add(addr)
    db.commit()
    db.refresh(addr)
    return addr


def update_address(
    db: Session,
    address: PassengerSavedAddress,
    data: PassengerSavedAddressUpdate,
) -> PassengerSavedAddress:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(address, field, value)
    db.commit()
    db.refresh(address)
    return address


def delete_address(db: Session, address: PassengerSavedAddress) -> None:
    db.delete(address)
    db.commit()
