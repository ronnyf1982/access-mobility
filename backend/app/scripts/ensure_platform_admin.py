"""Idempotentes Bootstrap-Script für einen Platform-Admin.

Liest Zugangsdaten ausschließlich aus Umgebungsvariablen.
Kein Passwort wird ausgegeben oder in Dateien gespeichert.

Benötigte Umgebungsvariablen:
    FAHRANDO_BOOTSTRAP_ADMIN_EMAIL
    FAHRANDO_BOOTSTRAP_ADMIN_PASSWORD
    FAHRANDO_BOOTSTRAP_ADMIN_FIRST_NAME
    FAHRANDO_BOOTSTRAP_ADMIN_LAST_NAME

Ausführen:
    cd backend
    python -m app.scripts.ensure_platform_admin

Beispiel (Platzhalter — echtes Passwort lokal eingeben, nie speichern):
    $env:FAHRANDO_BOOTSTRAP_ADMIN_EMAIL="platform-admin@fahrando.test"
    $env:FAHRANDO_BOOTSTRAP_ADMIN_PASSWORD="<HIER_LOKAL_EINTIPPEN>"
    $env:FAHRANDO_BOOTSTRAP_ADMIN_FIRST_NAME="Ronny"
    $env:FAHRANDO_BOOTSTRAP_ADMIN_LAST_NAME="Forschner"
    python -m app.scripts.ensure_platform_admin
    Remove-Item Env:\\FAHRANDO_BOOTSTRAP_ADMIN_PASSWORD
"""
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User, UserRole

_EMAIL_VAR = "FAHRANDO_BOOTSTRAP_ADMIN_EMAIL"
_PW_VAR = "FAHRANDO_BOOTSTRAP_ADMIN_PASSWORD"
_FIRST_VAR = "FAHRANDO_BOOTSTRAP_ADMIN_FIRST_NAME"
_LAST_VAR = "FAHRANDO_BOOTSTRAP_ADMIN_LAST_NAME"


def run() -> None:
    email = os.environ.get(_EMAIL_VAR, "").strip().lower()
    password = os.environ.get(_PW_VAR, "")
    first_name = os.environ.get(_FIRST_VAR, "").strip()
    last_name = os.environ.get(_LAST_VAR, "").strip()

    if not email:
        print(f"[ensure_platform_admin] FEHLER: {_EMAIL_VAR} ist nicht gesetzt. Abbruch.")
        sys.exit(1)
    if not password:
        print(f"[ensure_platform_admin] FEHLER: {_PW_VAR} ist nicht gesetzt. Abbruch.")
        sys.exit(1)
    if not first_name:
        print(f"[ensure_platform_admin] FEHLER: {_FIRST_VAR} ist nicht gesetzt. Abbruch.")
        sys.exit(1)
    if not last_name:
        print(f"[ensure_platform_admin] FEHLER: {_LAST_VAR} ist nicht gesetzt. Abbruch.")
        sys.exit(1)

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()

        if existing:
            if existing.role != UserRole.platform_admin:
                print(
                    f"[ensure_platform_admin] WARNUNG: {email} existiert bereits mit Rolle "
                    f"'{existing.role.value}'. Keine automatische Rollenänderung — manuell prüfen."
                )
            elif not existing.is_active:
                print(
                    f"[ensure_platform_admin] WARNUNG: {email} ist deaktiviert. "
                    "Manuell reaktivieren über Platform-Admin-Benutzerverwaltung."
                )
            else:
                print(
                    f"[ensure_platform_admin] OK: {email} ist bereits aktiver platform_admin. "
                    "Keine Änderung vorgenommen."
                )
            return

        now = datetime.now(timezone.utc)
        user = User(
            email=email,
            password_hash=hash_password(password),
            first_name=first_name,
            last_name=last_name,
            role=UserRole.platform_admin,
            is_active=True,
            onboarding_completed_at=now,
        )
        db.add(user)
        db.commit()
        print(
            f"[ensure_platform_admin] Platform-Admin '{first_name} {last_name}' <{email}> "
            "erfolgreich angelegt. Rolle: platform_admin. Status: aktiv."
        )

    finally:
        db.close()


if __name__ == "__main__":
    run()
