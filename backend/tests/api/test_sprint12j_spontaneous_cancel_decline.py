"""Sprint 12J — Fahrgast-Stornierung und Fahrer-Ablehnung für spontane Fahrten.

Testet:
  1.  Fahrgast kann eigene spontaneous_requested Fahrt stornieren → 200.
  2.  Fahrgast kann eigene assigned Fahrt stornieren, solange kein Pickup-Event → 200.
  3.  Fremder Fahrgast kann nicht stornieren → 403.
  4.  Nicht gefundene Fahrt → 404.
  5.  Completed Fahrt kann nicht storniert werden → 409.
  6.  Bereits stornierte Fahrt → 409.
  7.  Nach Stornierung ist Fahrer wieder verfügbar (Matching gibt Treffer).
  8.  Fahrer sieht stornierte Anfrage nicht mehr als spontaneous_requested.
  9.  Fahrer kann Anfrage ablehnen → driver_declined.
  10. Nach Ablehnung sieht Fahrer sie nicht mehr in seiner Liste.
  11. Tracking liefert driver_declined-Status für Fahrgast.
  12. Stornierte Fahrt erscheint in Fahrgast-Transportanfragen.
  13. Abgelehnte Fahrt erscheint in Fahrgast-Transportanfragen mit driver_declined.
  14. Stornierung nach passenger_picked_up Event → 409.

Requires seed_demo_data.py (driver@access.test / passenger@access.test).
"""

import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient


# ── Modul-Fixture ──────────────────────────────────────────────────────────────

@pytest.fixture(scope="module", autouse=True)
def ensure_fresh_shift_12j():
    """Frische aktive Schicht für driver@access.test / AM-VAN-1. Räumt vorhandene Fahrten auf."""
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
            TransportRequest.assigned_driver_profile_id == profile.id,
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


def _book_ride(client: TestClient, auth_headers: dict) -> str:
    resp = client.post("/api/v1/spontaneous-rides/matches", json=_BERLIN, headers=auth_headers)
    assert resp.status_code == 200, f"Matching fehlgeschlagen: {resp.text}"
    matches = resp.json()
    assert len(matches) >= 1, "Kein freier Fahrer für Buchung gefunden"
    m = matches[0]
    resp2 = client.post(
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
    assert resp2.status_code == 201, f"Buchung fehlgeschlagen: {resp2.text}"
    return resp2.json()["request_id"]


def _create_db_ride(
    status,
    *,
    is_spontaneous: bool = True,
    with_passenger_picked_up_event: bool = False,
) -> str:
    """Legt eine TransportRequest direkt in der DB an und gibt die ID zurück."""
    from app.db.session import SessionLocal
    from app.models.driver_profile import DriverProfile
    from app.models.ride_status_event import RideStatusEvent, RideStatusEventType
    from app.models.transport_request import TransportRequest
    from app.models.user import User
    from app.models.vehicle import Vehicle

    db = SessionLocal()
    try:
        driver_user = db.query(User).filter(User.email == "driver@access.test").first()
        profile = db.query(DriverProfile).filter(DriverProfile.user_id == driver_user.id).first()
        vehicle = db.query(Vehicle).filter(Vehicle.license_plate.ilike("AM-VAN-1")).first()
        passenger = db.query(User).filter(User.email == "passenger@access.test").first()

        req = TransportRequest(
            id=uuid.uuid4(),
            requester_user_id=passenger.id,
            passenger_user_id=passenger.id,
            status=status,
            is_spontaneous=is_spontaneous,
            pickup_latitude=52.516,
            pickup_longitude=13.388,
            pickup_address="Test-Abholort, 10117 Berlin",
            destination_address="Test-Ziel, 10178 Berlin",
            assigned_driver_profile_id=profile.id,
            assigned_vehicle_id=vehicle.id,
            assigned_at=datetime.now(timezone.utc),
        )
        db.add(req)
        db.flush()

        if with_passenger_picked_up_event:
            event = RideStatusEvent(
                transport_request_id=req.id,
                status=RideStatusEventType.passenger_picked_up,
                created_by_user_id=driver_user.id,
            )
            db.add(event)

        db.commit()
        return str(req.id)
    finally:
        db.close()


# ── 1. Fahrgast kann spontaneous_requested Fahrt stornieren ───────────────────

def test_passenger_can_cancel_requested_ride(
    client: TestClient, auth_headers: dict,
) -> None:
    request_id = _book_ride(client, auth_headers)
    _state["cancelable_requested_id"] = request_id

    resp = client.post(
        f"/api/v1/spontaneous-rides/{request_id}/cancel",
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "cancelled"


# ── 2. Fahrgast kann assigned Fahrt stornieren (kein Pickup-Event) ─────────────

def test_passenger_can_cancel_assigned_ride_before_pickup(
    client: TestClient, auth_headers: dict, driver_headers: dict,
) -> None:
    request_id = _book_ride(client, auth_headers)

    # Fahrer nimmt an
    accept_resp = client.post(
        f"/api/v1/driver/spontaneous-ride-requests/{request_id}/accept",
        headers=driver_headers,
    )
    assert accept_resp.status_code == 200
    _state["assigned_before_pickup_id"] = request_id

    # Fahrgast storniert
    resp = client.post(
        f"/api/v1/spontaneous-rides/{request_id}/cancel",
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "cancelled"


# ── 3. Fremder Fahrgast kann nicht stornieren → 403 ───────────────────────────

def test_other_passenger_cannot_cancel(
    client: TestClient, auth_headers: dict, driver_headers: dict,
) -> None:
    request_id = _book_ride(client, auth_headers)
    _state["third_party_test_id"] = request_id

    # driver_headers gehört dem Fahrer → kein Fahrgast → 403
    resp = client.post(
        f"/api/v1/spontaneous-rides/{request_id}/cancel",
        headers=driver_headers,
    )
    assert resp.status_code == 403

    # Fahrzeug freigeben: Fahrgast storniert sauber, damit folgende Tests buchen können
    cleanup = client.post(
        f"/api/v1/spontaneous-rides/{request_id}/cancel",
        headers=auth_headers,
    )
    assert cleanup.status_code == 200


# ── 4. Nicht gefundene Fahrt → 404 ────────────────────────────────────────────

def test_cancel_nonexistent_ride_returns_404(
    client: TestClient, auth_headers: dict,
) -> None:
    resp = client.post(
        f"/api/v1/spontaneous-rides/{uuid.uuid4()}/cancel",
        headers=auth_headers,
    )
    assert resp.status_code == 404


# ── 5. Completed Fahrt kann nicht storniert werden → 409 ─────────────────────

def test_cancel_completed_ride_returns_409(
    client: TestClient, auth_headers: dict, driver_headers: dict,
) -> None:
    from app.models.transport_request import TransportRequestStatus

    request_id = _book_ride(client, auth_headers)
    accept = client.post(
        f"/api/v1/driver/spontaneous-ride-requests/{request_id}/accept",
        headers=driver_headers,
    )
    assert accept.status_code == 200

    for ev in ["driver_on_way", "driver_arrived", "passenger_picked_up", "ride_started", "ride_completed"]:
        client.post(
            f"/api/v1/driver/transport-requests/{request_id}/status-events",
            json={"status": ev},
            headers=driver_headers,
        )

    resp = client.post(
        f"/api/v1/spontaneous-rides/{request_id}/cancel",
        headers=auth_headers,
    )
    assert resp.status_code == 409
    assert "nicht mehr storniert" in resp.json()["detail"]


# ── 6. Bereits stornierte Fahrt → 409 ─────────────────────────────────────────

def test_cancel_already_cancelled_ride_returns_409(
    client: TestClient, auth_headers: dict,
) -> None:
    request_id = _book_ride(client, auth_headers)
    first = client.post(
        f"/api/v1/spontaneous-rides/{request_id}/cancel",
        headers=auth_headers,
    )
    assert first.status_code == 200

    second = client.post(
        f"/api/v1/spontaneous-rides/{request_id}/cancel",
        headers=auth_headers,
    )
    assert second.status_code == 409
    assert "bereits storniert" in second.json()["detail"]


# ── 7. Nach Stornierung ist Fahrer wieder verfügbar ───────────────────────────

def test_driver_available_after_passenger_cancels(
    client: TestClient, auth_headers: dict, driver_headers: dict,
) -> None:
    # Buchung, Fahrer nimmt an, Fahrgast storniert
    request_id = _book_ride(client, auth_headers)
    client.post(
        f"/api/v1/driver/spontaneous-ride-requests/{request_id}/accept",
        headers=driver_headers,
    )
    client.post(
        f"/api/v1/spontaneous-rides/{request_id}/cancel",
        headers=auth_headers,
    )

    # Fahrer soll wieder im Matching erscheinen
    resp = client.post("/api/v1/spontaneous-rides/matches", json=_BERLIN, headers=auth_headers)
    assert resp.status_code == 200
    # Liste muss mindestens einen Fahrer enthalten (Fahrer ist wieder frei)
    assert len(resp.json()) >= 1, "Fahrer sollte nach Stornierung wieder verfügbar sein"


# ── 8. Fahrer sieht stornierte Anfrage nicht mehr ────────────────────────────

def test_driver_does_not_see_cancelled_ride_in_open_requests(
    client: TestClient, auth_headers: dict, driver_headers: dict,
) -> None:
    request_id = _book_ride(client, auth_headers)
    client.post(
        f"/api/v1/spontaneous-rides/{request_id}/cancel",
        headers=auth_headers,
    )

    resp = client.get("/api/v1/driver/spontaneous-ride-requests", headers=driver_headers)
    assert resp.status_code == 200
    ids_in_response = [r["id"] for r in resp.json()]
    assert request_id not in ids_in_response, "Stornierte Anfrage darf nicht in offener Liste erscheinen"


# ── 9. Fahrer kann Anfrage ablehnen ───────────────────────────────────────────

def test_driver_can_decline_request(
    client: TestClient, auth_headers: dict, driver_headers: dict,
) -> None:
    request_id = _book_ride(client, auth_headers)
    _state["declined_request_id"] = request_id

    resp = client.post(
        f"/api/v1/driver/spontaneous-ride-requests/{request_id}/decline",
        headers=driver_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "driver_declined"


# ── 10. Nach Ablehnung sieht Fahrer sie nicht mehr ───────────────────────────

def test_driver_does_not_see_declined_ride_in_open_requests(
    client: TestClient, driver_headers: dict,
) -> None:
    assert "declined_request_id" in _state
    declined_id = _state["declined_request_id"]

    resp = client.get("/api/v1/driver/spontaneous-ride-requests", headers=driver_headers)
    assert resp.status_code == 200
    ids_in_response = [r["id"] for r in resp.json()]
    assert declined_id not in ids_in_response, "Abgelehnte Anfrage darf nicht in offener Liste erscheinen"


# ── 11. Tracking liefert driver_declined für Fahrgast ─────────────────────────

def test_tracking_returns_driver_declined_status(
    client: TestClient, auth_headers: dict,
) -> None:
    assert "declined_request_id" in _state
    declined_id = _state["declined_request_id"]

    resp = client.get(
        f"/api/v1/spontaneous-rides/{declined_id}/tracking",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "driver_declined"
    assert data["can_track"] is False


# ── 12. Stornierte Fahrt erscheint in Fahrgast-Anfragen ──────────────────────

def test_cancelled_ride_appears_in_passenger_requests(
    client: TestClient, auth_headers: dict,
) -> None:
    assert "cancelable_requested_id" in _state
    cancelled_id = _state["cancelable_requested_id"]

    resp = client.get("/api/v1/transport-requests", headers=auth_headers)
    assert resp.status_code == 200
    ids_and_statuses = {r["id"]: r["status"] for r in resp.json()}
    assert cancelled_id in ids_and_statuses, "Stornierte Fahrt fehlt in Fahrgastliste"
    assert ids_and_statuses[cancelled_id] == "cancelled"


# ── 13. Abgelehnte Fahrt erscheint in Fahrgast-Anfragen mit driver_declined ───

def test_declined_ride_appears_in_passenger_requests(
    client: TestClient, auth_headers: dict,
) -> None:
    assert "declined_request_id" in _state
    declined_id = _state["declined_request_id"]

    resp = client.get("/api/v1/transport-requests", headers=auth_headers)
    assert resp.status_code == 200
    ids_and_statuses = {r["id"]: r["status"] for r in resp.json()}
    assert declined_id in ids_and_statuses, "Abgelehnte Fahrt fehlt in Fahrgastliste"
    assert ids_and_statuses[declined_id] == "driver_declined"


# ── 14. Stornierung nach passenger_picked_up Event → 409 ─────────────────────

def test_cancel_after_passenger_picked_up_returns_409(
    client: TestClient, auth_headers: dict,
) -> None:
    from app.models.transport_request import TransportRequestStatus

    request_id = _create_db_ride(
        TransportRequestStatus.assigned,
        with_passenger_picked_up_event=True,
    )

    resp = client.post(
        f"/api/v1/spontaneous-rides/{request_id}/cancel",
        headers=auth_headers,
    )
    assert resp.status_code == 409
    assert "nicht mehr storniert" in resp.json()["detail"]
