import uuid

from sqlalchemy.orm import Session

from app.models.mobility_profile import MobilityProfile
from app.schemas.mobility_profile import MobilityProfileUpdate


def get_by_user_id(db: Session, user_id: uuid.UUID) -> MobilityProfile | None:
    return db.query(MobilityProfile).filter(MobilityProfile.user_id == user_id).first()


def get_or_create(db: Session, user_id: uuid.UUID) -> tuple[MobilityProfile, bool]:
    """Gibt bestehendes Profil zurück oder legt ein leeres an.

    Returns: (profile, created) — created=True wenn neu angelegt.
    """
    profile = get_by_user_id(db, user_id)
    if profile:
        return profile, False
    profile = MobilityProfile(user_id=user_id)
    db.add(profile)
    db.flush()
    return profile, True


def upsert(db: Session, user_id: uuid.UUID, payload: MobilityProfileUpdate) -> MobilityProfile:
    """Erstellt oder aktualisiert das Profil. Nur gesendete Felder werden überschrieben."""
    profile, _ = get_or_create(db, user_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, key, value)
    db.flush()
    return profile
