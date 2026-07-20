"""Sprint 12A: Live-Status für Fahrgast und Vertrauensperson."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.transport_request import TransportRequest, TransportRequestStatus
from app.models.trusted_relationship import TrustedRelationship, TrustStatus
from app.models.user import User, UserRole


def _get_passenger_assigned_request(db: Session) -> TransportRequest | None:
    passenger = db.query(User).filter(User.email == "passenger@access.test").first()
    if not passenger:
        return None
    return (
        db.query(TransportRequest)
        .filter(
            TransportRequest.passenger_user_id == passenger.id,
            TransportRequest.status == TransportRequestStatus.assigned,
        )
        .first()
    )


def _get_passenger_any_request(db: Session) -> TransportRequest | None:
    passenger = db.query(User).filter(User.email == "passenger@access.test").first()
    if not passenger:
        return None
    return (
        db.query(TransportRequest)
        .filter(TransportRequest.passenger_user_id == passenger.id)
        .first()
    )


def _get_other_passenger_request(db: Session) -> TransportRequest | None:
    """Gibt eine Fahrt zurück, die NICHT passenger@access.test gehört."""
    passenger = db.query(User).filter(User.email == "passenger@access.test").first()
    if not passenger:
        return None
    return (
        db.query(TransportRequest)
        .filter(TransportRequest.passenger_user_id != passenger.id)
        .first()
    )


class TestPassengerLiveStatus:
    def test_passenger_reads_own_status_history(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        db = SessionLocal()
        try:
            req = _get_passenger_any_request(db)
            if not req:
                pytest.skip("Keine Fahrt für passenger@access.test")
            request_id = str(req.id)
        finally:
            db.close()

        resp = client.get(
            f"/api/v1/transport-requests/{request_id}/status-events",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_empty_status_history_returns_list(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        """Leere Statushistorie liefert [] — kein Crash."""
        db = SessionLocal()
        try:
            passenger = db.query(User).filter(User.email == "passenger@access.test").first()
            # Suche Fahrt ohne Status-Events (draft/requested reichen)
            req = (
                db.query(TransportRequest)
                .filter(
                    TransportRequest.passenger_user_id == passenger.id,
                    TransportRequest.status == TransportRequestStatus.requested,
                )
                .first()
            )
            if not req:
                pytest.skip("Keine Fahrt mit Status 'requested' für passenger@access.test")
            request_id = str(req.id)
        finally:
            db.close()

        resp = client.get(
            f"/api/v1/transport-requests/{request_id}/status-events",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json() == []


class TestTrustedPersonLiveStatus:
    def test_trusted_person_can_read_linked_passenger_ride_status(
        self, client: TestClient, trusted_person_headers: dict
    ) -> None:
        db = SessionLocal()
        try:
            req = _get_passenger_assigned_request(db)
            if not req:
                pytest.skip("Keine zugewiesene Fahrt für passenger@access.test (Seed ausführen)")
            request_id = str(req.id)

            # Sicherstellen, dass die TrustedRelationship aktiv ist
            passenger = db.query(User).filter(User.email == "passenger@access.test").first()
            relative = db.query(User).filter(User.email == "relative@access.test").first()
            if not passenger or not relative:
                pytest.skip("Demo-Nutzer fehlen")
            rel = (
                db.query(TrustedRelationship)
                .filter(
                    TrustedRelationship.passenger_user_id == passenger.id,
                    TrustedRelationship.trusted_user_id == relative.id,
                    TrustedRelationship.status == TrustStatus.active,
                )
                .first()
            )
            if not rel:
                pytest.skip("Keine aktive TrustedRelationship (Seed ausführen)")
        finally:
            db.close()

        resp = client.get(
            f"/api/v1/transport-requests/{request_id}/status-events",
            headers=trusted_person_headers,
        )
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_trusted_person_cannot_read_unlinked_ride(
        self, client: TestClient, trusted_person_headers: dict
    ) -> None:
        db = SessionLocal()
        try:
            req = _get_other_passenger_request(db)
            if not req:
                pytest.skip("Keine Fahrt eines anderen Fahrgasts")
            request_id = str(req.id)
        finally:
            db.close()

        resp = client.get(
            f"/api/v1/transport-requests/{request_id}/status-events",
            headers=trusted_person_headers,
        )
        assert resp.status_code == 403

    def test_trusted_person_cannot_create_status_event(
        self, client: TestClient, trusted_person_headers: dict
    ) -> None:
        db = SessionLocal()
        try:
            req = _get_passenger_assigned_request(db)
            if not req:
                pytest.skip("Keine zugewiesene Fahrt")
            request_id = str(req.id)
        finally:
            db.close()

        resp = client.post(
            f"/api/v1/driver/transport-requests/{request_id}/status-events",
            json={"status": "driver_on_way"},
            headers=trusted_person_headers,
        )
        assert resp.status_code == 403


class TestNotificationDispatchPlaceholder:
    def test_collect_targets_returns_list(self) -> None:
        from app.services.notification_dispatch import collect_notification_targets_for_status_event
        from app.models.notification_preference import NotificationEventType

        db = SessionLocal()
        try:
            passenger = db.query(User).filter(User.email == "passenger@access.test").first()
            req = _get_passenger_assigned_request(db)
            if not passenger or not req:
                pytest.skip("Seed-Daten fehlen")

            targets = collect_notification_targets_for_status_event(
                db, req.id, NotificationEventType.driver_on_way
            )
        finally:
            db.close()

        assert isinstance(targets, list)

    def test_collect_targets_unknown_request_returns_empty(self) -> None:
        import uuid as _uuid
        from app.services.notification_dispatch import collect_notification_targets_for_status_event
        from app.models.notification_preference import NotificationEventType

        db = SessionLocal()
        try:
            result = collect_notification_targets_for_status_event(
                db, _uuid.uuid4(), NotificationEventType.ride_completed
            )
        finally:
            db.close()

        assert result == []
