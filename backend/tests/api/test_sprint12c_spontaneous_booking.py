"""Sprint 12C — Spontaneous ride booking and driver acceptance tests.

Test order matters: tests 6–12 share database state. The sequence is:
  test 5  → driver sees empty spontaneous-ride-requests (before any booking)
  test 6  → passenger books AM-VAN-1 (driver@access.test) → spontaneous_requested
  test 7  → booking AM-VAN-1 again → 409 (vehicle blocked)
  test 8  → driver sees pending request
  test 9  → driver2 tries to accept → 403 (wrong driver)
  test 10 → matching excludes AM-VAN-1 (now spontaneous_requested)
  test 11 → driver accepts → 200, status = assigned
  test 12 → driver sees empty spontaneous-ride-requests (after accept)

Requires seed_demo_data.py to have been run. The ensure_active_driver_shift fixture
recreates the active shift for driver@/AM-VAN-1 in case earlier tests ended it.
"""
import pytest
from fastapi.testclient import TestClient


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module", autouse=True)
def ensure_active_driver_shift():
    """Ensure driver@access.test has an active shift with location for this module.

    Earlier test modules (Sprint 10, 12A) end the active shift as part of their
    own tests. This fixture creates a fresh one so Sprint 12C tests always have
    a bookable driver available.
    """
    from datetime import datetime, timezone

    from app.db.session import SessionLocal
    from app.models.driver_profile import DriverProfile
    from app.models.driver_shift import DriverShift, ShiftStatus
    from app.models.user import User
    from app.models.vehicle import Vehicle

    db = SessionLocal()
    try:
        driver_user = db.query(User).filter(User.email == "driver@access.test").first()
        if not driver_user:
            yield
            return
        profile = db.query(DriverProfile).filter(
            DriverProfile.user_id == driver_user.id
        ).first()
        if not profile:
            yield
            return
        vehicle = (
            db.query(Vehicle)
            .filter(Vehicle.license_plate.ilike("AM-VAN-1"))
            .first()
        )
        if not vehicle:
            yield
            return

        # End any existing active/paused shifts so start_shift wouldn't conflict
        for s in db.query(DriverShift).filter(
            DriverShift.driver_profile_id == profile.id,
            DriverShift.status.in_([ShiftStatus.active, ShiftStatus.paused]),
        ).all():
            s.status = ShiftStatus.ended

        # Complete any blocking rides from previous test runs so AM-VAN-1 appears in matches
        from app.models.transport_request import TransportRequest, TransportRequestStatus
        for tr in db.query(TransportRequest).filter(
            TransportRequest.assigned_vehicle_id == vehicle.id,
            TransportRequest.status.in_([
                TransportRequestStatus.assigned,
                TransportRequestStatus.spontaneous_requested,
            ]),
        ).all():
            tr.status = TransportRequestStatus.completed
        db.flush()

        shift = DriverShift(
            driver_profile_id=profile.id,
            vehicle_id=vehicle.id,
            status=ShiftStatus.active,
            started_at=datetime.now(timezone.utc),
            current_latitude=52.525,
            current_longitude=13.402,
        )
        db.add(shift)
        db.commit()
    finally:
        db.close()

    yield


@pytest.fixture(scope="module")
def driver2_headers(client: TestClient) -> dict:
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "driver2@access.test", "password": "Access123!"},
    )
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


# ── Helpers ───────────────────────────────────────────────────────────────────

_BERLIN_CENTER = {"pickup_latitude": 52.516, "pickup_longitude": 13.388}

# Shared state between tests (module scope)
_booked: dict = {}


def _get_driver_and_vehicle(client: TestClient, auth_headers: dict) -> tuple[str, str]:
    """Return (driver_id, vehicle_id) from the first match result."""
    resp = client.post(
        "/api/v1/spontaneous-rides/matches",
        json=_BERLIN_CENTER,
        headers=auth_headers,
    )
    assert resp.status_code == 200
    matches = resp.json()
    assert len(matches) >= 1, "Need at least one match for booking tests"
    m = matches[0]
    return m["driver_id"], m["vehicle_id"]


# ── 1. Authentication guard ───────────────────────────────────────────────────

def test_book_unauthenticated_returns_401(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/spontaneous-rides/book",
        json={**_BERLIN_CENTER, "driver_id": "00000000-0000-0000-0000-000000000001", "vehicle_id": "00000000-0000-0000-0000-000000000002"},
    )
    assert resp.status_code == 401


# ── 2. Role guard ─────────────────────────────────────────────────────────────

def test_book_driver_role_returns_403(client: TestClient, driver_headers: dict) -> None:
    resp = client.post(
        "/api/v1/spontaneous-rides/book",
        json={**_BERLIN_CENTER, "driver_id": "00000000-0000-0000-0000-000000000001", "vehicle_id": "00000000-0000-0000-0000-000000000002"},
        headers=driver_headers,
    )
    assert resp.status_code == 403


# ── 3. Validation ─────────────────────────────────────────────────────────────

def test_book_invalid_latitude_returns_422(client: TestClient, auth_headers: dict) -> None:
    resp = client.post(
        "/api/v1/spontaneous-rides/book",
        json={"pickup_latitude": 999.0, "pickup_longitude": 13.0,
              "driver_id": "00000000-0000-0000-0000-000000000001",
              "vehicle_id": "00000000-0000-0000-0000-000000000002"},
        headers=auth_headers,
    )
    assert resp.status_code == 422


# ── 4. Non-existent driver ────────────────────────────────────────────────────

def test_book_nonexistent_driver_returns_404(client: TestClient, auth_headers: dict) -> None:
    import uuid
    resp = client.post(
        "/api/v1/spontaneous-rides/book",
        json={**_BERLIN_CENTER,
              "driver_id": str(uuid.uuid4()),
              "vehicle_id": str(uuid.uuid4())},
        headers=auth_headers,
    )
    assert resp.status_code == 404


# ── 5. Driver sees empty list before booking ──────────────────────────────────

def test_driver_spontaneous_requests_empty_before_booking(
    client: TestClient, driver_headers: dict
) -> None:
    resp = client.get("/api/v1/driver/spontaneous-ride-requests", headers=driver_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert all(r["status"] != "spontaneous_requested" for r in data), \
        "Should have no pending spontaneous requests at start of test run"


# ── 6. Successful booking ─────────────────────────────────────────────────────

def test_book_success_returns_201(client: TestClient, auth_headers: dict) -> None:
    driver_id, vehicle_id = _get_driver_and_vehicle(client, auth_headers)
    resp = client.post(
        "/api/v1/spontaneous-rides/book",
        json={**_BERLIN_CENTER, "driver_id": driver_id, "vehicle_id": vehicle_id},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "request_id" in data
    assert data["status"] == "spontaneous_requested"
    assert data["driver_display_name"]
    assert data["vehicle_label"]
    assert data["estimated_arrival_minutes"] >= 3
    # Persist for subsequent tests
    _booked["request_id"] = data["request_id"]
    _booked["driver_id"] = driver_id
    _booked["vehicle_id"] = vehicle_id


# ── 7. Double booking → 409 ───────────────────────────────────────────────────

def test_book_same_vehicle_again_returns_409(client: TestClient, auth_headers: dict) -> None:
    assert "driver_id" in _booked, "test 6 must run first"
    resp = client.post(
        "/api/v1/spontaneous-rides/book",
        json={**_BERLIN_CENTER,
              "driver_id": _booked["driver_id"],
              "vehicle_id": _booked["vehicle_id"]},
        headers=auth_headers,
    )
    assert resp.status_code == 409


# ── 8. Driver sees pending request ────────────────────────────────────────────

def test_driver_sees_pending_spontaneous_request(
    client: TestClient, driver_headers: dict
) -> None:
    assert "request_id" in _booked, "test 6 must run first"
    resp = client.get("/api/v1/driver/spontaneous-ride-requests", headers=driver_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert any(r["id"] == _booked["request_id"] for r in data)
    item = next(r for r in data if r["id"] == _booked["request_id"])
    assert item["status"] == "spontaneous_requested"
    assert item["pickup_latitude"] is not None
    assert item["pickup_longitude"] is not None


# ── 9. Driver2 cannot accept another driver's request ─────────────────────────

def test_driver2_accept_foreign_request_returns_403(
    client: TestClient, driver2_headers: dict
) -> None:
    assert "request_id" in _booked, "test 6 must run first"
    resp = client.post(
        f"/api/v1/driver/spontaneous-ride-requests/{_booked['request_id']}/accept",
        headers=driver2_headers,
    )
    assert resp.status_code == 403


# ── 10. Matching excludes vehicle with spontaneous_requested status ────────────

def test_matching_excludes_booked_vehicle(client: TestClient, auth_headers: dict) -> None:
    assert "vehicle_id" in _booked, "test 6 must run first"
    resp = client.post(
        "/api/v1/spontaneous-rides/matches",
        json=_BERLIN_CENTER,
        headers=auth_headers,
    )
    assert resp.status_code == 200
    vehicle_ids = [m["vehicle_id"] for m in resp.json()]
    assert _booked["vehicle_id"] not in vehicle_ids, \
        "Booked vehicle must be excluded from match results"


# ── 11. Driver accepts → status becomes assigned ──────────────────────────────

def test_driver_accept_request_returns_200(
    client: TestClient, driver_headers: dict
) -> None:
    assert "request_id" in _booked, "test 6 must run first"
    resp = client.post(
        f"/api/v1/driver/spontaneous-ride-requests/{_booked['request_id']}/accept",
        headers=driver_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == _booked["request_id"]
    assert data["status"] == "assigned"


# ── 12. Driver spontaneous-ride-requests is empty after accept ────────────────

def test_driver_spontaneous_requests_empty_after_accept(
    client: TestClient, driver_headers: dict
) -> None:
    resp = client.get("/api/v1/driver/spontaneous-ride-requests", headers=driver_headers)
    assert resp.status_code == 200
    data = resp.json()
    request_ids = [r["id"] for r in data]
    assert _booked.get("request_id") not in request_ids, \
        "Accepted request must no longer appear in spontaneous-ride-requests"
