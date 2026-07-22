"""Sprint 12K - Automatische Weiterleitung bei Ablehnung oder Timeout.

Testet:
  1.  Buchung setzt rematch_group_id (UUID) und rematch_attempt=0.
  2.  Tracking eines ausstehenden spontanen TR liefert request_expires_at.
  3.  Tracking eines frischen TR hat next_request_id=null.
  4.  Fahrer1-Ablehnung loest Rematch aus (neuer TR fuer Fahrer2).
  4b. Fahrer B hat anderes, aber passendes Fahrzeug (AM-BUS-1 vs AM-VAN-1).
  5.  Neuer TR nach Rematch hat dieselbe rematch_group_id.
  6.  Neuer TR hat rematch_attempt=1 (inkrementiert).
  7.  Tracking des abgelehnten TR liefert next_request_id (neuer TR).
  8.  Fahrer2-Ablehnung: kein weiterer Fahrer -> next_request_id=null.
  9.  Manuelle Stornierung loest keinen Rematch aus.
  10. Timeout-Endpoint gibt 409, wenn TR noch nicht abgelaufen.
  11. Timeout-Endpoint loest Rematch aus, wenn created_at manipuliert.
  12. Timeout-Endpoint liefert SpontaneousRideTracking mit rematch-Feldern.
  13. Timeout-Endpoint: falscher Nutzer -> 403 oder 404.
  14. Timeout-Endpoint: falscher Status (bereits driver_declined) -> 409.

Requires seed_demo_data.py:
  driver@access.test  + AM-VAN-1
  driver2@access.test + AM-BUS-1
  passenger@access.test
  relative@access.test  (trusted_person_headers fixture)
"""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient


# -- Modul-Fixture -------------------------------------------------------------

@pytest.fixture(scope="module", autouse=True)
def ensure_fresh_shifts_12k():
    """Zwei aktive Schichten: driver@access.test/AM-VAN-1 + driver2@access.test/AM-BUS-1."""
    from app.db.session import SessionLocal
    from app.models.driver_profile import DriverProfile
    from app.models.driver_shift import DriverShift, ShiftStatus
    from app.models.transport_request import TransportRequest, TransportRequestStatus
    from app.models.user import User
    from app.models.vehicle import Vehicle

    db = SessionLocal()
    try:
        for email, plate, lat, lon in [
            ("driver@access.test",  "AM-VAN-1", 52.520, 13.395),
            ("driver2@access.test", "AM-BUS-1", 52.518, 13.399),
        ]:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                continue
            profile = db.query(DriverProfile).filter(DriverProfile.user_id == user.id).first()
            if not profile:
                continue
            vehicle = db.query(Vehicle).filter(Vehicle.license_plate.ilike(plate)).first()
            if not vehicle:
                continue

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
                current_latitude=lat,
                current_longitude=lon,
            )
            db.add(shift)

        db.commit()
    finally:
        db.close()

    yield


# -- Shared state --------------------------------------------------------------

_state: dict = {}
_BERLIN = {"pickup_latitude": 52.516, "pickup_longitude": 13.388}
_PICKUP_ADDR = "Unter den Linden 1, 10117 Berlin"
_DEST_ADDR   = "Alexanderplatz 1, 10178 Berlin"


def _find_and_book(client: TestClient, headers: dict) -> str:
    """Matcht und bucht eine spontane Fahrt. Gibt request_id zurueck."""
    resp = client.post("/api/v1/spontaneous-rides/matches", json=_BERLIN, headers=headers)
    assert resp.status_code == 200, f"Matching fehlgeschlagen: {resp.text}"
    matches = resp.json()
    assert len(matches) >= 1, "Kein freier Fahrer verfuegbar"
    m = matches[0]
    resp2 = client.post(
        "/api/v1/spontaneous-rides/book",
        json={
            **_BERLIN,
            "driver_id": m["driver_id"],
            "vehicle_id": m["vehicle_id"],
            "pickup_address": _PICKUP_ADDR,
            "destination_address": _DEST_ADDR,
        },
        headers=headers,
    )
    assert resp2.status_code == 201, f"Buchung fehlgeschlagen: {resp2.text}"
    return resp2.json()["request_id"]


def _login_headers(client: TestClient, email: str) -> dict:
    """Login mit Seed-Passwort, gibt Authorization-Header zurueck."""
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": "Access123!"})
    assert resp.status_code == 200, f"Login fehlgeschlagen fuer {email}: {resp.text}"
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


# -- Tests: Kette A (Buchung -> Ablehnung -> Rematch -> erschoepft) ------------

def test_book_sets_rematch_group_id(client: TestClient, auth_headers: dict):
    """Buchung setzt rematch_group_id und rematch_attempt=0 in der DB."""
    from app.db.session import SessionLocal
    from app.models.driver_profile import DriverProfile
    from app.models.transport_request import TransportRequest
    from app.models.user import User

    request_id = _find_and_book(client, auth_headers)
    _state["ride_a_id"] = request_id

    db = SessionLocal()
    try:
        tr = db.get(TransportRequest, uuid.UUID(request_id))
        assert tr is not None
        assert tr.rematch_group_id is not None, "rematch_group_id darf nicht None sein"
        assert tr.rematch_attempt == 0
        _state["group_id"] = str(tr.rematch_group_id)

        # Zugewiesenen Fahrer ermitteln, um korrekte Credentials fuer Ablehnung zu haben
        if tr.assigned_driver_profile_id:
            dp = db.get(DriverProfile, tr.assigned_driver_profile_id)
            if dp:
                u = db.get(User, dp.user_id)
                _state["ride_a_driver_email"] = u.email if u else None
    finally:
        db.close()


def test_tracking_returns_expires_at_for_pending(client: TestClient, auth_headers: dict):
    """Tracking eines ausstehenden spontanen TR liefert request_expires_at."""
    rid = _state["ride_a_id"]
    resp = client.get(f"/api/v1/spontaneous-rides/{rid}/tracking", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "spontaneous_requested"
    assert data["request_expires_at"] is not None, "request_expires_at muss gesetzt sein"


def test_tracking_next_request_id_null_initially(client: TestClient, auth_headers: dict):
    """Frisch gebuchte Fahrt hat noch kein next_request_id."""
    rid = _state["ride_a_id"]
    resp = client.get(f"/api/v1/spontaneous-rides/{rid}/tracking", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["next_request_id"] is None


def test_driver1_decline_triggers_rematch(client: TestClient):
    """Fahrer1 lehnt ab -> neuer TR fuer Fahrer2 wird erstellt."""
    from app.db.session import SessionLocal
    from app.models.driver_profile import DriverProfile
    from app.models.transport_request import TransportRequest, TransportRequestStatus
    from app.models.user import User

    driver_email = _state.get("ride_a_driver_email", "driver@access.test")
    headers = _login_headers(client, driver_email)
    rid = _state["ride_a_id"]
    resp = client.post(f"/api/v1/driver/spontaneous-ride-requests/{rid}/decline", headers=headers)
    assert resp.status_code == 200, f"Ablehnung fehlgeschlagen: {resp.text}"

    db = SessionLocal()
    try:
        tr1 = db.get(TransportRequest, uuid.UUID(rid))
        assert tr1 is not None
        assert tr1.status == TransportRequestStatus.driver_declined

        group_id = tr1.rematch_group_id
        trs_in_group = (
            db.query(TransportRequest)
            .filter(TransportRequest.rematch_group_id == group_id)
            .all()
        )
        assert len(trs_in_group) == 2, f"Erwartet 2 TRs in Gruppe, gefunden: {len(trs_in_group)}"

        tr2 = next((t for t in trs_in_group if str(t.id) != rid), None)
        assert tr2 is not None
        assert tr2.status == TransportRequestStatus.spontaneous_requested
        _state["ride_b_id"] = str(tr2.id)

        # Fahrer fuer ride_b ermitteln
        if tr2.assigned_driver_profile_id:
            dp = db.get(DriverProfile, tr2.assigned_driver_profile_id)
            if dp:
                u = db.get(User, dp.user_id)
                _state["ride_b_driver_email"] = u.email if u else None
    finally:
        db.close()


def test_rematch_driver_b_has_different_compatible_vehicle(client: TestClient):
    """Fahrer B hat ein anderes Fahrzeug als Fahrer A — aber trotzdem rollstuhltauglich."""
    from app.db.session import SessionLocal
    from app.models.transport_request import TransportRequest
    from app.models.vehicle import Vehicle

    db = SessionLocal()
    try:
        tr_a = db.get(TransportRequest, uuid.UUID(_state["ride_a_id"]))
        tr_b = db.get(TransportRequest, uuid.UUID(_state["ride_b_id"]))
        assert tr_a is not None and tr_b is not None

        assert tr_a.assigned_vehicle_id != tr_b.assigned_vehicle_id, \
            "Rematch muss anderes Fahrzeug verwenden als die abgelehnte Fahrt"

        vehicle_b = db.get(Vehicle, tr_b.assigned_vehicle_id)
        assert vehicle_b is not None
        assert vehicle_b.wheelchair_space_count >= 1, \
            f"Fahrzeug B ({vehicle_b.license_plate}) braucht Rollstuhlplatz"
        assert vehicle_b.has_ramp or vehicle_b.has_lift, \
            f"Fahrzeug B ({vehicle_b.license_plate}) braucht Rampe oder Lift"
        assert vehicle_b.has_wheelchair_restraint, \
            f"Fahrzeug B ({vehicle_b.license_plate}) braucht Rollstuhlsicherung"
    finally:
        db.close()


def test_rematch_new_tr_same_group_id(client: TestClient):
    """Neuer TR nach Rematch hat dieselbe rematch_group_id."""
    from app.db.session import SessionLocal
    from app.models.transport_request import TransportRequest

    db = SessionLocal()
    try:
        tr2 = db.get(TransportRequest, uuid.UUID(_state["ride_b_id"]))
        assert tr2 is not None
        assert str(tr2.rematch_group_id) == _state["group_id"]
    finally:
        db.close()


def test_rematch_new_tr_attempt_incremented(client: TestClient):
    """Neuer TR nach Rematch hat rematch_attempt=1."""
    from app.db.session import SessionLocal
    from app.models.transport_request import TransportRequest

    db = SessionLocal()
    try:
        tr2 = db.get(TransportRequest, uuid.UUID(_state["ride_b_id"]))
        assert tr2 is not None
        assert tr2.rematch_attempt == 1
    finally:
        db.close()


def test_tracking_declined_tr_has_next_request_id(client: TestClient, auth_headers: dict):
    """Tracking des abgelehnten TR (ride_a) liefert next_request_id -> ride_b."""
    rid = _state["ride_a_id"]
    resp = client.get(f"/api/v1/spontaneous-rides/{rid}/tracking", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "driver_declined"
    assert data["next_request_id"] == _state["ride_b_id"]


def test_driver2_decline_no_further_rematch(client: TestClient, auth_headers: dict):
    """Fahrer2 lehnt ab -> kein weiterer Fahrer -> next_request_id=null."""
    driver_email = _state.get("ride_b_driver_email", "driver2@access.test")
    headers = _login_headers(client, driver_email)
    rid = _state["ride_b_id"]
    resp = client.post(f"/api/v1/driver/spontaneous-ride-requests/{rid}/decline", headers=headers)
    assert resp.status_code == 200, f"Ablehnung fehlgeschlagen: {resp.text}"

    resp2 = client.get(f"/api/v1/spontaneous-rides/{rid}/tracking", headers=auth_headers)
    assert resp2.status_code == 200
    data = resp2.json()
    assert data["status"] == "driver_declined"
    assert data["next_request_id"] is None


# -- Tests: Unabhaengige Szenarien ---------------------------------------------

def test_passenger_cancel_does_not_rematch(client: TestClient, auth_headers: dict):
    """Manuelle Stornierung durch Fahrgast loest keinen Rematch aus."""
    from app.db.session import SessionLocal
    from app.models.transport_request import TransportRequest, TransportRequestStatus

    rid = _find_and_book(client, auth_headers)

    resp = client.post(f"/api/v1/spontaneous-rides/{rid}/cancel", headers=auth_headers)
    assert resp.status_code == 200

    db = SessionLocal()
    try:
        tr = db.get(TransportRequest, uuid.UUID(rid))
        assert tr is not None
        assert tr.status == TransportRequestStatus.cancelled

        group_trs = (
            db.query(TransportRequest)
            .filter(TransportRequest.rematch_group_id == tr.rematch_group_id)
            .all()
        )
        assert len(group_trs) == 1, "Stornierung darf keinen Rematch ausloesen"
    finally:
        db.close()

    resp2 = client.get(f"/api/v1/spontaneous-rides/{rid}/tracking", headers=auth_headers)
    assert resp2.status_code == 200
    assert resp2.json()["next_request_id"] is None


def test_timeout_not_yet_expired_returns_409(client: TestClient, auth_headers: dict):
    """Timeout-Endpoint gibt 409, wenn die Anfrage noch nicht abgelaufen ist."""
    rid = _find_and_book(client, auth_headers)

    resp = client.post(f"/api/v1/spontaneous-rides/{rid}/timeout", headers=auth_headers)
    assert resp.status_code == 409

    client.post(f"/api/v1/spontaneous-rides/{rid}/cancel", headers=auth_headers)


def test_timeout_triggers_rematch_when_expired(client: TestClient, auth_headers: dict):
    """Timeout loest Rematch aus, wenn created_at in der Vergangenheit liegt."""
    from app.db.session import SessionLocal
    from app.models.transport_request import TransportRequest, TransportRequestStatus

    rid = _find_and_book(client, auth_headers)
    _state["timeout_expired_id"] = rid

    db = SessionLocal()
    try:
        tr = db.get(TransportRequest, uuid.UUID(rid))
        assert tr is not None
        tr.created_at = datetime.now(timezone.utc) - timedelta(minutes=5)
        db.commit()
    finally:
        db.close()

    resp = client.post(f"/api/v1/spontaneous-rides/{rid}/timeout", headers=auth_headers)
    assert resp.status_code == 200, f"Timeout-Endpoint fehlgeschlagen: {resp.text}"

    db = SessionLocal()
    try:
        tr = db.get(TransportRequest, uuid.UUID(rid))
        assert tr.status == TransportRequestStatus.driver_declined
    finally:
        db.close()


def test_timeout_returns_tracking_with_rematch_fields(client: TestClient, auth_headers: dict):
    """Timeout-Antwort ist SpontaneousRideTracking mit status, next_request_id, request_expires_at."""
    from app.db.session import SessionLocal
    from app.models.transport_request import TransportRequest

    rid = _find_and_book(client, auth_headers)

    db = SessionLocal()
    try:
        tr = db.get(TransportRequest, uuid.UUID(rid))
        tr.created_at = datetime.now(timezone.utc) - timedelta(minutes=5)
        db.commit()
    finally:
        db.close()

    resp = client.post(f"/api/v1/spontaneous-rides/{rid}/timeout", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "driver_declined"
    assert "next_request_id" in data
    assert "request_expires_at" in data


def test_timeout_wrong_passenger_returns_403(client: TestClient, trusted_person_headers: dict):
    """Fremder Nutzer (relative@access.test) kann Timeout nicht melden -> 403 oder 404."""
    rid = _state.get("ride_a_id")
    assert rid, "ride_a_id nicht gesetzt - Kette A fehlgeschlagen"

    resp = client.post(f"/api/v1/spontaneous-rides/{rid}/timeout", headers=trusted_person_headers)
    assert resp.status_code in (403, 404)


def test_timeout_wrong_status_returns_409(client: TestClient, auth_headers: dict):
    """Timeout-Endpoint auf Fahrt mit driver_declined Status -> 409."""
    rid = _state.get("ride_a_id")
    assert rid, "ride_a_id nicht gesetzt - Kette A fehlgeschlagen"

    resp = client.post(f"/api/v1/spontaneous-rides/{rid}/timeout", headers=auth_headers)
    assert resp.status_code == 409
