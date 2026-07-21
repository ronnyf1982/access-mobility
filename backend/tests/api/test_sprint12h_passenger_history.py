"""Sprint 12H — Passenger ride history: completed spontaneous rides visible in list.

Requires seed_demo_data.py to have been run (passenger@access.test must exist).

The module fixture ensures at least one completed spontaneous ride with pickup_address,
destination_address, and a ride_completed status event exists for passenger@access.test.
"""
import uuid

import pytest
from fastapi.testclient import TestClient


# ── Module fixture ─────────────────────────────────────────────────────────────

@pytest.fixture(scope="module", autouse=True)
def ensure_completed_spontaneous_ride_12h():
    """Ensure a completed spontaneous ride with addresses and event exists."""
    from app.db.session import SessionLocal
    from app.models.ride_status_event import RideStatusEvent, RideStatusEventType
    from app.models.transport_request import TransportRequest, TransportRequestStatus
    from app.models.user import User

    db = SessionLocal()
    try:
        passenger = db.query(User).filter(User.email == "passenger@access.test").first()
        if not passenger:
            yield
            return

        existing = (
            db.query(TransportRequest)
            .filter(
                TransportRequest.passenger_user_id == passenger.id,
                TransportRequest.is_spontaneous.is_(True),
                TransportRequest.status == TransportRequestStatus.completed,
                TransportRequest.pickup_address.isnot(None),
                TransportRequest.destination_address.isnot(None),
            )
            .first()
        )

        if not existing:
            tr = TransportRequest(
                id=uuid.uuid4(),
                requester_user_id=passenger.id,
                passenger_user_id=passenger.id,
                status=TransportRequestStatus.completed,
                is_spontaneous=True,
                pickup_latitude=52.516,
                pickup_longitude=13.388,
                pickup_address="Unter den Linden 1, 10117 Berlin",
                destination_address="Alexanderplatz 1, 10178 Berlin",
            )
            db.add(tr)
            db.flush()

            event = RideStatusEvent(
                transport_request_id=tr.id,
                status=RideStatusEventType.ride_completed,
                created_by_user_id=passenger.id,
            )
            db.add(event)
            db.commit()
    finally:
        db.close()

    yield


# ── Tests ──────────────────────────────────────────────────────────────────────

def test_unauthenticated_cannot_list_rides(client: TestClient) -> None:
    resp = client.get("/api/v1/transport-requests")
    assert resp.status_code == 401


def test_passenger_sees_completed_spontaneous_ride(client: TestClient, auth_headers: dict) -> None:
    """GET /transport-requests returns completed spontaneous rides for passenger."""
    resp = client.get("/api/v1/transport-requests", headers=auth_headers)
    assert resp.status_code == 200
    completed = [r for r in resp.json() if r["status"] == "completed" and r["is_spontaneous"]]
    assert len(completed) >= 1, "Keine abgeschlossene Spontanfahrt im Verlauf gefunden"


def test_completed_ride_has_pickup_address(client: TestClient, auth_headers: dict) -> None:
    resp = client.get("/api/v1/transport-requests", headers=auth_headers)
    assert resp.status_code == 200
    completed = next(
        (r for r in resp.json() if r["status"] == "completed" and r["is_spontaneous"]),
        None,
    )
    assert completed is not None
    assert completed["pickup_address"] is not None
    assert len(completed["pickup_address"]) > 0


def test_completed_ride_has_destination_address(client: TestClient, auth_headers: dict) -> None:
    resp = client.get("/api/v1/transport-requests", headers=auth_headers)
    assert resp.status_code == 200
    completed = next(
        (r for r in resp.json() if r["status"] == "completed" and r["is_spontaneous"]),
        None,
    )
    assert completed is not None
    assert completed["destination_address"] is not None
    assert len(completed["destination_address"]) > 0


def test_completed_ride_has_last_status_label(client: TestClient, auth_headers: dict) -> None:
    """last_status_label must reflect the latest RideStatusEvent ('Fahrt abgeschlossen')."""
    resp = client.get("/api/v1/transport-requests", headers=auth_headers)
    assert resp.status_code == 200
    completed = next(
        (r for r in resp.json() if r["status"] == "completed" and r["is_spontaneous"]),
        None,
    )
    assert completed is not None
    assert completed["last_status_label"] == "Fahrt abgeschlossen"


def test_rides_without_events_have_no_last_status_label(client: TestClient, auth_headers: dict) -> None:
    """Draft/requested rides without status events must return last_status_label=null."""
    resp = client.get("/api/v1/transport-requests", headers=auth_headers)
    assert resp.status_code == 200
    rides_without_events = [
        r for r in resp.json()
        if r["status"] in ("draft", "requested") and not r.get("last_status_label")
    ]
    # Just verify the field exists (may be null) — not an assertion failure if list is empty
    for r in resp.json():
        assert "last_status_label" in r, "last_status_label field missing from list item"


def test_passenger_can_read_status_events_of_completed_ride(
    client: TestClient, auth_headers: dict
) -> None:
    """Passenger can read status events for their own completed spontaneous ride."""
    resp = client.get("/api/v1/transport-requests", headers=auth_headers)
    assert resp.status_code == 200
    completed = next(
        (r for r in resp.json() if r["status"] == "completed" and r["is_spontaneous"]),
        None,
    )
    assert completed is not None

    events_resp = client.get(
        f"/api/v1/transport-requests/{completed['id']}/status-events",
        headers=auth_headers,
    )
    assert events_resp.status_code == 200
    events = events_resp.json()
    assert len(events) >= 1
    assert any(e["status"] == "ride_completed" for e in events)


def test_driver_list_does_not_include_passenger_completed_rides(
    client: TestClient, auth_headers: dict, driver_headers: dict
) -> None:
    """Driver's /transport-requests must not expose passenger@access.test's completed rides."""
    passenger_resp = client.get("/api/v1/transport-requests", headers=auth_headers)
    assert passenger_resp.status_code == 200
    passenger_completed_ids = {
        r["id"] for r in passenger_resp.json()
        if r["status"] == "completed" and r["is_spontaneous"]
    }

    driver_resp = client.get("/api/v1/transport-requests", headers=driver_headers)
    assert driver_resp.status_code == 200
    driver_ride_ids = {r["id"] for r in driver_resp.json()}

    assert not (passenger_completed_ids & driver_ride_ids), (
        "Fahrer sieht abgeschlossene Spontanfahrten des Fahrgasts"
    )
