"""Seed-Skript für Demo-Daten (Entwicklung).

Ausführen:
    cd backend
    python -m app.scripts.seed_demo_data

Idempotent: Bereits vorhandene Einträge werden übersprungen.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.membership import OrganizationMembership
from app.models.organization import Organization, OrganizationType
from app.models.trusted_relationship import TrustedRelationship, TrustStatus
from app.models.user import User, UserRole

DEMO_PASSWORD = "Access123!"

DEMO_USERS = [
    {
        "email": "passenger@access.test",
        "first_name": "Max",
        "last_name": "Muster",
        "role": UserRole.passenger,
        "phone": "+49 30 1234560",
    },
    {
        "email": "relative@access.test",
        "first_name": "Anna",
        "last_name": "Muster",
        "role": UserRole.trusted_person,
        "phone": "+49 30 1234561",
    },
    {
        "email": "orgadmin@access.test",
        "first_name": "Werner",
        "last_name": "Brandt",
        "role": UserRole.organization_admin,
        "phone": "+49 30 1234562",
    },
    {
        "email": "coordinator@access.test",
        "first_name": "Petra",
        "last_name": "Wolf",
        "role": UserRole.organization_coordinator,
        "phone": "+49 30 1234563",
    },
    {
        "email": "provider@access.test",
        "first_name": "Heinz",
        "last_name": "Weber",
        "role": UserRole.provider_admin,
        "phone": "+49 30 1234564",
    },
    {
        "email": "dispatcher@access.test",
        "first_name": "Thomas",
        "last_name": "Klein",
        "role": UserRole.dispatcher,
        "phone": "+49 30 1234565",
    },
    {
        "email": "driver@access.test",
        "first_name": "Lars",
        "last_name": "Fahrer",
        "role": UserRole.driver,
        "phone": "+49 30 1234566",
    },
    {
        "email": "admin@access.test",
        "first_name": "Plattform",
        "last_name": "Admin",
        "role": UserRole.platform_admin,
        "phone": None,
    },
]

DEMO_ORGS = [
    {
        "name": "Caritas Berlin e.V.",
        "type": OrganizationType.facility,
        "contact_email": "kontakt@caritas-berlin.test",
        "contact_phone": "+49 30 9900100",
    },
    {
        "name": "WB Fahrdienste GmbH",
        "type": OrganizationType.transport_provider,
        "contact_email": "info@wb-fahrdienste.test",
        "contact_phone": "+49 30 9900200",
    },
]


def main() -> None:
    db = SessionLocal()
    try:
        # Users anlegen
        created_users: dict[str, User] = {}
        for data in DEMO_USERS:
            email = data["email"].lower()
            existing = db.query(User).filter(User.email == email).first()
            if existing:
                print(f"  skip  {email} (bereits vorhanden)")
                created_users[email] = existing
                continue
            user = User(
                email=email,
                password_hash=hash_password(DEMO_PASSWORD),
                first_name=data["first_name"],
                last_name=data["last_name"],
                role=data["role"],
                phone=data.get("phone"),
            )
            db.add(user)
            db.flush()
            created_users[email] = user
            print(f"  +user {email} ({data['role'].value})")

        # Orgs anlegen
        created_orgs: dict[str, Organization] = {}
        for data in DEMO_ORGS:
            existing = db.query(Organization).filter(Organization.name == data["name"]).first()
            if existing:
                print(f"  skip  org '{data['name']}' (bereits vorhanden)")
                created_orgs[data["name"]] = existing
                continue
            org = Organization(
                name=data["name"],
                type=data["type"],
                contact_email=data.get("contact_email"),
                contact_phone=data.get("contact_phone"),
            )
            db.add(org)
            db.flush()
            created_orgs[data["name"]] = org
            print(f"  +org  '{data['name']}' ({data['type'].value})")

        # Memberships anlegen
        caritas = created_orgs.get("Caritas Berlin e.V.")
        wb = created_orgs.get("WB Fahrdienste GmbH")

        memberships = [
            (created_users.get("orgadmin@access.test"),    caritas, "Organisationsleitung"),
            (created_users.get("coordinator@access.test"), caritas, "Koordination"),
            (created_users.get("provider@access.test"),    wb,      "Geschäftsführung"),
            (created_users.get("dispatcher@access.test"),  wb,      "Disposition"),
            (created_users.get("driver@access.test"),      wb,      "Fahrer:in"),
        ]
        for user, org, role_label in memberships:
            if not user or not org:
                continue
            exists = (
                db.query(OrganizationMembership)
                .filter(
                    OrganizationMembership.user_id == user.id,
                    OrganizationMembership.organization_id == org.id,
                )
                .first()
            )
            if not exists:
                db.add(
                    OrganizationMembership(
                        user_id=user.id,
                        organization_id=org.id,
                        organization_role=role_label,
                    )
                )
                print(f"  +memb {user.email} -> {org.name} ({role_label})")

        # TrustedRelationship: relative@ darf für passenger@ buchen und Fahrten sehen
        passenger = created_users.get("passenger@access.test")
        relative = created_users.get("relative@access.test")
        if passenger and relative:
            exists = (
                db.query(TrustedRelationship)
                .filter(
                    TrustedRelationship.passenger_user_id == passenger.id,
                    TrustedRelationship.trusted_user_id == relative.id,
                )
                .first()
            )
            if not exists:
                db.add(
                    TrustedRelationship(
                        passenger_user_id=passenger.id,
                        trusted_user_id=relative.id,
                        can_book_rides=True,
                        can_view_rides=True,
                        can_manage_profile=False,
                        status=TrustStatus.active,
                    )
                )
                print("  +trust relative@access.test -> passenger@access.test (aktiv)")

        db.commit()
        print("\nDemo-Daten erfolgreich angelegt.")
        print(f"Passwort für alle Konten: {DEMO_PASSWORD}")
    except Exception as exc:
        db.rollback()
        print(f"Fehler: {exc}", file=sys.stderr)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
