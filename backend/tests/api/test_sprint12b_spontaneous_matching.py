"""Sprint 12B — Spontaneous ride matching tests.

Depends on seed_demo_data.py having been run:
- driver@access.test has active DriverShift with AM-VAN-1 (lat=52.525, lon=13.402)
  → wheelchair-capable vehicle, not assigned to active transport request
- driver2@access.test has PAUSED DriverShift with AM-CAR-1
  → excluded because shift is not active
- AM-BUS-1 is assigned to a transport request (status=assigned)
  → excluded even if a shift exists
- passenger@access.test has MobilityProfile: uses_wheelchair, needs_ramp, requires_wheelchair_space
"""
import pytest
from fastapi.testclient import TestClient


# ── Helpers ───────────────────────────────────────────────────────────────────

_BERLIN_CENTER = {"pickup_latitude": 52.516, "pickup_longitude": 13.388}
_INVALID_COORDS = {"pickup_latitude": 999.0, "pickup_longitude": 0.0}


# ── Authentication ────────────────────────────────────────────────────────────

def test_unauthenticated_returns_401(client: TestClient) -> None:
    resp = client.post("/api/v1/spontaneous-rides/matches", json=_BERLIN_CENTER)
    assert resp.status_code == 401


def test_driver_role_returns_403(client: TestClient, driver_headers: dict) -> None:
    resp = client.post(
        "/api/v1/spontaneous-rides/matches",
        json=_BERLIN_CENTER,
        headers=driver_headers,
    )
    assert resp.status_code == 403


# ── Validation ────────────────────────────────────────────────────────────────

def test_invalid_latitude_returns_422(client: TestClient, auth_headers: dict) -> None:
    resp = client.post(
        "/api/v1/spontaneous-rides/matches",
        json=_INVALID_COORDS,
        headers=auth_headers,
    )
    assert resp.status_code == 422


def test_invalid_longitude_returns_422(client: TestClient, auth_headers: dict) -> None:
    resp = client.post(
        "/api/v1/spontaneous-rides/matches",
        json={"pickup_latitude": 52.5, "pickup_longitude": 999.0},
        headers=auth_headers,
    )
    assert resp.status_code == 422


# ── Passenger happy-path ──────────────────────────────────────────────────────

def test_passenger_receives_valid_response(client: TestClient, auth_headers: dict) -> None:
    resp = client.post(
        "/api/v1/spontaneous-rides/matches",
        json=_BERLIN_CENTER,
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


def test_response_contains_no_sensitive_driver_data(
    client: TestClient, auth_headers: dict
) -> None:
    resp = client.post(
        "/api/v1/spontaneous-rides/matches",
        json=_BERLIN_CENTER,
        headers=auth_headers,
    )
    assert resp.status_code == 200
    for item in resp.json():
        assert "phone" not in item
        assert "email" not in item
        assert "password" not in item
        assert "license_plate" not in item


def test_response_schema_fields(client: TestClient, auth_headers: dict) -> None:
    resp = client.post(
        "/api/v1/spontaneous-rides/matches",
        json=_BERLIN_CENTER,
        headers=auth_headers,
    )
    assert resp.status_code == 200
    for item in resp.json():
        assert "driver_id" in item
        assert "driver_display_name" in item
        assert "vehicle_id" in item
        assert "vehicle_label" in item
        assert "vehicle_type" in item
        assert "vehicle_latitude" in item
        assert "vehicle_longitude" in item
        assert "distance_km" in item
        assert "estimated_arrival_minutes" in item
        assert "matched_capabilities" in item
        assert item["can_accept_now"] is True


def test_eta_minimum_is_3_minutes(client: TestClient, auth_headers: dict) -> None:
    resp = client.post(
        "/api/v1/spontaneous-rides/matches",
        json=_BERLIN_CENTER,
        headers=auth_headers,
    )
    assert resp.status_code == 200
    for item in resp.json():
        assert item["estimated_arrival_minutes"] >= 3


def test_results_sorted_by_distance(client: TestClient, auth_headers: dict) -> None:
    resp = client.post(
        "/api/v1/spontaneous-rides/matches",
        json=_BERLIN_CENTER,
        headers=auth_headers,
    )
    assert resp.status_code == 200
    distances = [item["distance_km"] for item in resp.json()]
    assert distances == sorted(distances)


# ── Filtering ─────────────────────────────────────────────────────────────────

def test_paused_driver_is_excluded(client: TestClient, auth_headers: dict) -> None:
    """driver2@access.test + AM-CAR-1 is paused → must not appear."""
    resp = client.post(
        "/api/v1/spontaneous-rides/matches",
        json=_BERLIN_CENTER,
        headers=auth_headers,
    )
    assert resp.status_code == 200
    vehicle_labels = [item["vehicle_label"] for item in resp.json()]
    assert "Standard-PKW 1" not in vehicle_labels


def test_assigned_vehicle_is_excluded(client: TestClient, auth_headers: dict) -> None:
    """AM-BUS-1 is assigned to a transport request → must not appear."""
    resp = client.post(
        "/api/v1/spontaneous-rides/matches",
        json=_BERLIN_CENTER,
        headers=auth_headers,
    )
    assert resp.status_code == 200
    vehicle_labels = [item["vehicle_label"] for item in resp.json()]
    assert "Rollstuhlbus 1" not in vehicle_labels


def test_passenger_cannot_search_for_other_passenger(
    client: TestClient, auth_headers: dict
) -> None:
    import uuid
    resp = client.post(
        "/api/v1/spontaneous-rides/matches",
        json={**_BERLIN_CENTER, "passenger_user_id": str(uuid.uuid4())},
        headers=auth_headers,
    )
    assert resp.status_code == 403


def test_dispatcher_can_search(client: TestClient, dispatcher_headers: dict) -> None:
    resp = client.post(
        "/api/v1/spontaneous-rides/matches",
        json=_BERLIN_CENTER,
        headers=dispatcher_headers,
    )
    assert resp.status_code == 200
