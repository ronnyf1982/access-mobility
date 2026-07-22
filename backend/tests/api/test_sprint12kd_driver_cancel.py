"""Sprint 12K-D — Fahrer-Stornierung angenommener spontaner Fahrten.

Tests:
  1.  Fahrer kann zugewiesene spontane Fahrt vor Fahrgastaufnahme stornieren → 200.
  2.  Status nach Storno ist driver_declined (Auto-Rematch-Logik wurde ausgeführt).
  3.  Fahrt erscheint nicht mehr in Fahrer-Assignments nach Storno.
  4.  Fahrer-Storno nach passenger_picked_up → 409.
  5.  Fahrer-Storno nach ride_started → 409.
  6.  Fahrer kann nur eigene Fahrt stornieren → 403.
  7.  Nicht-Fahrer (Fahrgast) kann Endpoint nicht nutzen → 403.
  8.  Nicht gefundene Fahrt → 404.
  9.  Storno im Status spontaneous_requested (nicht assigned) → 409.
  10. Nach Fahrer-Storno ist Fahrer wieder für neue Anfragen verfügbar.
  11. 12G Statusflow bleibt grün: ride_completed → TR-Status completed, nicht in assignments.
  12. 12J Fahrgast-Storno bleibt grün: Fahrgast kann assigned Fahrt vor pickup stornieren.

Requires seed_demo_data.py (driver@access.test / passenger@access.test).
"""
import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient


# ── Modul-Fixture ─────────────────────────────────────────────────────────────

@pytest.fixture(scope="module", autouse=True)
def ensure_fresh_shift_12kd():
    """Frische aktive Schicht für driver@access.test / AM-VAN-1."""
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

        # driver2-Fahrten bereinigen (verhindert Zustandsverschmutzung für sprint11)
        driver2_user = db.query(User).filter(User.email == "driver2@access.test").first()
        if driver2_user:
            profile2 = db.query(DriverProfile).filter(DriverProfile.user_id == driver2_user.id).first()
            if profile2:
                for tr in db.query(TransportRequest).filter(
                    TransportRequest.assigned_driver_profile_id == profile2.id,
                    TransportRequest.status == TransportRequestStatus.assigned,
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


# ── Shared state ──────────────────────────────────────────────────────────────

_state: dict = {}
_BERLIN = {"pickup_latitude": 52.516, "pickup_longitude": 13.388}


def _book_and_accept(client: TestClient, auth_headers: dict, driver_headers: dict) -> str:
    """Buch eine Fahrt und lass den Fahrer sie annehmen. Gibt request_id zurück."""
    resp = client.post("/api/v1/spontaneous-rides/matches", json=_BERLIN, headers=auth_headers)
    assert resp.status_code == 200, f"Matching fehlgeschlagen: {resp.text}"
    matches = resp.json()
    assert len(matches) >= 1, "Kein Fahrer verfügbar"
    m = matches[0]
    book = client.post(
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
    assert book.status_code == 201, f"Buchung fehlgeschlagen: {book.text}"
    request_id = book.json()["request_id"]

    accept = client.post(
        f"/api/v1/driver/spontaneous-ride-requests/{request_id}/accept",
        headers=driver_headers,
    )
    assert accept.status_code == 200, f"Annehmen fehlgeschlagen: {accept.text}"
    assert accept.json()["status"] == "assigned"
    return request_id


def _force_complete_ride(request_id: str) -> None:
    """Setzt eine Fahrt direkt in DB auf completed, um Testblockierungen aufzulösen."""
    from app.db.session import SessionLocal
    from app.models.transport_request import TransportRequest, TransportRequestStatus
    db = SessionLocal()
    try:
        tr = db.get(TransportRequest, uuid.UUID(request_id))
        if tr:
            tr.status = TransportRequestStatus.completed
            db.commit()
    finally:
        db.close()


def _create_assigned_ride_with_event(event_status: str) -> str:
    """Legt direkt in DB eine assigned Fahrt mit einem Status-Event an."""
    from app.db.session import SessionLocal
    from app.models.driver_profile import DriverProfile
    from app.models.ride_status_event import RideStatusEvent, RideStatusEventType
    from app.models.transport_request import TransportRequest, TransportRequestStatus
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
            status=TransportRequestStatus.assigned,
            is_spontaneous=True,
            pickup_latitude=52.516,
            pickup_longitude=13.388,
            pickup_address="Test-Abholort",
            destination_address="Test-Ziel",
            assigned_driver_profile_id=profile.id,
            assigned_vehicle_id=vehicle.id,
            assigned_at=datetime.now(timezone.utc),
            rematch_group_id=uuid.uuid4(),
            rematch_attempt=0,
        )
        db.add(req)
        db.flush()

        evt = RideStatusEvent(
            transport_request_id=req.id,
            status=RideStatusEventType(event_status),
            created_by_user_id=driver_user.id,
        )
        db.add(evt)
        db.commit()
        return str(req.id)
    finally:
        db.close()


# ── 1+2. Fahrer kann vor Fahrgastaufnahme stornieren → driver_declined ────────

def test_driver_can_cancel_assigned_ride_before_pickup(
    client: TestClient, auth_headers: dict, driver_headers: dict,
) -> None:
    request_id = _book_and_accept(client, auth_headers, driver_headers)
    _state["cancelled_before_pickup_id"] = request_id

    resp = client.post(
        f"/api/v1/driver/spontaneous-ride-requests/{request_id}/cancel",
        headers=driver_headers,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "driver_declined"


# ── 3. Fahrt erscheint nicht mehr in Assignments ──────────────────────────────

def test_cancelled_ride_not_in_driver_assignments(
    client: TestClient, driver_headers: dict,
) -> None:
    assert "cancelled_before_pickup_id" in _state
    resp = client.get("/api/v1/driver/assignments", headers=driver_headers)
    assert resp.status_code == 200
    ids = [r["id"] for r in resp.json()]
    assert _state["cancelled_before_pickup_id"] not in ids


# ── 4. Storno nach passenger_picked_up → 409 ─────────────────────────────────

def test_driver_cannot_cancel_after_passenger_picked_up(
    client: TestClient, driver_headers: dict,
) -> None:
    request_id = _create_assigned_ride_with_event("passenger_picked_up")

    resp = client.post(
        f"/api/v1/driver/spontaneous-ride-requests/{request_id}/cancel",
        headers=driver_headers,
    )
    assert resp.status_code == 409, resp.text
    assert "Fahrgastaufnahme" in resp.json()["detail"]
    _force_complete_ride(request_id)


# ── 5. Storno nach ride_started → 409 ────────────────────────────────────────

def test_driver_cannot_cancel_after_ride_started(
    client: TestClient, driver_headers: dict,
) -> None:
    request_id = _create_assigned_ride_with_event("ride_started")

    resp = client.post(
        f"/api/v1/driver/spontaneous-ride-requests/{request_id}/cancel",
        headers=driver_headers,
    )
    assert resp.status_code == 409, resp.text
    _force_complete_ride(request_id)


# ── 6. Fahrer kann nur eigene Fahrt stornieren → 403 ─────────────────────────

def test_driver_cannot_cancel_other_drivers_ride(
    client: TestClient, auth_headers: dict, driver_headers: dict,
) -> None:
    """Direkt in DB eine Fahrt mit driver2@access.test anlegen, Fahrer A versucht Storno."""
    from app.db.session import SessionLocal
    from app.models.driver_profile import DriverProfile
    from app.models.driver_shift import DriverShift, ShiftStatus
    from app.models.transport_request import TransportRequest, TransportRequestStatus
    from app.models.user import User
    from app.models.vehicle import Vehicle

    db = SessionLocal()
    try:
        driver2_user = db.query(User).filter(User.email == "driver2@access.test").first()
        if not driver2_user:
            pytest.skip("driver2@access.test nicht in Seed-Daten vorhanden")
        profile2 = db.query(DriverProfile).filter(DriverProfile.user_id == driver2_user.id).first()
        vehicle2 = db.query(Vehicle).filter(Vehicle.license_plate.ilike("AM-BUS-1")).first()
        passenger = db.query(User).filter(User.email == "passenger@access.test").first()

        if not profile2 or not vehicle2:
            pytest.skip("Fahrer 2 / AM-BUS-1 nicht in Seed-Daten")

        req = TransportRequest(
            id=uuid.uuid4(),
            requester_user_id=passenger.id,
            passenger_user_id=passenger.id,
            status=TransportRequestStatus.assigned,
            is_spontaneous=True,
            pickup_latitude=52.516,
            pickup_longitude=13.388,
            assigned_driver_profile_id=profile2.id,
            assigned_vehicle_id=vehicle2.id,
            assigned_at=datetime.now(timezone.utc),
            rematch_group_id=uuid.uuid4(),
            rematch_attempt=0,
        )
        db.add(req)
        db.commit()
        request_id = str(req.id)
    finally:
        db.close()

    # Fahrer A (driver_headers) versucht Fahrt von Fahrer B zu stornieren → 403
    resp = client.post(
        f"/api/v1/driver/spontaneous-ride-requests/{request_id}/cancel",
        headers=driver_headers,
    )
    assert resp.status_code == 403, resp.text
    _force_complete_ride(request_id)


# ── 7. Nicht-Fahrer (Fahrgast) → 403 ─────────────────────────────────────────

def test_passenger_cannot_use_driver_cancel_endpoint(
    client: TestClient, auth_headers: dict, driver_headers: dict,
) -> None:
    request_id = _book_and_accept(client, auth_headers, driver_headers)

    resp = client.post(
        f"/api/v1/driver/spontaneous-ride-requests/{request_id}/cancel",
        headers=auth_headers,  # Fahrgast-Headers
    )
    assert resp.status_code == 403, resp.text

    # Aufräumen: Fahrgast storniert regulär
    client.post(f"/api/v1/spontaneous-rides/{request_id}/cancel", headers=auth_headers)


# ── 8. Nicht gefundene Fahrt → 404 ───────────────────────────────────────────

def test_driver_cancel_nonexistent_ride_returns_404(
    client: TestClient, driver_headers: dict,
) -> None:
    resp = client.post(
        f"/api/v1/driver/spontaneous-ride-requests/{uuid.uuid4()}/cancel",
        headers=driver_headers,
    )
    assert resp.status_code == 404


# ── 9. Storno im Status spontaneous_requested → 409 ──────────────────────────

def test_driver_cancel_returns_409_for_non_assigned_status(
    client: TestClient, auth_headers: dict, driver_headers: dict,
) -> None:
    """Status spontaneous_requested ist kein assigned → 409."""
    resp = client.post("/api/v1/spontaneous-rides/matches", json=_BERLIN, headers=auth_headers)
    assert resp.status_code == 200
    matches = resp.json()
    assert len(matches) >= 1
    m = matches[0]
    book = client.post(
        "/api/v1/spontaneous-rides/book",
        json={
            **_BERLIN,
            "driver_id": m["driver_id"],
            "vehicle_id": m["vehicle_id"],
            "pickup_address": "Test",
            "destination_address": "Test-Ziel",
        },
        headers=auth_headers,
    )
    assert book.status_code == 201
    request_id = book.json()["request_id"]

    # Fahrt ist noch spontaneous_requested (nicht accepted) → 409
    resp2 = client.post(
        f"/api/v1/driver/spontaneous-ride-requests/{request_id}/cancel",
        headers=driver_headers,
    )
    assert resp2.status_code == 409

    # Aufräumen
    client.post(f"/api/v1/spontaneous-rides/{request_id}/cancel", headers=auth_headers)


# ── 10. Nach Fahrer-Storno ist Fahrer wieder verfügbar ───────────────────────

def test_driver_available_for_new_requests_after_cancel(
    client: TestClient, auth_headers: dict, driver_headers: dict,
) -> None:
    request_id = _book_and_accept(client, auth_headers, driver_headers)

    cancel_resp = client.post(
        f"/api/v1/driver/spontaneous-ride-requests/{request_id}/cancel",
        headers=driver_headers,
    )
    assert cancel_resp.status_code == 200

    # Fahrer soll wieder im Matching erscheinen
    match_resp = client.post("/api/v1/spontaneous-rides/matches", json=_BERLIN, headers=auth_headers)
    assert match_resp.status_code == 200
    assert len(match_resp.json()) >= 1, "Fahrer sollte nach Storno wieder verfügbar sein"


# ── 11. Regression: 12G ride_completed → TR-Status completed ─────────────────

def test_12g_regression_ride_completed_removes_from_assignments(
    client: TestClient, auth_headers: dict, driver_headers: dict,
) -> None:
    """Sicherstellen dass ride_completed den TR-Status auf completed setzt."""
    request_id = _book_and_accept(client, auth_headers, driver_headers)

    for ev in ["driver_on_way", "driver_arrived", "passenger_picked_up", "ride_started", "ride_completed"]:
        resp = client.post(
            f"/api/v1/driver/transport-requests/{request_id}/status-events",
            json={"status": ev},
            headers=driver_headers,
        )
        assert resp.status_code == 201, f"Event {ev} fehlgeschlagen: {resp.text}"

    assignments = client.get("/api/v1/driver/assignments", headers=driver_headers)
    assert assignments.status_code == 200
    ids = [r["id"] for r in assignments.json()]
    assert request_id not in ids, "Abgeschlossene Fahrt darf nicht in Assignments erscheinen"


# ── 12. Regression: 12J Fahrgast-Storno bleibt grün ─────────────────────────

def test_12j_regression_passenger_can_cancel_assigned_ride(
    client: TestClient, auth_headers: dict, driver_headers: dict,
) -> None:
    request_id = _book_and_accept(client, auth_headers, driver_headers)

    resp = client.post(
        f"/api/v1/spontaneous-rides/{request_id}/cancel",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"
