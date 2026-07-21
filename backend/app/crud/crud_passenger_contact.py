import uuid

from sqlalchemy.orm import Session

from app.models.passenger_contact import PassengerContact
from app.schemas.passenger_contact import PassengerContactCreate, PassengerContactUpdate


def get_profile_contacts(db: Session, mobility_profile_id: uuid.UUID) -> list[PassengerContact]:
    return (
        db.query(PassengerContact)
        .filter(PassengerContact.mobility_profile_id == mobility_profile_id)
        .order_by(PassengerContact.priority.asc(), PassengerContact.created_at.asc())
        .all()
    )


def get_contact(db: Session, contact_id: uuid.UUID) -> PassengerContact | None:
    return db.get(PassengerContact, contact_id)


def create_contact(
    db: Session,
    mobility_profile_id: uuid.UUID,
    data: PassengerContactCreate,
) -> PassengerContact:
    contact = PassengerContact(
        id=uuid.uuid4(),
        mobility_profile_id=mobility_profile_id,
        **data.model_dump(),
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


def update_contact(
    db: Session,
    contact: PassengerContact,
    data: PassengerContactUpdate,
) -> PassengerContact:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(contact, field, value)
    db.commit()
    db.refresh(contact)
    return contact


def delete_contact(db: Session, contact: PassengerContact) -> None:
    db.delete(contact)
    db.commit()
