"""Seed-Skript für Demo-Daten (Entwicklung).

Ausführen:
    cd backend
    python -m app.scripts.seed_demo_data

Idempotent: Bereits vorhandene Einträge werden übersprungen.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import datetime

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.driver_profile import DriverProfile
from app.models.driver_shift import DriverShift, ShiftStatus
from app.models.membership import OrganizationMembership
from app.models.mobility_profile import MobilityProfile, WheelchairType
from app.models.notification_preference import NotificationEventType, PassengerNotificationPreference
from app.models.organization import Organization, OrganizationType
from app.models.ride_status_event import RideStatusEvent, RideStatusEventType
from app.models.transport_request import TransportRequest, TransportRequestStatus
from app.models.trusted_relationship import TrustedRelationship, TrustStatus
from app.models.user import User, UserRole
from app.models.vehicle import Vehicle, VehicleType

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
        "email": "driver2@access.test",
        "first_name": "Maria",
        "last_name": "Fahr",
        "role": UserRole.driver,
        "phone": "+49 30 1234577",
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
            (created_users.get("driver2@access.test"),     wb,      "Fahrer:in"),
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

        # MobilityProfile für passenger@access.test
        passenger_user = created_users.get("passenger@access.test")
        if passenger_user:
            existing_profile = (
                db.query(MobilityProfile)
                .filter(MobilityProfile.user_id == passenger_user.id)
                .first()
            )
            if not existing_profile:
                db.add(
                    MobilityProfile(
                        user_id=passenger_user.id,
                        uses_wheelchair=True,
                        wheelchair_type=WheelchairType.manual,
                        needs_ramp=True,
                        requires_wheelchair_space=True,
                        needs_entry_assistance=True,
                        needs_escort=False,
                        emergency_contact_name="Anna Muster",
                        emergency_contact_phone="+49 30 123456",
                        communication_notes="Bitte langsam und klar kommunizieren.",
                        general_notes="Demo-Profil fuer lokale Entwicklung.",
                    )
                )
                print("  +prof passenger@access.test (Rollstuhl manuell, Rampe, Einstiegshilfe)")
            else:
                print("  skip  MobilityProfile passenger@access.test (bereits vorhanden)")

        # ── Fahrzeuge (für WB Fahrdienste GmbH) ────────────────────────────────
        if wb:
            demo_vehicles = [
                {
                    "name": "Rollstuhlbus 1",
                    "license_plate": "AM-BUS-1",
                    "vehicle_type": VehicleType.wheelchair_bus,
                    "seat_count": 4,
                    "wheelchair_space_count": 2,
                    "escort_seat_count": 2,
                    "has_ramp": True,
                    "has_lift": True,
                    "has_wheelchair_restraint": True,
                    "supports_electric_wheelchair": True,
                    "has_low_entry": True,
                    "has_extra_wide_door": True,
                    "has_first_aid_kit": True,
                    # Maße & Gewicht — Mercedes Sprinter 519 CDI Hochdach
                    "vehicle_length_cm": 699,
                    "vehicle_width_cm": 198,
                    "vehicle_width_with_mirrors_cm": 224,
                    "vehicle_height_cm": 270,
                    "wheelbase_cm": 391,
                    "turning_circle_m": 13.4,
                    "empty_weight_kg": 2480,
                    "gross_vehicle_weight_kg": 5000,
                    "payload_capacity_kg": 2520,
                    "requires_large_parking_space": True,
                    "suitable_for_narrow_streets": False,
                    "suitable_for_underground_parking": False,
                    "has_parking_assist": True,
                },
                {
                    "name": "Rollstuhl-Van 1",
                    "license_plate": "AM-VAN-1",
                    "vehicle_type": VehicleType.wheelchair_van,
                    "seat_count": 3,
                    "wheelchair_space_count": 1,
                    "escort_seat_count": 1,
                    "has_ramp": True,
                    "has_lift": False,
                    "has_wheelchair_restraint": True,
                    "supports_electric_wheelchair": False,
                    "has_low_entry": False,
                    "has_first_aid_kit": True,
                    "has_hygiene_equipment": True,
                    # Maße & Gewicht — VW Caddy Maxi
                    "vehicle_length_cm": 484,
                    "vehicle_width_cm": 183,
                    "vehicle_width_with_mirrors_cm": 202,
                    "vehicle_height_cm": 185,
                    "wheelbase_cm": 302,
                    "turning_circle_m": 11.2,
                    "empty_weight_kg": 1620,
                    "gross_vehicle_weight_kg": 2130,
                    "payload_capacity_kg": 510,
                    "requires_large_parking_space": False,
                    "suitable_for_narrow_streets": True,
                    "suitable_for_underground_parking": True,
                    "has_parking_assist": True,
                },
                {
                    "name": "Standard-PKW 1",
                    "license_plate": "AM-CAR-1",
                    "vehicle_type": VehicleType.standard_car,
                    "seat_count": 4,
                    "wheelchair_space_count": 0,
                    "escort_seat_count": 0,
                    "has_ramp": False,
                    "has_lift": False,
                    "has_wheelchair_restraint": False,
                    "supports_electric_wheelchair": False,
                    # Maße & Gewicht — VW Passat Variant
                    "vehicle_length_cm": 476,
                    "vehicle_width_cm": 183,
                    "vehicle_width_with_mirrors_cm": 200,
                    "vehicle_height_cm": 148,
                    "wheelbase_cm": 272,
                    "turning_circle_m": 10.9,
                    "empty_weight_kg": 1485,
                    "gross_vehicle_weight_kg": 2100,
                    "payload_capacity_kg": 615,
                    "requires_large_parking_space": False,
                    "suitable_for_narrow_streets": True,
                    "suitable_for_underground_parking": True,
                    "has_parking_assist": False,
                },
            ]
            _DIM_FIELDS = [
                "vehicle_length_cm", "vehicle_width_cm", "vehicle_width_with_mirrors_cm",
                "vehicle_height_cm", "wheelbase_cm", "turning_circle_m",
                "empty_weight_kg", "gross_vehicle_weight_kg", "payload_capacity_kg",
                "requires_large_parking_space", "suitable_for_narrow_streets",
                "suitable_for_underground_parking", "has_parking_assist",
            ]
            for v_data in demo_vehicles:
                exists = (
                    db.query(Vehicle)
                    .filter(Vehicle.license_plate == v_data["license_plate"])
                    .first()
                )
                if not exists:
                    db.add(Vehicle(organization_id=wb.id, **v_data))
                    print(f"  +veh  {v_data['license_plate']} ({v_data['name']})")
                elif exists.vehicle_length_cm is None:
                    # Dimensions added by migration — backfill for pre-existing records
                    for field in _DIM_FIELDS:
                        if field in v_data:
                            setattr(exists, field, v_data[field])
                    print(f"  upd   Fahrzeug {v_data['license_plate']} — Maße/Gewicht/Zufahrt ergänzt")
                else:
                    print(f"  skip  Fahrzeug {v_data['license_plate']} (bereits vorhanden)")

        # ── Fahrerprofil (für driver@access.test) ───────────────────────────
        driver_user = created_users.get("driver@access.test")
        if driver_user and wb:
            existing_dp = (
                db.query(DriverProfile)
                .filter(DriverProfile.user_id == driver_user.id)
                .first()
            )
            if not existing_dp:
                db.add(
                    DriverProfile(
                        user_id=driver_user.id,
                        organization_id=wb.id,
                        display_name="Demo Fahrer",
                        phone="+49 30 1234566",
                        can_assist_wheelchair=True,
                        can_secure_wheelchair=True,
                        can_operate_lift=True,
                        has_first_aid_training=True,
                        has_passenger_transport_license=True,
                    )
                )
                print("  +drv  driver@access.test -> WB Fahrdienste GmbH")
            else:
                print("  skip  DriverProfile driver@access.test (bereits vorhanden)")

        # ── Fahrerprofil-Erweiterung Sprint 7: Rollstuhlsicherungs-Training ───
        if driver_user and wb:
            existing_dp = (
                db.query(DriverProfile)
                .filter(DriverProfile.user_id == driver_user.id)
                .first()
            )
            if existing_dp and not existing_dp.has_wheelchair_restraint_training:
                existing_dp.has_wheelchair_restraint_training = True
                print("  upd   DriverProfile driver@access.test — has_wheelchair_restraint_training gesetzt")

        # ── Fahrerprofil-Erweiterung Sprint 10B: Standardfahrzeug ──────────
        if driver_user and wb:
            existing_dp = (
                db.query(DriverProfile)
                .filter(DriverProfile.user_id == driver_user.id)
                .first()
            )
            if existing_dp and existing_dp.default_vehicle_id is None:
                default_vehicle = (
                    db.query(Vehicle)
                    .filter(Vehicle.license_plate == "AM-BUS-1", Vehicle.is_active == True)  # noqa: E712
                    .first()
                )
                if default_vehicle:
                    existing_dp.default_vehicle_id = default_vehicle.id
                    print(f"  upd   DriverProfile driver@access.test — default_vehicle_id = {default_vehicle.license_plate}")
            elif existing_dp and existing_dp.default_vehicle_id is not None:
                print("  ok    DriverProfile driver@access.test — default_vehicle_id bereits gesetzt")

        # ── Transportanfragen (für passenger@access.test) ───────────────────
        if passenger_user:
            existing_requests = (
                db.query(TransportRequest)
                .filter(TransportRequest.passenger_user_id == passenger_user.id)
                .count()
            )
            if existing_requests == 0:
                # 1. Entwurf
                db.add(TransportRequest(
                    requester_user_id=passenger_user.id,
                    passenger_user_id=passenger_user.id,
                    transport_type_id="accessible_ride",
                    status=TransportRequestStatus.draft,
                    pickup_address="Musterstraße 12, 10115 Berlin",
                    pickup_details="EG links, Klingel Muster",
                    destination_address="Charité – Universitätsmedizin Berlin, Charitéplatz 1, 10117 Berlin",
                    destination_details="Eingang Haus N, Anmeldung Erdgeschoss",
                    pickup_date=datetime.date(2026, 7, 20),
                    pickup_time=datetime.time(9, 0),
                    arrival_time=datetime.time(9, 45),
                    is_round_trip=True,
                    return_time_known=False,
                    requirement_snapshot={
                        "transport_type_id": "accessible_ride",
                        "selected_profile_fields": ["uses_wheelchair", "needs_ramp", "needs_entry_assistance"],
                        "selected_field_values": {},
                        "notes": "Rollstuhl manuell, Rampe erforderlich",
                    },
                    mobility_profile_snapshot={
                        "uses_wheelchair": True,
                        "wheelchair_type": "manual",
                        "needs_ramp": True,
                        "needs_entry_assistance": True,
                        "requires_wheelchair_space": True,
                    },
                    notes="Termin beim Neurologen — bitte pünktlich",
                ))
                print("  +req  Entwurf accessible_ride für passenger@access.test")

                # 2. Abgesendete Anfrage
                req2 = TransportRequest(
                    requester_user_id=passenger_user.id,
                    passenger_user_id=passenger_user.id,
                    transport_type_id="patient_ride_no_medical_care",
                    status=TransportRequestStatus.requested,
                    pickup_address="Berliner Str. 88, 10713 Berlin",
                    pickup_details="2. OG, Aufzug vorhanden",
                    destination_address="Reha-Zentrum am Park, Spandauer Damm 130, 14050 Berlin",
                    destination_details="Haupteingang, Anmeldung am Empfang",
                    pickup_date=datetime.date(2026, 7, 22),
                    pickup_time=datetime.time(8, 30),
                    is_round_trip=True,
                    return_time_known=True,
                    return_pickup_time=datetime.time(13, 0),
                    requirement_snapshot={
                        "transport_type_id": "patient_ride_no_medical_care",
                        "selected_profile_fields": ["requires_wheelchair_space", "needs_entry_assistance", "requires_extra_time"],
                        "selected_field_values": {},
                        "notes": None,
                    },
                    mobility_profile_snapshot={
                        "uses_wheelchair": True,
                        "wheelchair_type": "manual",
                        "needs_entry_assistance": True,
                        "requires_wheelchair_space": True,
                        "requires_extra_time": True,
                    },
                    submitted_at=datetime.datetime(2026, 7, 10, 14, 22, 0, tzinfo=datetime.timezone.utc),
                )
                db.add(req2)
                print("  +req  requested patient_ride_no_medical_care für passenger@access.test")
            else:
                print(f"  skip  Basis-TransportRequests passenger@access.test ({existing_requests} vorhanden)")

            # Sprint 7: Anfragen 3+4 nur anlegen wenn noch nicht da (by pickup_address)
            sprint7_seeds = [
                {
                    "pickup_address": "Müllerstraße 45, 13353 Berlin",
                    "destination_address": "Tagespflege Sonnenschein, Seestraße 68, 13347 Berlin",
                    "transport_type_id": "accessible_ride",
                    "status": TransportRequestStatus.requested,
                    "pickup_date": datetime.date(2026, 7, 28),
                    "pickup_time": datetime.time(9, 15),
                    "is_round_trip": True,
                    "return_time_known": True,
                    "return_pickup_time": datetime.time(15, 30),
                    "requirement_snapshot": {
                        "transport_type_id": "accessible_ride",
                        "selected_profile_fields": [
                            "uses_wheelchair", "needs_ramp", "needs_escort", "requires_wheelchair_space"
                        ],
                        "selected_field_values": {},
                        "notes": "Rollstuhl manuell, Rampe und Begleitplatz erforderlich.",
                    },
                    "mobility_profile_snapshot": {
                        "uses_wheelchair": True,
                        "wheelchair_type": "manual",
                        "needs_ramp": True,
                        "needs_escort": True,
                        "requires_wheelchair_space": True,
                    },
                    "notes": "Sprint-7-Demo: Gute Übereinstimmung mit Rollstuhlbus 1 und Demo Fahrer.",
                    "submitted_at": datetime.datetime(2026, 7, 10, 16, 0, 0, tzinfo=datetime.timezone.utc),
                    "label": "accessible_ride mit Rollstuhl + Rampe + Begleitung (Sprint 7 — gute Übereinstimmung)",
                },
                {
                    "pickup_address": "Sonnenallee 200, 12059 Berlin",
                    "destination_address": "Vivantes Klinikum Neukölln, Rudower Str. 48, 12351 Berlin",
                    "transport_type_id": "stretcher_ride",
                    "status": TransportRequestStatus.requested,
                    "pickup_date": datetime.date(2026, 7, 30),
                    "pickup_time": datetime.time(7, 45),
                    "is_round_trip": False,
                    "return_time_known": False,
                    "requirement_snapshot": {
                        "transport_type_id": "stretcher_ride",
                        "selected_profile_fields": [
                            "needs_stretcher_transport", "requires_special_positioning"
                        ],
                        "selected_field_values": {},
                        "notes": "Liegendtransport, besondere Lagerung notwendig.",
                    },
                    "mobility_profile_snapshot": {
                        "needs_stretcher_transport": True,
                        "requires_special_positioning": True,
                    },
                    "notes": "Sprint-7-Demo: Warnungsfall — kein Fahrzeug mit Liegendtransport-Ausstattung.",
                    "submitted_at": datetime.datetime(2026, 7, 10, 16, 5, 0, tzinfo=datetime.timezone.utc),
                    "label": "stretcher_ride (Sprint 7 — Warnungsfall)",
                },
            ]
            for seed in sprint7_seeds:
                label = seed.pop("label")
                exists = (
                    db.query(TransportRequest)
                    .filter(
                        TransportRequest.passenger_user_id == passenger_user.id,
                        TransportRequest.pickup_address == seed["pickup_address"],
                    )
                    .first()
                )
                if not exists:
                    db.add(TransportRequest(
                        requester_user_id=passenger_user.id,
                        passenger_user_id=passenger_user.id,
                        **seed,
                    ))
                    print(f"  +req  {label}")
                else:
                    print(f"  skip  TransportRequest '{seed['pickup_address']}' (bereits vorhanden)")

        # ── Onboarding-Backfill für Staff-Rollen ────────────────────────────────
        # Fahrer, Disponenten, Admins etc. müssen kein Onboarding durchlaufen.
        # Alle Nicht-Fahrgast-Rollen bekommen onboarding_completed_at gesetzt,
        # falls es noch NULL ist (z. B. nach Migration von Sprint 8).
        _staff_roles = {
            UserRole.driver,
            UserRole.provider_admin,
            UserRole.dispatcher,
            UserRole.organization_admin,
            UserRole.platform_admin,
            UserRole.trusted_person,
        }
        _backfill_ts = datetime.datetime.now(datetime.timezone.utc)
        _backfilled = 0
        for email, user in created_users.items():
            if user.role in _staff_roles and user.onboarding_completed_at is None:
                user.onboarding_completed_at = _backfill_ts
                _backfilled += 1
                print(f"  upd   {email} — onboarding_completed_at gesetzt (Staff-Rolle)")
        if _backfilled == 0:
            print("  ok    Onboarding-Backfill: alle Staff-Nutzer bereits gesetzt")

        # ── Sprint 11: Zugewiesene Fahrt für Fahrer-Statuswechsel Demo ──────────
        driver_user = created_users.get("driver@access.test")
        if passenger_user and driver_user:
            existing_dp = (
                db.query(DriverProfile)
                .filter(DriverProfile.user_id == driver_user.id)
                .first()
            )
            default_vehicle = (
                db.query(Vehicle)
                .filter(Vehicle.license_plate == "AM-BUS-1")
                .first()
            )
            assigned_req_address = "Hauptstraße 5, 10827 Berlin"
            existing_assigned = (
                db.query(TransportRequest)
                .filter(
                    TransportRequest.passenger_user_id == passenger_user.id,
                    TransportRequest.pickup_address == assigned_req_address,
                )
                .first()
            )
            if not existing_assigned and existing_dp and default_vehicle:
                assigned_req = TransportRequest(
                    requester_user_id=passenger_user.id,
                    passenger_user_id=passenger_user.id,
                    transport_type_id="accessible_ride",
                    status=TransportRequestStatus.assigned,
                    pickup_address=assigned_req_address,
                    pickup_details="EG, Klingel Muster",
                    destination_address="Vivantes Klinikum Spandau, Neue Bergstraße 6, 13585 Berlin",
                    destination_details="Eingang Haus A",
                    pickup_date=datetime.date(2026, 7, 21),
                    pickup_time=datetime.time(10, 0),
                    is_round_trip=False,
                    return_time_known=False,
                    mobility_profile_snapshot={
                        "uses_wheelchair": True,
                        "wheelchair_type": "manual",
                        "needs_ramp": True,
                        "requires_wheelchair_space": True,
                    },
                    notes="Sprint-11-Demo: zugewiesene Fahrt für Fahrer-Statuswechsel",
                    assigned_vehicle_id=default_vehicle.id,
                    assigned_driver_profile_id=existing_dp.id,
                    assigned_by_user_id=created_users.get("dispatcher@access.test", passenger_user).id,
                    assigned_at=datetime.datetime(2026, 7, 20, 8, 0, 0, tzinfo=datetime.timezone.utc),
                    submitted_at=datetime.datetime(2026, 7, 19, 18, 0, 0, tzinfo=datetime.timezone.utc),
                )
                db.add(assigned_req)
                db.flush()
                # Initiales Statusereignis
                db.add(RideStatusEvent(
                    transport_request_id=assigned_req.id,
                    status=RideStatusEventType.driver_on_way,
                    note="Automatisch gesetzt durch Seed (Demo)",
                    created_by_user_id=driver_user.id,
                ))
                print("  +req  Zugewiesene Fahrt für driver@access.test (Sprint 11 Demo)")
            else:
                print("  skip  Zugewiesene Sprint-11-Demo-Fahrt (bereits vorhanden oder Profil fehlt)")

        # ── Sprint 11: Benachrichtigungseinstellungen für passenger@access.test ─
        if passenger_user:
            passenger_mp = (
                db.query(MobilityProfile)
                .filter(MobilityProfile.user_id == passenger_user.id)
                .first()
            )
            if passenger_mp:
                _default_notif_prefs = [
                    (NotificationEventType.driver_on_way,       True,  True,  False, False),
                    (NotificationEventType.driver_arrived,       True,  True,  False, False),
                    (NotificationEventType.passenger_picked_up,  True,  True,  False, False),
                    (NotificationEventType.ride_started,         False, True,  False, False),
                    (NotificationEventType.ride_completed,       True,  True,  True,  False),
                    (NotificationEventType.ride_cancelled,       True,  True,  True,  False),
                    (NotificationEventType.issue_reported,       True,  True,  True,  True),
                ]
                added = 0
                for event_type, notify_tp, ch_app, ch_email, ch_sms in _default_notif_prefs:
                    exists = (
                        db.query(PassengerNotificationPreference)
                        .filter(
                            PassengerNotificationPreference.mobility_profile_id == passenger_mp.id,
                            PassengerNotificationPreference.event_type == event_type,
                        )
                        .first()
                    )
                    if not exists:
                        db.add(PassengerNotificationPreference(
                            mobility_profile_id=passenger_mp.id,
                            event_type=event_type,
                            notify_trusted_persons=notify_tp,
                            channel_in_app=ch_app,
                            channel_email=ch_email,
                            channel_sms=ch_sms,
                        ))
                        added += 1
                if added:
                    print(f"  +notif {added} Benachrichtigungseinstellungen für passenger@access.test")
                else:
                    print("  skip  Benachrichtigungseinstellungen passenger@access.test (bereits vorhanden)")

        # ── Sprint 12B: Fahrerprofil für driver2@access.test ───────────────────
        driver2_user = created_users.get("driver2@access.test")
        if driver2_user and wb:
            existing_dp2 = (
                db.query(DriverProfile)
                .filter(DriverProfile.user_id == driver2_user.id)
                .first()
            )
            if not existing_dp2:
                db.add(
                    DriverProfile(
                        user_id=driver2_user.id,
                        organization_id=wb.id,
                        display_name="Demo Fahrerin 2",
                        phone="+49 30 1234577",
                        can_assist_wheelchair=False,
                        can_secure_wheelchair=False,
                        can_operate_lift=False,
                        has_first_aid_training=True,
                        has_passenger_transport_license=True,
                    )
                )
                db.flush()
                print("  +drv  driver2@access.test -> WB Fahrdienste GmbH")
            else:
                print("  skip  DriverProfile driver2@access.test (bereits vorhanden)")

        # ── Sprint 12B: Schichten mit GPS-Demo-Positionen ───────────────────────
        # driver@access.test + AM-VAN-1 → aktiv, passende Ausstattung, nahe Berlin-Mitte
        # driver2@access.test + AM-CAR-1 → pausiert (kein Rollstuhl) → gefiltert
        driver_user_12b = created_users.get("driver@access.test")
        driver2_user_12b = created_users.get("driver2@access.test")

        van_vehicle = (
            db.query(Vehicle).filter(Vehicle.license_plate == "AM-VAN-1").first()
        )
        car_vehicle = (
            db.query(Vehicle).filter(Vehicle.license_plate == "AM-CAR-1").first()
        )

        if driver_user_12b and van_vehicle:
            dp1 = db.query(DriverProfile).filter(DriverProfile.user_id == driver_user_12b.id).first()
            if dp1:
                existing_shift = (
                    db.query(DriverShift)
                    .filter(
                        DriverShift.driver_profile_id == dp1.id,
                        DriverShift.vehicle_id == van_vehicle.id,
                        DriverShift.status == ShiftStatus.active,
                    )
                    .first()
                )
                if not existing_shift:
                    db.add(DriverShift(
                        driver_profile_id=dp1.id,
                        vehicle_id=van_vehicle.id,
                        status=ShiftStatus.active,
                        started_at=datetime.datetime(2026, 7, 20, 7, 0, 0, tzinfo=datetime.timezone.utc),
                        current_latitude=52.525,
                        current_longitude=13.402,
                        notes="Sprint-12B-Demo: aktive Schicht mit GPS-Position (Rollstuhl-Van, passt)",
                    ))
                    print("  +shft driver@access.test + AM-VAN-1 (aktiv, lat=52.525, lon=13.402)")
                else:
                    # Backfill GPS falls noch nicht gesetzt
                    if existing_shift.current_latitude is None:
                        existing_shift.current_latitude = 52.525
                        existing_shift.current_longitude = 13.402
                        print("  upd   DriverShift driver@access.test/AM-VAN-1 — GPS ergänzt")
                    else:
                        print("  skip  DriverShift driver@access.test/AM-VAN-1 (bereits vorhanden)")

        if driver2_user_12b and car_vehicle:
            dp2 = db.query(DriverProfile).filter(DriverProfile.user_id == driver2_user_12b.id).first()
            if dp2:
                existing_shift2 = (
                    db.query(DriverShift)
                    .filter(
                        DriverShift.driver_profile_id == dp2.id,
                        DriverShift.vehicle_id == car_vehicle.id,
                    )
                    .first()
                )
                if not existing_shift2:
                    db.add(DriverShift(
                        driver_profile_id=dp2.id,
                        vehicle_id=car_vehicle.id,
                        status=ShiftStatus.paused,
                        started_at=datetime.datetime(2026, 7, 20, 7, 30, 0, tzinfo=datetime.timezone.utc),
                        break_started_at=datetime.datetime(2026, 7, 20, 12, 0, 0, tzinfo=datetime.timezone.utc),
                        current_latitude=52.510,
                        current_longitude=13.395,
                        notes="Sprint-12B-Demo: Pause (Standard-PKW, kein Rollstuhl) → gefiltert",
                    ))
                    print("  +shft driver2@access.test + AM-CAR-1 (pausiert, lat=52.510)")
                else:
                    print("  skip  DriverShift driver2@access.test/AM-CAR-1 (bereits vorhanden)")

        # Onboarding-Backfill auch für driver2
        if driver2_user and driver2_user.onboarding_completed_at is None:
            driver2_user.onboarding_completed_at = datetime.datetime.now(datetime.timezone.utc)
            print("  upd   driver2@access.test — onboarding_completed_at gesetzt")

        db.commit()
        print("\nDemo-Daten erfolgreich angelegt.")
        print(f"Passwort fuer alle Konten: {DEMO_PASSWORD}")
    except Exception as exc:
        db.rollback()
        print(f"Fehler: {exc}", file=sys.stderr)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
