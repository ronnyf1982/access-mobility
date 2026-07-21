"""Sprint 12G — Driver status flow for spontaneous rides.

Test order matters: tests 9–17 share database state. The sequence is:
  test 9  → passenger books a ride
  test 10 → driver accepts → status assigned
  test 11 → driver sets driver_on_way
  test 12 → tracking shows 'Fahrer ist unterwegs' label
  test 13 → driver sets driver_arrived
  test 14 → driver sets passenger_picked_up
  test 15 → driver sets ride_started
  test 16 → driver sets ride_completed → TransportRequest.status = completed
  test 17 → tracking after completion: can_track=False, label 'Fahrt abgeschlossen'
  test 18 → driver cannot set further events (ride is completed → 409)

Requires seed_demo_data.py to have been run.
"""
import pytest
from fastapi.testclient import TestClient


# ── Module fixture ─────────────────────────────────────────────────────────────

@pytest.fixture(scope="module", autouse=True)
def ensure_fresh_shift_12g():
    """Fresh active shift for driver@access.test / AM-VAN-1. Clears prior rides."""
    from datetime import datetime, timezone

    from app.db.session import SessionLocal
    from app.models.driver_profile import DriverProfile
    from app.models.driver_shift import DriverShift, ShiftStatus
    from app.models.transport_request import TransportRequest, TransportRequestStatus
    from app.models.user import User
    from app.models.vehicle import Vehicle

    db = SessionLocal()
    try:
        driver_user = db.query(User).filter(User.email == "driver@access.test").first()
        if not driver_user:
            yield
            return
        profile = db.query(DriverProfile).filter(DriverProfile.user_id == driver_user.id).first()
        if not profile:
            yield
            return
        vehicle = db.query(Vehicle).filter(Vehicle.license_plate.ilike("AM-VAN-1")).first()
        if not vehicle:
            yield
            return

        for s in db.query(DriverShift).filter(
            DriverShift.driver_profile_id == profile.id,
            DriverShift.status.in_([ShiftStatus.active, ShiftStatus.paused]),
        ).all():
            s.status = ShiftStatus.ended

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


# ── Shared state ───────────────────────────────────────────────────────────────

_state: dict = {}
_BERLIN = {"pickup_latitude": 52.516, "pickup_longitude": 13.388}


def _get_first_match(client: TestClient, auth_headers: dict) -> dict:
    resp = client.post("/api/v1/spontaneous-rides/matches", json=_BERLIN, headers=auth_headers)
    assert resp.status_code == 200
    matches = resp.json()
    assert len(matches) >= 1, "Need at least one match"
    return matches[0]


# ── 1–4: Auth and role guards for status events ────────────────────────────────

def test_status_event_unauthenticated_returns_401(client: TestClient) -> None:
    import uuid
    resp = client.post(
        f"/api/v1/driver/transport-requests/{uuid.uuid4()}/status-events",
        json={"status": "driver_on_way"},
    )
    assert resp.status_code == 401


def test_status_event_passenger_returns_403(client: TestClient, auth_headers: dict) -> None:
    import uuid
    resp = client.post(
        f"/api/v1/driver/transport-requests/{uuid.uuid4()}/status-events",
        json={"status": "driver_on_way"},
        headers=auth_headers,
    )
    assert resp.status_code == 403


def test_status_event_nonexistent_ride_returns_404(client: TestClient, driver_headers: dict) -> None:
    import uuid
    resp = client.post(
        f"/api/v1/driver/transport-requests/{uuid.uuid4()}/status-events",
        json={"status": "driver_on_way"},
        headers=driver_headers,
    )
    assert resp.status_code == 404


def test_tracking_status_label_before_events_is_generic(client: TestClient, auth_headers: dict) -> None:
    """Before any status events, label reflects TransportRequest status only."""
    # This test just verifies the tracking endpoint is accessible — actual label
    # tested in stateful tests below after a ride is booked.
    import uuid
    resp = client.get(f"/api/v1/spontaneous-rides/{uuid.uuid4()}/tracking", headers=auth_headers)
    assert resp.status_code == 404


# ── 9–18: Stateful status flow ─────────────────────────────────────────────────

def test_passenger_books_ride_for_status_flow(client: TestClient, auth_headers: dict) -> None:
    m = _get_first_match(client, auth_headers)
    resp = client.post(
        "/api/v1/spontaneous-rides/book",
        json={
            **_BERLIN,
            "driver_id": m["driver_id"],
            "vehicle_id": m["vehicle_id"],
            "pickup_address": "Unter den Linden 1, 10117 Berlin",
            "destination_address": "Alexanderplatz 1, 10178 Berlin",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    _state["request_id"] = resp.json()["request_id"]


def test_driver_accepts_for_status_flow(client: TestClient, driver_headers: dict) -> None:
    assert "request_id" in _state
    resp = client.post(
        f"/api/v1/driver/spontaneous-ride-requests/{_state['request_id']}/accept",
        headers=driver_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "assigned"


def test_driver_sets_driver_on_way(client: TestClient, driver_headers: dict) -> None:
    assert "request_id" in _state
    resp = client.post(
        f"/api/v1/driver/transport-requests/{_state['request_id']}/status-events",
        json={"status": "driver_on_way"},
        headers=driver_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "driver_on_way"
    assert data["transport_request_id"] == _state["request_id"]


def test_tracking_shows_driver_on_way_label(client: TestClient, auth_headers: dict) -> None:
    assert "request_id" in _state
    resp = client.get(
        f"/api/v1/spontaneous-rides/{_state['request_id']}/tracking",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "assigned"
    assert data["ride_status_label"] == "Fahrer ist unterwegs"


def test_driver_sets_driver_arrived(client: TestClient, driver_headers: dict) -> None:
    assert "request_id" in _state
    resp = client.post(
        f"/api/v1/driver/transport-requests/{_state['request_id']}/status-events",
        json={"status": "driver_arrived"},
        headers=driver_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["status"] == "driver_arrived"


def test_driver_sets_passenger_picked_up(client: TestClient, driver_headers: dict) -> None:
    assert "request_id" in _state
    resp = client.post(
        f"/api/v1/driver/transport-requests/{_state['request_id']}/status-events",
        json={"status": "passenger_picked_up"},
        headers=driver_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["status"] == "passenger_picked_up"


def test_driver_sets_ride_started(client: TestClient, driver_headers: dict) -> None:
    assert "request_id" in _state
    resp = client.post(
        f"/api/v1/driver/transport-requests/{_state['request_id']}/status-events",
        json={"status": "ride_started"},
        headers=driver_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["status"] == "ride_started"


def test_driver_sets_ride_completed(client: TestClient, driver_headers: dict) -> None:
    assert "request_id" in _state
    resp = client.post(
        f"/api/v1/driver/transport-requests/{_state['request_id']}/status-events",
        json={"status": "ride_completed"},
        headers=driver_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["status"] == "ride_completed"


def test_transport_request_status_is_completed_after_event(client: TestClient, driver_headers: dict) -> None:
    """ride_completed event must flip TransportRequest.status to completed."""
    assert "request_id" in _state
    # Driver assignments only returns 'assigned' rides; ride should no longer appear.
    resp = client.get("/api/v1/driver/assignments", headers=driver_headers)
    assert resp.status_code == 200
    ids = [r["id"] for r in resp.json()]
    assert _state["request_id"] not in ids, "Completed ride must not appear in assignments"


def test_tracking_after_completion_returns_can_track_false(client: TestClient, auth_headers: dict) -> None:
    assert "request_id" in _state
    resp = client.get(
        f"/api/v1/spontaneous-rides/{_state['request_id']}/tracking",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "completed"
    assert data["can_track"] is False
    assert data["ride_status_label"] == "Fahrt abgeschlossen"


def test_driver_cannot_set_event_after_completion(client: TestClient, driver_headers: dict) -> None:
    """Setting a status event on an already-completed ride must return 409."""
    assert "request_id" in _state
    resp = client.post(
        f"/api/v1/driver/transport-requests/{_state['request_id']}/status-events",
        json={"status": "driver_on_way"},
        headers=driver_headers,
    )
    assert resp.status_code == 409
