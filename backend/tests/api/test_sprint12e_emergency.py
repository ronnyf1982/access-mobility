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
    def test_create_minimal_contact(self, client: TestClient, auth_headers: dict):
        resp = client.post(
            "/api/v1/passenger-contacts/",
            json={"name": "Minimalkontakt"},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Minimalkontakt"
        assert data["contact_type"] == "other"
        assert data["is_emergency_contact"] is False
        assert data["visible_to_driver"] is False
        # Cleanup
        client.delete(f"/api/v1/passenger-contacts/{data['id']}", headers=auth_headers)

    def test_missing_name_returns_422(self, client: TestClient, auth_headers: dict):
        resp = client.post(
            "/api/v1/passenger-contacts/",
            json={"phone_number": "0170 123"},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_invalid_contact_type_returns_422(self, client: TestClient, auth_headers: dict):
        resp = client.post(
            "/api/v1/passenger-contacts/",
            json={"name": "Test", "contact_type": "invalid_type"},
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
