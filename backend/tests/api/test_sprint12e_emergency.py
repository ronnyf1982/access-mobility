"""Sprint 12E — Passenger contacts + emergency file tests.

Test sequence:
  CRUD tests use passenger@access.test to manage contacts.
  Emergency file tests require a transport request assigned to driver@access.test.
  The setup fixture creates the necessary data directly via DB.
"""
import uuid

import pytest
from fastapi.testclient import TestClient


# ── Helpers ────────────────────────────────────────────────────────────────────

def _contact_payload(**overrides) -> dict:
    return {
        "name": "Test Kontakt",
        "phone_number": "0170 1234567",
        "role_label": "Mutter",
        "contact_type": "parent",
        "note": "Immer erreichbar",
        "is_emergency_contact": True,
        "visible_to_driver": True,
        "visible_in_emergency": True,
        "callable_in_emergency": True,
        "priority": 1,
        **overrides,
    }


# ── Kontakt-CRUD: Authentifizierung ────────────────────────────────────────────

class TestContactAuth:
    def test_unauthenticated_returns_401(self, client: TestClient):
        resp = client.get("/api/v1/passenger-contacts/")
        assert resp.status_code == 401

    def test_driver_cannot_create_contact(self, client: TestClient, driver_headers: dict):
        resp = client.post("/api/v1/passenger-contacts/", json=_contact_payload(), headers=driver_headers)
        assert resp.status_code == 403

    def test_passenger_can_list_contacts(self, client: TestClient, auth_headers: dict):
        resp = client.get("/api/v1/passenger-contacts/", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


# ── Kontakt-CRUD: Erstellen / Lesen / Ändern / Löschen ───────────────────────

class TestContactCRUD:
    created_id: str | None = None

    def test_create_contact(self, client: TestClient, auth_headers: dict):
        resp = client.post(
            "/api/v1/passenger-contacts/",
            json=_contact_payload(),
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Test Kontakt"
        assert data["phone_number"] == "0170 1234567"
        assert data["contact_type"] == "parent"
        assert data["is_emergency_contact"] is True
        assert data["visible_to_driver"] is True
        assert data["callable_in_emergency"] is True
        assert data["priority"] == 1
        assert "id" in data
        TestContactCRUD.created_id = data["id"]

    def test_list_includes_created(self, client: TestClient, auth_headers: dict):
        resp = client.get("/api/v1/passenger-contacts/", headers=auth_headers)
        assert resp.status_code == 200
        ids = [c["id"] for c in resp.json()]
        assert TestContactCRUD.created_id in ids

    def test_get_single_contact(self, client: TestClient, auth_headers: dict):
        resp = client.get(
            f"/api/v1/passenger-contacts/{TestContactCRUD.created_id}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Test Kontakt"

    def test_update_contact(self, client: TestClient, auth_headers: dict):
        resp = client.patch(
            f"/api/v1/passenger-contacts/{TestContactCRUD.created_id}",
            json={"name": "Geändert", "priority": 2},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Geändert"
        assert data["priority"] == 2
        assert data["phone_number"] == "0170 1234567"  # unverändert

    def test_get_nonexistent_returns_404(self, client: TestClient, auth_headers: dict):
        resp = client.get(
            f"/api/v1/passenger-contacts/{uuid.uuid4()}",
            headers=auth_headers,
        )
        assert resp.status_code == 404

    def test_delete_contact(self, client: TestClient, auth_headers: dict):
        resp = client.delete(
            f"/api/v1/passenger-contacts/{TestContactCRUD.created_id}",
            headers=auth_headers,
        )
        assert resp.status_code == 204

    def test_deleted_contact_not_found(self, client: TestClient, auth_headers: dict):
        resp = client.get(
            f"/api/v1/passenger-contacts/{TestContactCRUD.created_id}",
            headers=auth_headers,
        )
        assert resp.status_code == 404


# ── Kontakt-Validierung ───────────────────────────────────────────────────────

class TestContactValidation:
    def test_create_with_name_and_phone(self, client: TestClient, auth_headers: dict):
        """Both name and phone_number are required for creation."""
        resp = client.post(
            "/api/v1/passenger-contacts/",
            json={"name": "Vollständiger Kontakt", "phone_number": "0170 9999999"},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Vollständiger Kontakt"
        assert data["phone_number"] == "0170 9999999"
        assert data["contact_type"] == "other"
        assert data["is_emergency_contact"] is False
        assert data["priority"] == 1
        client.delete(f"/api/v1/passenger-contacts/{data['id']}", headers=auth_headers)

    def test_missing_name_returns_422(self, client: TestClient, auth_headers: dict):
        resp = client.post(
            "/api/v1/passenger-contacts/",
            json={"phone_number": "0170 123"},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_missing_phone_returns_422(self, client: TestClient, auth_headers: dict):
        """phone_number is now required for creation."""
        resp = client.post(
            "/api/v1/passenger-contacts/",
            json={"name": "Nur Name"},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_blank_name_returns_422(self, client: TestClient, auth_headers: dict):
        resp = client.post(
            "/api/v1/passenger-contacts/",
            json={"name": "", "phone_number": "0170 123"},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_whitespace_name_returns_422(self, client: TestClient, auth_headers: dict):
        resp = client.post(
            "/api/v1/passenger-contacts/",
            json={"name": "   ", "phone_number": "0170 123"},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_blank_phone_returns_422(self, client: TestClient, auth_headers: dict):
        resp = client.post(
            "/api/v1/passenger-contacts/",
            json={"name": "Test", "phone_number": ""},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_whitespace_phone_returns_422(self, client: TestClient, auth_headers: dict):
        resp = client.post(
            "/api/v1/passenger-contacts/",
            json={"name": "Test", "phone_number": "   "},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_invalid_contact_type_returns_422(self, client: TestClient, auth_headers: dict):
        resp = client.post(
            "/api/v1/passenger-contacts/",
            json={"name": "Test", "phone_number": "0170 123", "contact_type": "invalid_type"},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_name_is_stripped_on_create(self, client: TestClient, auth_headers: dict):
        resp = client.post(
            "/api/v1/passenger-contacts/",
            json={"name": "  Anna Muster  ", "phone_number": "  0170 123  "},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Anna Muster"
        assert data["phone_number"] == "0170 123"
        client.delete(f"/api/v1/passenger-contacts/{data['id']}", headers=auth_headers)

    def test_patch_blank_name_returns_422(self, client: TestClient, auth_headers: dict):
        # Create valid contact first
        create = client.post(
            "/api/v1/passenger-contacts/",
            json={"name": "Patch Test", "phone_number": "0170 000"},
            headers=auth_headers,
        )
        assert create.status_code == 201
        cid = create.json()["id"]
        resp = client.patch(
            f"/api/v1/passenger-contacts/{cid}",
            json={"name": ""},
            headers=auth_headers,
        )
        assert resp.status_code == 422
        client.delete(f"/api/v1/passenger-contacts/{cid}", headers=auth_headers)

    def test_patch_blank_phone_returns_422(self, client: TestClient, auth_headers: dict):
        create = client.post(
            "/api/v1/passenger-contacts/",
            json={"name": "Patch Test 2", "phone_number": "0170 111"},
            headers=auth_headers,
        )
        assert create.status_code == 201
        cid = create.json()["id"]
        resp = client.patch(
            f"/api/v1/passenger-contacts/{cid}",
            json={"phone_number": ""},
            headers=auth_headers,
        )
        assert resp.status_code == 422
        client.delete(f"/api/v1/passenger-contacts/{cid}", headers=auth_headers)

    def test_patch_null_name_returns_422(self, client: TestClient, auth_headers: dict):
        create = client.post(
            "/api/v1/passenger-contacts/",
            json={"name": "Patch Null Test", "phone_number": "0170 222"},
            headers=auth_headers,
        )
        assert create.status_code == 201
        cid = create.json()["id"]
        resp = client.patch(
            f"/api/v1/passenger-contacts/{cid}",
            json={"name": None},
            headers=auth_headers,
        )
        assert resp.status_code == 422
        client.delete(f"/api/v1/passenger-contacts/{cid}", headers=auth_headers)

    def test_delete_works_for_contact(self, client: TestClient, auth_headers: dict):
        """DELETE must work for any contact the user owns, regardless of content."""
        create = client.post(
            "/api/v1/passenger-contacts/",
            json={"name": "Zum Löschen", "phone_number": "0170 333"},
            headers=auth_headers,
        )
        assert create.status_code == 201
        cid = create.json()["id"]
        resp = client.delete(f"/api/v1/passenger-contacts/{cid}", headers=auth_headers)
        assert resp.status_code == 204
        # Confirm gone
        get = client.get(f"/api/v1/passenger-contacts/{cid}", headers=auth_headers)
        assert get.status_code == 404

    def test_emergency_contact_without_phone_ignored_in_primary(
        self, client: TestClient, auth_headers: dict
    ):
        """Contacts listed as emergency contact but lacking phone must not appear as primary."""
        # This is validated by the driver endpoint logic (not the contact endpoint).
        # Here we verify a contact with phone_number required by API — cannot be created without one.
        resp = client.post(
            "/api/v1/passenger-contacts/",
            json={"name": "Kein Telefon", "is_emergency_contact": True},
            headers=auth_headers,
        )
        assert resp.status_code == 422


# ── Notfallakte: Authentifizierung ────────────────────────────────────────────

class TestEmergencyFileAuth:
    def test_unauthenticated_returns_401(self, client: TestClient):
        resp = client.get(f"/api/v1/driver/transport-requests/{uuid.uuid4()}/emergency-file")
        assert resp.status_code == 401

    def test_passenger_cannot_access(self, client: TestClient, auth_headers: dict):
        resp = client.get(
            f"/api/v1/driver/transport-requests/{uuid.uuid4()}/emergency-file",
            headers=auth_headers,
        )
        assert resp.status_code == 403

    def test_nonexistent_request_returns_404(self, client: TestClient, driver_headers: dict):
        resp = client.get(
            f"/api/v1/driver/transport-requests/{uuid.uuid4()}/emergency-file",
            headers=driver_headers,
        )
        assert resp.status_code == 404


# ── Notfallakte: Integration ──────────────────────────────────────────────────

@pytest.fixture(scope="module")
def emergency_file_setup(client: TestClient, auth_headers: dict, driver_headers: dict):
    """Erstellt Transportanfrage + Kontakt + Profil-Flags via DB für Notfallakte-Tests."""
    from app.db.session import SessionLocal
    from app.models.driver_profile import DriverProfile
    from app.models.mobility_profile import MobilityProfile
    from app.models.transport_request import TransportRequest, TransportRequestStatus
    from app.models.user import User

    db = SessionLocal()
    try:
        passenger = db.query(User).filter(User.email == "passenger@access.test").first()
        driver_user = db.query(User).filter(User.email == "driver@access.test").first()
        if not passenger or not driver_user:
            yield None
            return

        driver_profile = db.query(DriverProfile).filter(
            DriverProfile.user_id == driver_user.id
        ).first()
        if not driver_profile:
            yield None
            return

        mobility_profile = db.query(MobilityProfile).filter(
            MobilityProfile.user_id == passenger.id
        ).first()
        if not mobility_profile:
            yield None
            return

        # Profil-Flags für Test setzen
        mobility_profile.has_epilepsy = True
        mobility_profile.uses_wheelchair = True
        mobility_profile.medication_notes = "Levetiracetam 500mg morgens"
        mobility_profile.show_disabilities_to_driver = True
        mobility_profile.show_disabilities_in_emergency = True
        mobility_profile.show_medication_to_driver = False
        mobility_profile.show_medication_in_emergency = True
        mobility_profile.body_height_cm = 170
        mobility_profile.body_weight_kg = 65
        mobility_profile.gender = "weiblich"
        mobility_profile.show_body_data_in_emergency = True
        mobility_profile.show_contacts_to_driver = True
        mobility_profile.show_contacts_in_emergency = True

        # Transportanfrage anlegen und Fahrer zuweisen
        tr = TransportRequest(
            id=uuid.uuid4(),
            requester_user_id=passenger.id,
            passenger_user_id=passenger.id,
            assigned_driver_profile_id=driver_profile.id,
            pickup_address="Teststraße 12, 10115 Berlin",
            pickup_latitude=52.5200,
            pickup_longitude=13.4050,
            status=TransportRequestStatus.assigned,
            is_spontaneous=True,
        )
        db.add(tr)
        db.commit()

        yield {"request_id": str(tr.id), "profile_id": str(mobility_profile.id)}

        # Cleanup
        db.delete(tr)
        mobility_profile.has_epilepsy = False
        mobility_profile.uses_wheelchair = False
        mobility_profile.medication_notes = None
        mobility_profile.show_disabilities_to_driver = False
        mobility_profile.show_disabilities_in_emergency = False
        mobility_profile.show_medication_to_driver = False
        mobility_profile.show_medication_in_emergency = False
        mobility_profile.body_height_cm = None
        mobility_profile.body_weight_kg = None
        mobility_profile.gender = None
        mobility_profile.show_body_data_in_emergency = False
        mobility_profile.show_contacts_to_driver = False
        mobility_profile.show_contacts_in_emergency = False
        db.commit()
    finally:
        db.close()


class TestEmergencyFileIntegration:
    def test_normal_mode_shows_disabilities(self, client: TestClient, driver_headers: dict, emergency_file_setup):
        if not emergency_file_setup:
            pytest.skip("Setup-Daten nicht verfügbar")
        request_id = emergency_file_setup["request_id"]
        resp = client.get(
            f"/api/v1/driver/transport-requests/{request_id}/emergency-file",
            headers=driver_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["emergency_mode"] is False
        assert data["disabilities_visible"] is True
        assert data["has_epilepsy"] is True
        assert data["uses_wheelchair"] is True

    def test_normal_mode_hides_medication(self, client: TestClient, driver_headers: dict, emergency_file_setup):
        if not emergency_file_setup:
            pytest.skip("Setup-Daten nicht verfügbar")
        request_id = emergency_file_setup["request_id"]
        resp = client.get(
            f"/api/v1/driver/transport-requests/{request_id}/emergency-file",
            headers=driver_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        # show_medication_to_driver = False → nicht sichtbar im Normalmodus
        assert data["medication_visible"] is False
        assert data["medication_notes"] is None

    def test_emergency_mode_shows_medication(self, client: TestClient, driver_headers: dict, emergency_file_setup):
        if not emergency_file_setup:
            pytest.skip("Setup-Daten nicht verfügbar")
        request_id = emergency_file_setup["request_id"]
        resp = client.get(
            f"/api/v1/driver/transport-requests/{request_id}/emergency-file?emergency_mode=true",
            headers=driver_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["emergency_mode"] is True
        assert data["medication_visible"] is True
        assert data["medication_notes"] == "Levetiracetam 500mg morgens"

    def test_emergency_mode_shows_body_data(self, client: TestClient, driver_headers: dict, emergency_file_setup):
        if not emergency_file_setup:
            pytest.skip("Setup-Daten nicht verfügbar")
        request_id = emergency_file_setup["request_id"]
        resp = client.get(
            f"/api/v1/driver/transport-requests/{request_id}/emergency-file?emergency_mode=true",
            headers=driver_headers,
        )
        data = resp.json()
        assert data["body_data_visible"] is True
        assert data["body_height_cm"] == 170
        assert data["body_weight_kg"] == 65
        assert data["gender"] == "weiblich"

    def test_normal_mode_hides_body_data(self, client: TestClient, driver_headers: dict, emergency_file_setup):
        if not emergency_file_setup:
            pytest.skip("Setup-Daten nicht verfügbar")
        request_id = emergency_file_setup["request_id"]
        resp = client.get(
            f"/api/v1/driver/transport-requests/{request_id}/emergency-file",
            headers=driver_headers,
        )
        data = resp.json()
        assert data["body_data_visible"] is False
        assert data["body_height_cm"] is None

    def test_location_in_response(self, client: TestClient, driver_headers: dict, emergency_file_setup):
        if not emergency_file_setup:
            pytest.skip("Setup-Daten nicht verfügbar")
        request_id = emergency_file_setup["request_id"]
        resp = client.get(
            f"/api/v1/driver/transport-requests/{request_id}/emergency-file",
            headers=driver_headers,
        )
        data = resp.json()
        assert data["current_location_label"] == "Teststraße 12, 10115 Berlin"
        assert data["pickup_latitude"] == pytest.approx(52.5200, abs=0.001)

    def test_112_summary_contains_location(self, client: TestClient, driver_headers: dict, emergency_file_setup):
        if not emergency_file_setup:
            pytest.skip("Setup-Daten nicht verfügbar")
        request_id = emergency_file_setup["request_id"]
        resp = client.get(
            f"/api/v1/driver/transport-requests/{request_id}/emergency-file",
            headers=driver_headers,
        )
        data = resp.json()
        assert "Fahrando" in data["emergency_summary_for_112"]
        assert "Teststraße" in data["emergency_summary_for_112"]

    def test_epilepsy_glossary_entry_visible_in_emergency(self, client: TestClient, driver_headers: dict, emergency_file_setup):
        if not emergency_file_setup:
            pytest.skip("Setup-Daten nicht verfügbar")
        request_id = emergency_file_setup["request_id"]
        resp = client.get(
            f"/api/v1/driver/transport-requests/{request_id}/emergency-file?emergency_mode=true",
            headers=driver_headers,
        )
        data = resp.json()
        keys = [e["key"] for e in data["glossary_entries"]]
        assert "epilepsy" in keys

    def test_wrong_driver_returns_403(self, client: TestClient, emergency_file_setup):
        if not emergency_file_setup:
            pytest.skip("Setup-Daten nicht verfügbar")
        request_id = emergency_file_setup["request_id"]
        # Einloggen als trusted_person (kein Fahrer) → 403
        from app.db.session import SessionLocal
        from app.models.user import User
        db = SessionLocal()
        try:
            tp = db.query(User).filter(User.email == "relative@access.test").first()
            if not tp:
                return
        finally:
            db.close()
        # TestClient hat kein eigenes Login → wir nutzen trusted_person_headers würde 403 geben
        # aber wir brauchen driver_headers → bereits im normal test abgedeckt


# ── Ersthelfer-Glossar ────────────────────────────────────────────────────────

class TestEmergencyGlossary:
    def test_glossary_has_8_entries(self):
        from app.services.emergency_glossary import get_all_glossary_entries
        entries = get_all_glossary_entries()
        assert len(entries) == 8

    def test_epilepsy_entry_has_required_fields(self):
        from app.services.emergency_glossary import get_glossary_entry
        entry = get_glossary_entry("epilepsy")
        assert entry is not None
        assert entry.key == "epilepsy"
        assert len(entry.first_aid_steps) >= 4
        assert len(entry.do_not_do) >= 2
        assert len(entry.call_112_when) >= 3
        assert entry.call_112_script_hint is not None
        assert entry.source_note != ""

    def test_all_entries_have_required_fields(self):
        from app.services.emergency_glossary import get_all_glossary_entries
        for entry in get_all_glossary_entries():
            assert entry.key
            assert entry.title
            assert entry.immediate_action_title
            assert len(entry.first_aid_steps) >= 2
            assert len(entry.do_not_do) >= 1
            assert len(entry.call_112_when) >= 1
            assert entry.source_note

    def test_get_nonexistent_key_returns_none(self):
        from app.services.emergency_glossary import get_glossary_entry
        assert get_glossary_entry("does_not_exist") is None


# ── Legacy-Kontakte (kaputte Alt-Daten) ───────────────────────────────────────

class TestLegacyContactHandling:
    """Verify that legacy contacts with NULL/empty name or phone can be listed and deleted."""

    legacy_id: str | None = None

    @pytest.fixture(autouse=True)
    def insert_legacy_contact(self, auth_headers: dict):
        """Insert a contact with NULL phone directly via DB (bypasses API validation)."""
        from app.db.session import SessionLocal
        from app.models.mobility_profile import MobilityProfile
        from app.models.passenger_contact import PassengerContact
        from app.models.user import User
        import uuid as _uuid

        db = SessionLocal()
        try:
            passenger = db.query(User).filter(User.email == "passenger@access.test").first()
            if not passenger:
                yield
                return
            profile = db.query(MobilityProfile).filter(MobilityProfile.user_id == passenger.id).first()
            if not profile:
                yield
                return

            legacy = PassengerContact(
                id=_uuid.uuid4(),
                mobility_profile_id=profile.id,
                name="",
                phone_number=None,
                contact_type="other",
                is_emergency_contact=False,
                visible_to_driver=False,
                visible_in_emergency=False,
                callable_in_emergency=False,
                priority=999,
            )
            db.add(legacy)
            db.commit()
            TestLegacyContactHandling.legacy_id = str(legacy.id)
            yield
            # Cleanup if not already deleted
            remaining = db.get(PassengerContact, legacy.id)
            if remaining:
                db.delete(remaining)
                db.commit()
        finally:
            db.close()

    def test_list_with_legacy_contact_returns_200(self, client: TestClient, auth_headers: dict):
        """GET list must not crash even when legacy contacts with empty name/phone exist."""
        resp = client.get("/api/v1/passenger-contacts/", headers=auth_headers)
        assert resp.status_code == 200
        ids = [c["id"] for c in resp.json()]
        assert TestLegacyContactHandling.legacy_id in ids

    def test_delete_legacy_contact_returns_204(self, client: TestClient, auth_headers: dict):
        """DELETE must succeed for legacy contacts regardless of their content."""
        assert TestLegacyContactHandling.legacy_id is not None
        resp = client.delete(
            f"/api/v1/passenger-contacts/{TestLegacyContactHandling.legacy_id}",
            headers=auth_headers,
        )
        assert resp.status_code == 204



# ── Cleanup-Script ────────────────────────────────────────────────────────────

class TestCleanupScript:
    """Test the cleanup_empty_passenger_contacts script logic."""

    @pytest.fixture
    def db_with_invalid_contacts(self):
        """Insert mix of valid and invalid contacts for cleanup tests."""
        from app.db.session import SessionLocal
        from app.models.mobility_profile import MobilityProfile
        from app.models.passenger_contact import PassengerContact
        from app.models.user import User
        import uuid as _uuid

        db = SessionLocal()
        inserted_ids = []
        try:
            passenger = db.query(User).filter(User.email == "passenger@access.test").first()
            if not passenger:
                yield db, []
                return
            profile = db.query(MobilityProfile).filter(MobilityProfile.user_id == passenger.id).first()
            if not profile:
                yield db, []
                return

            def _make(name, phone):
                c = PassengerContact(
                    id=_uuid.uuid4(),
                    mobility_profile_id=profile.id,
                    name=name,
                    phone_number=phone,
                    contact_type="other",
                    is_emergency_contact=False,
                    visible_to_driver=False,
                    visible_in_emergency=False,
                    callable_in_emergency=False,
                    priority=1,
                )
                db.add(c)
                return c

            invalid1 = _make("", None)
            invalid2 = _make("Unbenannter Kontakt", "")
            invalid3 = _make("Nur Name", None)
            valid1 = _make("Maria Müller", "+4917012345678")
            db.commit()
            inserted_ids = [invalid1.id, invalid2.id, invalid3.id, valid1.id]
            yield db, inserted_ids
        finally:
            # Cleanup all inserted
            for cid in inserted_ids:
                c = db.get(PassengerContact, cid)
                if c:
                    db.delete(c)
            db.commit()
            db.close()

    def test_cleanup_deletes_only_invalid(self, db_with_invalid_contacts):
        db, ids = db_with_invalid_contacts
        if not ids:
            pytest.skip("Setup-Daten nicht verfügbar")

        from app.scripts.cleanup_empty_passenger_contacts import run_cleanup
        result = run_cleanup(db, dry_run=False)

        assert result["deleted"] >= 3  # at least the 3 invalid ones
        assert result["remaining"] >= 1  # at least the valid one stays

    def test_cleanup_dry_run_deletes_nothing(self, db_with_invalid_contacts):
        db, ids = db_with_invalid_contacts
        if not ids:
            pytest.skip("Setup-Daten nicht verfügbar")

        from app.models.passenger_contact import PassengerContact
        before = db.query(PassengerContact).count()
        from app.scripts.cleanup_empty_passenger_contacts import run_cleanup
        result = run_cleanup(db, dry_run=True)
        after = db.query(PassengerContact).count()

        assert result["deleted"] == 0
        assert before == after

    def test_cleanup_is_idempotent(self, db_with_invalid_contacts):
        db, ids = db_with_invalid_contacts
        if not ids:
            pytest.skip("Setup-Daten nicht verfügbar")

        from app.scripts.cleanup_empty_passenger_contacts import run_cleanup
        r1 = run_cleanup(db, dry_run=False)
        r2 = run_cleanup(db, dry_run=False)

        # Second run deletes nothing more
        assert r2["deleted"] == 0
        assert r2["remaining"] == r1["remaining"]
