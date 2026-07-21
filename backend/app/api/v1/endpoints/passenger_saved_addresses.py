import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.crud import crud_passenger_saved_address
from app.crud.crud_mobility_profile import get_or_create
from app.models.user import User, UserRole
from app.schemas.passenger_saved_address import (
    PassengerSavedAddressCreate,
    PassengerSavedAddressPublic,
    PassengerSavedAddressUpdate,
)

router = APIRouter(prefix="/passenger-saved-addresses", tags=["passenger-saved-addresses"])

_ALLOWED_ROLES = {UserRole.passenger, UserRole.trusted_person}


def _require_allowed(current_user: User) -> None:
    if current_user.role not in _ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Kein Zugriff auf gespeicherte Adressen.",
        )


def _get_profile_or_404(db: Session, user: User):
    profile, _ = get_or_create(db, user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profil nicht gefunden.")
    return profile


def _get_address_or_404(db: Session, address_id: uuid.UUID, profile_id: uuid.UUID):
    addr = crud_passenger_saved_address.get_address(db, address_id)
    if not addr or addr.mobility_profile_id != profile_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Adresse nicht gefunden."
        )
    return addr


@router.get("/", response_model=list[PassengerSavedAddressPublic])
def list_addresses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[PassengerSavedAddressPublic]:
    _require_allowed(current_user)
    profile = _get_profile_or_404(db, current_user)
    addrs = crud_passenger_saved_address.get_profile_addresses(db, profile.id)
    return [PassengerSavedAddressPublic.model_validate(a) for a in addrs]


@router.post("/", response_model=PassengerSavedAddressPublic, status_code=status.HTTP_201_CREATED)
def create_address(
    body: PassengerSavedAddressCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PassengerSavedAddressPublic:
    _require_allowed(current_user)
    profile = _get_profile_or_404(db, current_user)
    addr = crud_passenger_saved_address.create_address(db, profile.id, body)
    return PassengerSavedAddressPublic.model_validate(addr)


@router.patch("/{address_id}", response_model=PassengerSavedAddressPublic)
def update_address(
    address_id: uuid.UUID,
    body: PassengerSavedAddressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PassengerSavedAddressPublic:
    _require_allowed(current_user)
    profile = _get_profile_or_404(db, current_user)
    addr = _get_address_or_404(db, address_id, profile.id)
    addr = crud_passenger_saved_address.update_address(db, addr, body)
    return PassengerSavedAddressPublic.model_validate(addr)


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_address(
    address_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    _require_allowed(current_user)
    profile = _get_profile_or_404(db, current_user)
    addr = _get_address_or_404(db, address_id, profile.id)
    crud_passenger_saved_address.delete_address(db, addr)
