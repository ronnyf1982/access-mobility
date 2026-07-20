"""Sprint 11: RideStatusEvent API tests."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.driver_profile import DriverProfile
from app.models.transport_request import TransportRequest, TransportRequestStatus
from app.models.user import User
from app.models.vehicle import Vehicle


def _get_assigned_request(db: Session) -> TransportRequest | None:
    return (
        db.query(TransportRequest)
        .filter(TransportRequest.status == TransportRequestStatus.assigned)
        .first()
    )


class TestRideStatusEventCreation:
    def test_driver_can_create_status_event(self, client: TestClient, driver_headers: dict) -> None:
        db = SessionLocal()
        try:
            req = _get_assigned_request(db)
            if not req:
                pytest.skip("Keine zugewiesene Fahrt im Test-DB (Seed ausführen)")
            request_id = str(req.id)
        finally:
            db.close()

        resp = client.post(
            f"/api/v1/driver/transport-requests/{request_id}/status-events",
            json={"status": "driver_on_way"},
            headers=driver_headers,
        )
        assert resp.status_code == 201, resp.text
        data = resp.json()
        assert data["status"] == "driver_on_way"
        assert data["transport_request_id"] == request_id

    def test_driver_can_create_issue_event_with_note(self, client: TestClient, driver_headers: dict) -> None:
        db = SessionLocal()
        try:
            req = _get_assigned_request(db)
            if not req:
                pytest.skip("Keine zugewiesene Fahrt im Test-DB")
            request_id = str(req.id)
        finally:
            db.close()

        resp = client.post(
            f"/api/v1/driver/transport-requests/{request_id}/status-events",
            json={"status": "issue_reported", "note": "Fahrzeugpanne"},
            headers=driver_headers,
        )
        assert resp.status_code == 201, resp.text
        data = resp.json()
        assert data["status"] == "issue_reported"
        assert data["note"] == "Fahrzeugpanne"

    def test_invalid_status_rejected(self, client: TestClient, driver_headers: dict) -> None:
        db = SessionLocal()
        try:
            req = _get_assigned_request(db)
            if not req:
                pytest.skip("Keine zugewiesene Fahrt")
            request_id = str(req.id)
        finally:
            db.close()

        resp = client.post(
            f"/api/v1/driver/transport-requests/{request_id}/status-events",
            json={"status": "ungueltig"},
            headers=driver_headers,
        )
        assert resp.status_code == 422

    def test_passenger_cannot_create_status_event(self, client: TestClient, auth_headers: dict) -> None:
        db = SessionLocal()
        try:
            req = _get_assigned_request(db)
            if not req:
                pytest.skip("Keine zugewiesene Fahrt")
            request_id = str(req.id)
        finally:
            db.close()

        resp = client.post(
            f"/api/v1/driver/transport-requests/{request_id}/status-events",
            json={"status": "driver_on_way"},
            headers=auth_headers,
        )
        assert resp.status_code == 403


class TestRideStatusEventListing:
    def test_dispatcher_can_read_status_history(self, client: TestClient, dispatcher_headers: dict) -> None:
        db = SessionLocal()
        try:
            req = _get_assigned_request(db)
            if not req:
                pytest.skip("Keine zugewiesene Fahrt")
            request_id = str(req.id)
        finally:
            db.close()

        resp = client.get(
            f"/api/v1/transport-requests/{request_id}/status-events",
            headers=dispatcher_headers,
        )
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_passenger_can_read_own_ride_status(self, client: TestClient, auth_headers: dict) -> None:
        db = SessionLocal()
        try:
            passenger = db.query(User).filter(User.email == "passenger@access.test").first()
            req = (
                db.query(TransportRequest)
                .filter(
                    TransportRequest.passenger_user_id == passenger.id,
                    TransportRequest.status == TransportRequestStatus.assigned,
                )
                .first()
            )
            if not req:
                pytest.skip("Keine zugewiesene Fahrt für passenger@access.test")
            request_id = str(req.id)
        finally:
            db.close()

        resp = client.get(
            f"/api/v1/transport-requests/{request_id}/status-events",
            headers=auth_headers,
        )
        assert resp.status_code == 200

    def test_driver_cannot_read_unassigned_ride(self, client: TestClient, driver_headers: dict) -> None:
        db = SessionLocal()
        try:
            driver_user = db.query(User).filter(User.email == "driver@access.test").first()
            driver_profile = db.query(DriverProfile).filter(DriverProfile.user_id == driver_user.id).first()
            unassigned = (
                db.query(TransportRequest)
                .filter(
                    TransportRequest.status == TransportRequestStatus.requested,
                )
                .first()
            )
            if not unassigned:
                pytest.skip("Keine unzugewiesene Fahrt")
            request_id = str(unassigned.id)
        finally:
            db.close()

        resp = client.get(
            f"/api/v1/transport-requests/{request_id}/status-events",
            headers=driver_headers,
        )
        assert resp.status_code == 403
