"""Sprint 11: PassengerNotificationPreference API tests."""
from fastapi.testclient import TestClient


ALL_EVENT_TYPES = [
    "driver_on_way",
    "driver_arrived",
    "passenger_picked_up",
    "ride_started",
    "ride_completed",
    "ride_cancelled",
    "issue_reported",
]


class TestNotificationPreferences:
    def test_passenger_can_read_preferences(self, client: TestClient, auth_headers: dict) -> None:
        resp = client.get("/api/v1/passenger/notification-preferences", headers=auth_headers)
        assert resp.status_code == 200
        prefs = resp.json()
        assert isinstance(prefs, list)

    def test_passenger_can_save_preferences(self, client: TestClient, auth_headers: dict) -> None:
        payload = [
            {
                "event_type": evt,
                "notify_trusted_persons": True,
                "channel_in_app": True,
                "channel_email": False,
                "channel_sms": False,
            }
            for evt in ALL_EVENT_TYPES
        ]
        resp = client.put("/api/v1/passenger/notification-preferences", json=payload, headers=auth_headers)
        assert resp.status_code == 200
        saved = resp.json()
        assert len(saved) == len(ALL_EVENT_TYPES)
        event_types_returned = {p["event_type"] for p in saved}
        assert event_types_returned == set(ALL_EVENT_TYPES)

    def test_save_is_idempotent(self, client: TestClient, auth_headers: dict) -> None:
        payload = [
            {
                "event_type": "ride_completed",
                "notify_trusted_persons": True,
                "channel_in_app": False,
                "channel_email": True,
                "channel_sms": False,
            }
        ]
        resp1 = client.put("/api/v1/passenger/notification-preferences", json=payload, headers=auth_headers)
        resp2 = client.put("/api/v1/passenger/notification-preferences", json=payload, headers=auth_headers)
        assert resp1.status_code == 200
        assert resp2.status_code == 200
        # Beide Antworten identisch
        r1 = {p["event_type"]: p for p in resp1.json()}
        r2 = {p["event_type"]: p for p in resp2.json()}
        assert r1["ride_completed"]["channel_email"] is True
        assert r2["ride_completed"]["channel_email"] is True

    def test_driver_cannot_access_passenger_preferences(self, client: TestClient, driver_headers: dict) -> None:
        resp = client.get("/api/v1/passenger/notification-preferences", headers=driver_headers)
        assert resp.status_code == 403

    def test_dispatcher_cannot_access_passenger_preferences(self, client: TestClient, dispatcher_headers: dict) -> None:
        resp = client.get("/api/v1/passenger/notification-preferences", headers=dispatcher_headers)
        assert resp.status_code == 403
