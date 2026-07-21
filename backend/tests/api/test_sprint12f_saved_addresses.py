"""Sprint 12F — PassengerSavedAddress CRUD tests."""
import uuid

import pytest
from fastapi.testclient import TestClient


def _addr_payload(**overrides) -> dict:
    return {
        "label": "Zuhause",
        "address_type": "home",
        "street_address": "Musterstraße 12",
        "postal_code": "10115",
        "city": "Berlin",
        "additional_info": "Hintereingang",
        "note": "Klingel zweimal drücken",
        "is_default_pickup": True,
        "is_default_destination": False,
        "is_active": True,
        **overrides,
    }


# ── Auth ──────────────────────────────────────────────────────────────────────

class TestAddressAuth:
    def test_unauthenticated_returns_401(self, client: TestClient):
        resp = client.get("/api/v1/passenger-saved-addresses/")
        assert resp.status_code == 401

    def test_driver_cannot_list(self, client: TestClient, driver_headers: dict):
        resp = client.get("/api/v1/passenger-saved-addresses/", headers=driver_headers)
        assert resp.status_code == 403

    def test_passenger_can_list(self, client: TestClient, auth_headers: dict):
        resp = client.get("/api/v1/passenger-saved-addresses/", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


# ── CRUD ──────────────────────────────────────────────────────────────────────

class TestAddressCRUD:
    created_id: str | None = None

    def test_create_address(self, client: TestClient, auth_headers: dict):
        resp = client.post(
            "/api/v1/passenger-saved-addresses/",
            json=_addr_payload(),
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["label"] == "Zuhause"
        assert data["street_address"] == "Musterstraße 12"
        assert data["postal_code"] == "10115"
        assert data["city"] == "Berlin"
        assert data["address_type"] == "home"
        assert data["is_default_pickup"] is True
        assert data["is_active"] is True
        assert "id" in data
        TestAddressCRUD.created_id = data["id"]

    def test_list_includes_created(self, client: TestClient, auth_headers: dict):
        resp = client.get("/api/v1/passenger-saved-addresses/", headers=auth_headers)
        assert resp.status_code == 200
        ids = [a["id"] for a in resp.json()]
        assert TestAddressCRUD.created_id in ids

    def test_update_address(self, client: TestClient, auth_headers: dict):
        resp = client.patch(
            f"/api/v1/passenger-saved-addresses/{TestAddressCRUD.created_id}",
            json={"label": "Mein Zuhause", "city": "München"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["label"] == "Mein Zuhause"
        assert data["city"] == "München"
        assert data["street_address"] == "Musterstraße 12"  # unchanged

    def test_get_nonexistent_returns_404(self, client: TestClient, auth_headers: dict):
        resp = client.patch(
            f"/api/v1/passenger-saved-addresses/{uuid.uuid4()}",
            json={"label": "X"},
            headers=auth_headers,
        )
        assert resp.status_code == 404

    def test_delete_address(self, client: TestClient, auth_headers: dict):
        resp = client.delete(
            f"/api/v1/passenger-saved-addresses/{TestAddressCRUD.created_id}",
            headers=auth_headers,
        )
        assert resp.status_code == 204

    def test_deleted_not_listed(self, client: TestClient, auth_headers: dict):
        resp = client.get("/api/v1/passenger-saved-addresses/", headers=auth_headers)
        assert resp.status_code == 200
        ids = [a["id"] for a in resp.json()]
        assert TestAddressCRUD.created_id not in ids


# ── Validierung ───────────────────────────────────────────────────────────────

class TestAddressValidation:
    def test_missing_label_returns_422(self, client: TestClient, auth_headers: dict):
        payload = _addr_payload()
        del payload["label"]
        resp = client.post("/api/v1/passenger-saved-addresses/", json=payload, headers=auth_headers)
        assert resp.status_code == 422

    def test_blank_label_returns_422(self, client: TestClient, auth_headers: dict):
        resp = client.post(
            "/api/v1/passenger-saved-addresses/",
            json=_addr_payload(label=""),
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_whitespace_label_returns_422(self, client: TestClient, auth_headers: dict):
        resp = client.post(
            "/api/v1/passenger-saved-addresses/",
            json=_addr_payload(label="   "),
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_missing_street_returns_422(self, client: TestClient, auth_headers: dict):
        payload = _addr_payload()
        del payload["street_address"]
        resp = client.post("/api/v1/passenger-saved-addresses/", json=payload, headers=auth_headers)
        assert resp.status_code == 422

    def test_blank_street_returns_422(self, client: TestClient, auth_headers: dict):
        resp = client.post(
            "/api/v1/passenger-saved-addresses/",
            json=_addr_payload(street_address=""),
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_missing_postal_code_returns_422(self, client: TestClient, auth_headers: dict):
        payload = _addr_payload()
        del payload["postal_code"]
        resp = client.post("/api/v1/passenger-saved-addresses/", json=payload, headers=auth_headers)
        assert resp.status_code == 422

    def test_missing_city_returns_422(self, client: TestClient, auth_headers: dict):
        payload = _addr_payload()
        del payload["city"]
        resp = client.post("/api/v1/passenger-saved-addresses/", json=payload, headers=auth_headers)
        assert resp.status_code == 422

    def test_invalid_address_type_returns_422(self, client: TestClient, auth_headers: dict):
        resp = client.post(
            "/api/v1/passenger-saved-addresses/",
            json=_addr_payload(address_type="invalid_type"),
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_label_is_stripped(self, client: TestClient, auth_headers: dict):
        resp = client.post(
            "/api/v1/passenger-saved-addresses/",
            json=_addr_payload(label="  Schule  "),
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["label"] == "Schule"
        client.delete(f"/api/v1/passenger-saved-addresses/{data['id']}", headers=auth_headers)

    def test_patch_blank_label_returns_422(self, client: TestClient, auth_headers: dict):
        create = client.post(
            "/api/v1/passenger-saved-addresses/",
            json=_addr_payload(label="Werkstatt"),
            headers=auth_headers,
        )
        assert create.status_code == 201
        aid = create.json()["id"]
        resp = client.patch(
            f"/api/v1/passenger-saved-addresses/{aid}",
            json={"label": ""},
            headers=auth_headers,
        )
        assert resp.status_code == 422
        client.delete(f"/api/v1/passenger-saved-addresses/{aid}", headers=auth_headers)

    def test_patch_blank_city_returns_422(self, client: TestClient, auth_headers: dict):
        create = client.post(
            "/api/v1/passenger-saved-addresses/",
            json=_addr_payload(label="Arztpraxis"),
            headers=auth_headers,
        )
        assert create.status_code == 201
        aid = create.json()["id"]
        resp = client.patch(
            f"/api/v1/passenger-saved-addresses/{aid}",
            json={"city": ""},
            headers=auth_headers,
        )
        assert resp.status_code == 422
        client.delete(f"/api/v1/passenger-saved-addresses/{aid}", headers=auth_headers)

    def test_minimal_address_works(self, client: TestClient, auth_headers: dict):
        resp = client.post(
            "/api/v1/passenger-saved-addresses/",
            json={
                "label": "Minimal",
                "street_address": "Hauptstraße 1",
                "postal_code": "12345",
                "city": "Teststadt",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["address_type"] == "other"
        assert data["is_active"] is True
        assert data["is_default_pickup"] is False
        assert data["additional_info"] is None
        client.delete(f"/api/v1/passenger-saved-addresses/{data['id']}", headers=auth_headers)

    def test_driver_cannot_create(self, client: TestClient, driver_headers: dict):
        resp = client.post(
            "/api/v1/passenger-saved-addresses/",
            json=_addr_payload(),
            headers=driver_headers,
        )
        assert resp.status_code == 403

    def test_driver_cannot_delete(self, client: TestClient, auth_headers: dict, driver_headers: dict):
        create = client.post(
            "/api/v1/passenger-saved-addresses/",
            json=_addr_payload(label="Für Fahrer-Test"),
            headers=auth_headers,
        )
        assert create.status_code == 201
        aid = create.json()["id"]
        resp = client.delete(
            f"/api/v1/passenger-saved-addresses/{aid}",
            headers=driver_headers,
        )
        assert resp.status_code == 403
        client.delete(f"/api/v1/passenger-saved-addresses/{aid}", headers=auth_headers)

    def test_default_pickup_flag_saved(self, client: TestClient, auth_headers: dict):
        resp = client.post(
            "/api/v1/passenger-saved-addresses/",
            json=_addr_payload(label="Standard-Abholung", is_default_pickup=True),
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["is_default_pickup"] is True
        client.delete(f"/api/v1/passenger-saved-addresses/{data['id']}", headers=auth_headers)

    def test_all_address_types_accepted(self, client: TestClient, auth_headers: dict):
        for atype in ["home", "school", "work_workshop", "daycare", "doctor", "other"]:
            resp = client.post(
                "/api/v1/passenger-saved-addresses/",
                json=_addr_payload(label=f"Test {atype}", address_type=atype),
                headers=auth_headers,
            )
            assert resp.status_code == 201, f"address_type={atype} failed"
            client.delete(
                f"/api/v1/passenger-saved-addresses/{resp.json()['id']}",
                headers=auth_headers,
            )
