"""Sprint 7 — Matching & Disposition API tests.

Tests run against the real PostgreSQL database using seed data
(passenger@access.test + Sprint 7 seed transport requests).
"""
import pytest
from fastapi.testclient import TestClient


def _get_request_by_status(client, headers, status: str) -> dict | None:
    resp = client.get("/api/v1/transport-requests", headers=headers)
    assert resp.status_code == 200
    for req in resp.json():
        if req["status"] == status:
            return req
    return None


def _get_request_by_address(client, headers, address_fragment: str) -> dict | None:
    resp = client.get("/api/v1/transport-requests", headers=headers)
    assert resp.status_code == 200
    for req in resp.json():
        if req.get("pickup_address") and address_fragment in req["pickup_address"]:
            return req
    return None


# ── GET matching-options ───────────────────────────────────────────────────────


class TestMatchingOptions:
    def test_returns_vehicles_and_drivers(self, client: TestClient, auth_headers: dict):
        req = _get_request_by_status(client, auth_headers, "requested")
        assert req is not None, "No 'requested' transport request found in seed data"
        resp = client.get(
            f"/api/v1/transport-requests/{req['id']}/matching-options",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "request_id" in data
        assert "vehicles" in data
        assert "drivers" in data
        assert data["request_id"] == req["id"]

    def test_vehicle_option_has_required_fields(self, client: TestClient, auth_headers: dict):
        req = _get_request_by_status(client, auth_headers, "requested")
        assert req is not None
        resp = client.get(
            f"/api/v1/transport-requests/{req['id']}/matching-options",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        vehicles = resp.json()["vehicles"]
        if vehicles:
            v = vehicles[0]
            for field in ("vehicle_id", "name", "license_plate", "vehicle_type", "status", "reasons",
                          "missing_requirements", "matched_requirements"):
                assert field in v, f"Missing field: {field}"
            assert v["status"] in ("suitable", "warning", "unsuitable")

    def test_driver_option_has_required_fields(self, client: TestClient, auth_headers: dict):
        req = _get_request_by_status(client, auth_headers, "requested")
        assert req is not None
        resp = client.get(
            f"/api/v1/transport-requests/{req['id']}/matching-options",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        drivers = resp.json()["drivers"]
        if drivers:
            d = drivers[0]
            for field in ("driver_profile_id", "display_name", "status", "reasons",
                          "missing_requirements", "matched_requirements"):
                assert field in d, f"Missing field: {field}"
            assert d["status"] in ("suitable", "warning", "unsuitable")

    def test_good_match_seed_has_suitable_vehicle(self, client: TestClient, auth_headers: dict):
        """Sprint 7 Seed 1 (Müllerstraße) should show at least one suitable vehicle."""
        req = _get_request_by_address(client, auth_headers, "Müllerstraße")
        assert req is not None, "Sprint 7 seed 1 not found"
        resp = client.get(
            f"/api/v1/transport-requests/{req['id']}/matching-options",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        statuses = [v["status"] for v in resp.json()["vehicles"]]
        assert "suitable" in statuses, f"Expected suitable vehicle, got: {statuses}"

    def test_warning_seed_has_no_suitable_vehicle(self, client: TestClient, auth_headers: dict):
        """Sprint 7 Seed 2 (Sonnenallee / stretcher_ride) should have no suitable vehicles."""
        req = _get_request_by_address(client, auth_headers, "Sonnenallee")
        assert req is not None, "Sprint 7 seed 2 not found"
        resp = client.get(
            f"/api/v1/transport-requests/{req['id']}/matching-options",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        statuses = [v["status"] for v in resp.json()["vehicles"]]
        assert "suitable" not in statuses, f"Expected no suitable vehicle for stretcher seed, got: {statuses}"

    def test_404_for_unknown_request(self, client: TestClient, auth_headers: dict):
        resp = client.get(
            "/api/v1/transport-requests/00000000-0000-0000-0000-000000000000/matching-options",
            headers=auth_headers,
        )
        assert resp.status_code == 404


# ── POST assign ───────────────────────────────────────────────────────────────


class TestAssign:
    def _get_vehicle_and_driver(self, client: TestClient, headers: dict, request_id: str):
        """Return first active vehicle_id and driver_profile_id from matching-options."""
        resp = client.get(
            f"/api/v1/transport-requests/{request_id}/matching-options",
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        vehicle_id = data["vehicles"][0]["vehicle_id"] if data["vehicles"] else None
        driver_id = data["drivers"][0]["driver_profile_id"] if data["drivers"] else None
        return vehicle_id, driver_id

    def test_assign_requested_request(self, client: TestClient, auth_headers: dict):
        req = _get_request_by_address(client, auth_headers, "Müllerstraße")
        assert req is not None
        if req["status"] == "assigned":
            # Already assigned from previous test run — unassign first
            client.post(
                f"/api/v1/transport-requests/{req['id']}/unassign",
                headers=auth_headers,
            )
            req["status"] = "requested"

        vehicle_id, driver_id = self._get_vehicle_and_driver(client, auth_headers, req["id"])
        assert vehicle_id and driver_id

        resp = client.post(
            f"/api/v1/transport-requests/{req['id']}/assign",
            headers=auth_headers,
            json={
                "vehicle_id": vehicle_id,
                "driver_profile_id": driver_id,
                "assignment_notes": "Test-Zuweisung Sprint 7",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "assigned"
        assert data["assigned_vehicle_id"] == vehicle_id
        assert data["assigned_driver_profile_id"] == driver_id
        assert data["assignment_notes"] == "Test-Zuweisung Sprint 7"
        assert data["assigned_at"] is not None

    def test_assign_cancelled_request_returns_409(self, client: TestClient, auth_headers: dict):
        req = _get_request_by_status(client, auth_headers, "cancelled")
        if req is None:
            pytest.skip("No cancelled transport request in seed data")
        vehicle_id, driver_id = self._get_vehicle_and_driver(client, auth_headers,
                                                              # Use any requested request for IDs
                                                              _get_request_by_status(client, auth_headers, "requested")["id"])
        resp = client.post(
            f"/api/v1/transport-requests/{req['id']}/assign",
            headers=auth_headers,
            json={"vehicle_id": vehicle_id, "driver_profile_id": driver_id},
        )
        assert resp.status_code == 409

    def test_assign_draft_request_returns_409(self, client: TestClient, auth_headers: dict):
        req = _get_request_by_status(client, auth_headers, "draft")
        assert req is not None, "No draft transport request found"
        vehicle_id, driver_id = self._get_vehicle_and_driver(client, auth_headers,
                                                              _get_request_by_status(client, auth_headers, "requested")["id"])
        resp = client.post(
            f"/api/v1/transport-requests/{req['id']}/assign",
            headers=auth_headers,
            json={"vehicle_id": vehicle_id, "driver_profile_id": driver_id},
        )
        assert resp.status_code == 409

    def test_assign_nonexistent_vehicle_returns_422(self, client: TestClient, auth_headers: dict):
        req = _get_request_by_status(client, auth_headers, "requested")
        assert req is not None
        resp = client.post(
            f"/api/v1/transport-requests/{req['id']}/assign",
            headers=auth_headers,
            json={
                "vehicle_id": "00000000-0000-0000-0000-000000000000",
                "driver_profile_id": "00000000-0000-0000-0000-000000000001",
            },
        )
        assert resp.status_code == 422

    def test_assign_nonexistent_driver_returns_422(self, client: TestClient, auth_headers: dict):
        req = _get_request_by_status(client, auth_headers, "requested")
        assert req is not None
        vehicle_id, _ = self._get_vehicle_and_driver(client, auth_headers, req["id"])
        assert vehicle_id
        resp = client.post(
            f"/api/v1/transport-requests/{req['id']}/assign",
            headers=auth_headers,
            json={
                "vehicle_id": vehicle_id,
                "driver_profile_id": "00000000-0000-0000-0000-000000000001",
            },
        )
        assert resp.status_code == 422


# ── POST unassign ─────────────────────────────────────────────────────────────


class TestUnassign:
    def test_unassign_assigned_request(self, client: TestClient, auth_headers: dict):
        req = _get_request_by_status(client, auth_headers, "assigned")
        if req is None:
            pytest.skip("No assigned transport request (run test_assign first)")
        resp = client.post(
            f"/api/v1/transport-requests/{req['id']}/unassign",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "requested"
        assert data["assigned_vehicle_id"] is None
        assert data["assigned_driver_profile_id"] is None
        assert data["assigned_at"] is None

    def test_unassign_non_assigned_returns_409(self, client: TestClient, auth_headers: dict):
        req = _get_request_by_status(client, auth_headers, "requested")
        assert req is not None
        resp = client.post(
            f"/api/v1/transport-requests/{req['id']}/unassign",
            headers=auth_headers,
        )
        assert resp.status_code == 409

    def test_unassign_404_unknown(self, client: TestClient, auth_headers: dict):
        resp = client.post(
            "/api/v1/transport-requests/00000000-0000-0000-0000-000000000000/unassign",
            headers=auth_headers,
        )
        assert resp.status_code == 404


# ── Rollenbasierte Disposition (provider / dispatcher) ────────────────────────


class TestRoleBasedDisposition:
    """provider_admin und dispatcher sehen alle requested/assigned Anfragen."""

    def test_passenger_sees_only_own_requests(self, client: TestClient, auth_headers: dict):
        resp = client.get("/api/v1/transport-requests", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) > 0, "Passenger should see their own requests"
        # All returned requests must belong to passenger (requester or passenger field)
        me = client.get("/api/v1/auth/me", headers=auth_headers).json()
        for req in data:
            assert req["requester_user_id"] == me["id"] or req["passenger_user_id"] == me["id"], \
                f"Request {req['id']} does not belong to passenger"

    def test_provider_sees_requested_and_assigned(self, client: TestClient, provider_headers: dict):
        resp = client.get("/api/v1/transport-requests", headers=provider_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) > 0, "Provider should see requested/assigned requests"
        for req in data:
            assert req["status"] in ("requested", "assigned"), \
                f"Provider list contains unexpected status: {req['status']}"

    def test_dispatcher_sees_requested_and_assigned(self, client: TestClient, dispatcher_headers: dict):
        resp = client.get("/api/v1/transport-requests", headers=dispatcher_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) > 0, "Dispatcher should see requested/assigned requests"
        for req in data:
            assert req["status"] in ("requested", "assigned")

    def test_provider_can_load_matching_options(self, client: TestClient, provider_headers: dict):
        resp = client.get("/api/v1/transport-requests", headers=provider_headers)
        assert resp.status_code == 200
        requests = resp.json()
        assert requests, "Provider needs at least one request to test matching"
        req_id = requests[0]["id"]
        match_resp = client.get(
            f"/api/v1/transport-requests/{req_id}/matching-options",
            headers=provider_headers,
        )
        assert match_resp.status_code == 200
        data = match_resp.json()
        assert "vehicles" in data and "drivers" in data

    def test_provider_can_assign_and_unassign(self, client: TestClient, provider_headers: dict):
        resp = client.get("/api/v1/transport-requests", headers=provider_headers)
        req = next((r for r in resp.json() if r["status"] == "requested"), None)
        if req is None:
            pytest.skip("No requested request available for provider assign test")

        # Get matching options to obtain valid vehicle/driver IDs
        match = client.get(
            f"/api/v1/transport-requests/{req['id']}/matching-options",
            headers=provider_headers,
        ).json()
        assert match["vehicles"] and match["drivers"]
        vehicle_id = match["vehicles"][0]["vehicle_id"]
        driver_id = match["drivers"][0]["driver_profile_id"]

        # Assign
        assign_resp = client.post(
            f"/api/v1/transport-requests/{req['id']}/assign",
            headers=provider_headers,
            json={
                "vehicle_id": vehicle_id,
                "driver_profile_id": driver_id,
                "assignment_notes": "Provider-Test Sprint 7",
            },
        )
        assert assign_resp.status_code == 200
        assert assign_resp.json()["status"] == "assigned"

        # Unassign
        unassign_resp = client.post(
            f"/api/v1/transport-requests/{req['id']}/unassign",
            headers=provider_headers,
        )
        assert unassign_resp.status_code == 200
        assert unassign_resp.json()["status"] == "requested"

    def test_provider_cannot_access_draft_requests(self, client: TestClient, provider_headers: dict):
        """Draft requests must not appear in provider's disposition list."""
        resp = client.get("/api/v1/transport-requests", headers=provider_headers)
        assert resp.status_code == 200
        for req in resp.json():
            assert req["status"] != "draft", "Draft requests must not appear in provider list"

    def test_provider_cannot_access_cancelled_requests(self, client: TestClient, provider_headers: dict):
        """Cancelled requests must not appear in provider's disposition list."""
        resp = client.get("/api/v1/transport-requests", headers=provider_headers)
        assert resp.status_code == 200
        for req in resp.json():
            assert req["status"] != "cancelled", "Cancelled requests must not appear in provider list"


# ── Fahrgast-Kontaktdaten in API-Responses ────────────────────────────────────


class TestPassengerDisplayFields:
    """Fahrgast-Kontaktdaten erscheinen für Dispo-Rollen; Felder existieren auch für Fahrgäste."""

    def test_provider_list_contains_passenger_display_name(
        self, client: TestClient, provider_headers: dict
    ):
        resp = client.get("/api/v1/transport-requests", headers=provider_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) > 0, "Provider must see at least one request"
        for req in data:
            assert "passenger_display_name" in req, "passenger_display_name missing from list item"
            assert req["passenger_display_name"] is not None, (
                f"passenger_display_name should not be None for request {req['id']}"
            )

    def test_provider_list_contains_passenger_phone_field(
        self, client: TestClient, provider_headers: dict
    ):
        resp = client.get("/api/v1/transport-requests", headers=provider_headers)
        assert resp.status_code == 200
        for req in resp.json():
            assert "passenger_phone" in req, "passenger_phone missing from list item"

    def test_provider_list_contains_passenger_email_field(
        self, client: TestClient, provider_headers: dict
    ):
        resp = client.get("/api/v1/transport-requests", headers=provider_headers)
        assert resp.status_code == 200
        for req in resp.json():
            assert "passenger_email" in req, "passenger_email missing from list item"
            assert req["passenger_email"] is not None, "passenger_email should be populated"

    def test_provider_detail_contains_all_passenger_fields(
        self, client: TestClient, provider_headers: dict
    ):
        requests = client.get("/api/v1/transport-requests", headers=provider_headers).json()
        assert requests, "Provider needs at least one request"
        req_id = requests[0]["id"]
        detail = client.get(
            f"/api/v1/transport-requests/{req_id}", headers=provider_headers
        )
        assert detail.status_code == 200
        data = detail.json()
        for field in (
            "passenger_display_name",
            "passenger_email",
            "passenger_phone",
            "passenger_emergency_contact_name",
            "passenger_emergency_contact_phone",
        ):
            assert field in data, f"Field {field} missing from detail response"

    def test_passenger_list_has_display_name_populated(
        self, client: TestClient, auth_headers: dict
    ):
        """Fahrgäste sehen ihre eigenen Anfragen mit Fahrgastname (sie selbst sind der Fahrgast)."""
        resp = client.get("/api/v1/transport-requests", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        for req in data:
            assert "passenger_display_name" in req
            assert req["passenger_display_name"] is not None, (
                "passenger_display_name should be populated for own requests"
            )
