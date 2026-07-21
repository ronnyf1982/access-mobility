import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.crud import crud_passenger_contact
from app.crud.crud_mobility_profile import get_or_create
from app.models.user import User, UserRole
from app.schemas.passenger_contact import (
    PassengerContactCreate,
    PassengerContactPublic,
    PassengerContactUpdate,
)

router = APIRouter(prefix="/passenger-contacts", tags=["passenger-contacts"])

_PASSENGER_ROLES = {UserRole.passenger, UserRole.trusted_person}


def _require_passenger(current_user: User) -> None:
    if current_user.role not in _PASSENGER_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nur Fahrgäste können Kontakte verwalten.",
        )


def _get_profile_or_404(db: Session, user: User):
    profile, _ = get_or_create(db, user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profil nicht gefunden.")
    return profile


def _get_contact_or_404(db: Session, contact_id: uuid.UUID, profile_id: uuid.UUID):
    contact = crud_passenger_contact.get_contact(db, contact_id)
    if not contact or contact.mobility_profile_id != profile_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kontakt nicht gefunden.")
    return contact


@router.get("/", response_model=list[PassengerContactPublic])
def list_contacts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[PassengerContactPublic]:
    _require_passenger(current_user)
    profile = _get_profile_or_404(db, current_user)
    contacts = crud_passenger_contact.get_profile_contacts(db, profile.id)
    return [PassengerContactPublic.model_validate(c) for c in contacts]


@router.post("/", response_model=PassengerContactPublic, status_code=status.HTTP_201_CREATED)
def create_contact(
    body: PassengerContactCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PassengerContactPublic:
    _require_passenger(current_user)
    profile = _get_profile_or_404(db, current_user)
    contact = crud_passenger_contact.create_contact(db, profile.id, body)
    return PassengerContactPublic.model_validate(contact)


@router.get("/{contact_id}", response_model=PassengerContactPublic)
def get_contact(
    contact_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PassengerContactPublic:
    _require_passenger(current_user)
    profile = _get_profile_or_404(db, current_user)
    contact = _get_contact_or_404(db, contact_id, profile.id)
    return PassengerContactPublic.model_validate(contact)


@router.patch("/{contact_id}", response_model=PassengerContactPublic)
def update_contact(
    contact_id: uuid.UUID,
    body: PassengerContactUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PassengerContactPublic:
    _require_passenger(current_user)
    profile = _get_profile_or_404(db, current_user)
    contact = _get_contact_or_404(db, contact_id, profile.id)
    contact = crud_passenger_contact.update_contact(db, contact, body)
    return PassengerContactPublic.model_validate(contact)


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(
    contact_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    _require_passenger(current_user)
    profile = _get_profile_or_404(db, current_user)
    contact = _get_contact_or_404(db, contact_id, profile.id)
    crud_passenger_contact.delete_contact(db, contact)
