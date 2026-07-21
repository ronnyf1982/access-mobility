"""Delete PassengerContact rows where name or phone_number is NULL/empty/whitespace.

Targets the demo passenger (passenger@access.test) by default.
Safe: never deletes contacts that have BOTH a non-blank name AND phone_number.
Idempotent: running multiple times produces the same result.

Local:
    cd backend
    .venv\\Scripts\\Activate.ps1
    python -m app.scripts.cleanup_empty_passenger_contacts

Railway console:
    /opt/venv/bin/python -m app.scripts.cleanup_empty_passenger_contacts

Dry-run (no deletes):
    python -m app.scripts.cleanup_empty_passenger_contacts --dry-run
"""
from __future__ import annotations

import sys

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.mobility_profile import MobilityProfile
from app.models.passenger_contact import PassengerContact
from app.models.user import User

_DEMO_EMAIL = "passenger@access.test"
_FALLBACK_LABEL = "Unbenannter Kontakt"


def _is_invalid(c: PassengerContact) -> bool:
    name_ok = bool(c.name and c.name.strip() and c.name.strip() != _FALLBACK_LABEL)
    phone_ok = bool(c.phone_number and c.phone_number.strip())
    return not (name_ok and phone_ok)


def run_cleanup(db: Session, *, dry_run: bool = False, email: str = _DEMO_EMAIL) -> dict:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        print(f"Nutzer '{email}' nicht gefunden.")
        return {"found": 0, "deleted": 0, "remaining": 0}

    profile = db.query(MobilityProfile).filter(MobilityProfile.user_id == user.id).first()
    if not profile:
        print(f"Kein Mobilitätsprofil für {email}.")
        return {"found": 0, "deleted": 0, "remaining": 0}

    all_contacts = (
        db.query(PassengerContact)
        .filter(PassengerContact.mobility_profile_id == profile.id)
        .all()
    )

    to_delete = [c for c in all_contacts if _is_invalid(c)]
    to_keep = [c for c in all_contacts if not _is_invalid(c)]

    print(f"Nutzer:            {email}")
    print(f"Kontakte gesamt:   {len(all_contacts)}")
    print(f"Ungültig (löschen):{len(to_delete)}")
    print(f"Gültig (behalten): {len(to_keep)}")

    if dry_run:
        print("DRY RUN — keine Datenbankänderungen.")
        for c in to_delete:
            print(f"  [würde löschen] id={c.id} | name={c.name!r} | phone={c.phone_number!r}")
        return {"found": len(all_contacts), "deleted": 0, "remaining": len(to_keep)}

    for c in to_delete:
        db.delete(c)
    db.commit()

    remaining = (
        db.query(PassengerContact)
        .filter(PassengerContact.mobility_profile_id == profile.id)
        .count()
    )
    print(f"Gelöscht:          {len(to_delete)}")
    print(f"Verbleibend:       {remaining}")

    return {"found": len(all_contacts), "deleted": len(to_delete), "remaining": remaining}


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    db = SessionLocal()
    try:
        run_cleanup(db, dry_run=dry)
    finally:
        db.close()
