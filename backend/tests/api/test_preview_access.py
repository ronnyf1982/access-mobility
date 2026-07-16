"""Tests für PreviewAccess-Verwaltung und öffentliches Gate-Login."""
import uuid
import pytest
from fastapi.testclient import TestClient

BASE_ADMIN = "/api/v1/platform-admin/test-access-users"
BASE_PUBLIC = "/api/v1/public/test-access/login"


# ── Hilfsfunktionen ───────────────────────────────────────────────────────────

def _unique_email() -> str:
    return f"gate-{uuid.uuid4().hex[:8]}@testgate.invalid"


def _create_preview_user(
    client: TestClient,
    admin_headers: dict,
    email: str | None = None,
    password: str = "GatePasswort123!",
    **overrides,
) -> dict:
    payload = {
        "email": email or _unique_email(),
        "password": password,
        "first_name": "Gate",
        "last_name": "Tester",
        "is_active": True,
        **overrides,
    }
    resp = client.post(BASE_ADMIN, json=payload, headers=admin_headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


# ── Berechtigungsprüfung ──────────────────────────────────────────────────────

class TestAccessControl:
    def test_unauthenticated_list_401(self, client: TestClient) -> None:
        resp = client.get(BASE_ADMIN)
        assert resp.status_code == 401

    def test_unauthenticated_create_401(self, client: TestClient) -> None:
        resp = client.post(BASE_ADMIN, json={})
        assert resp.status_code == 401

    def test_passenger_list_forbidden(self, client: TestClient, auth_headers: dict) -> None:
        resp = client.get(BASE_ADMIN, headers=auth_headers)
        assert resp.status_code == 403

    def test_passenger_create_forbidden(self, client: TestClient, auth_headers: dict) -> None:
        resp = client.post(
            BASE_ADMIN,
            json={"email": "x@x.test", "password": "pw123456789", "first_name": "X", "last_name": "Y"},
            headers=auth_headers,
        )
        assert resp.status_code == 403

    def test_provider_list_forbidden(self, client: TestClient, provider_headers: dict) -> None:
        resp = client.get(BASE_ADMIN, headers=provider_headers)
        assert resp.status_code == 403

    def test_dispatcher_list_forbidden(self, client: TestClient, dispatcher_headers: dict) -> None:
        resp = client.get(BASE_ADMIN, headers=dispatcher_headers)
        assert resp.status_code == 403

    def test_driver_list_forbidden(self, client: TestClient, driver_headers: dict) -> None:
        resp = client.get(BASE_ADMIN, headers=driver_headers)
        assert resp.status_code == 403

    def test_driver_create_forbidden(self, client: TestClient, driver_headers: dict) -> None:
        resp = client.post(
            BASE_ADMIN,
            json={"email": "x@x.test", "password": "pw123456789", "first_name": "X", "last_name": "Y"},
            headers=driver_headers,
        )
        assert resp.status_code == 403

    def test_passenger_reset_password_forbidden(self, client: TestClient, auth_headers: dict) -> None:
        resp = client.post(
            f"{BASE_ADMIN}/999/reset-password",
            json={"new_password": "NeuesPw123!", "confirm_password": "NeuesPw123!"},
            headers=auth_headers,
        )
        assert resp.status_code == 403

    def test_passenger_activate_forbidden(self, client: TestClient, auth_headers: dict) -> None:
        resp = client.post(f"{BASE_ADMIN}/999/activate", headers=auth_headers)
        assert resp.status_code == 403

    def test_passenger_deactivate_forbidden(self, client: TestClient, auth_headers: dict) -> None:
        resp = client.post(f"{BASE_ADMIN}/999/deactivate", headers=auth_headers)
        assert resp.status_code == 403


# ── Listenansicht ─────────────────────────────────────────────────────────────

class TestListUsers:
    def test_admin_can_list(self, client: TestClient, admin_headers: dict) -> None:
        resp = client.get(BASE_ADMIN, headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_no_password_hash_in_list(self, client: TestClient, admin_headers: dict) -> None:
        _create_preview_user(client, admin_headers)
        resp = client.get(BASE_ADMIN, headers=admin_headers)
        assert resp.status_code == 200
        text = resp.text
        assert "password_hash" not in text
        assert "password" not in text

    def test_search_by_email(self, client: TestClient, admin_headers: dict) -> None:
        email = _unique_email()
        _create_preview_user(client, admin_headers, email=email)
        resp = client.get(f"{BASE_ADMIN}?search={email}", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert any(u["email"] == email for u in data)

    def test_filter_by_active_true(self, client: TestClient, admin_headers: dict) -> None:
        resp = client.get(f"{BASE_ADMIN}?is_active=true", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert all(u["is_active"] is True for u in data)


# ── Benutzer anlegen ──────────────────────────────────────────────────────────

class TestCreateUser:
    def test_admin_can_create(self, client: TestClient, admin_headers: dict) -> None:
        user = _create_preview_user(client, admin_headers)
        assert user["is_active"] is True
        assert "password_hash" not in user
        assert "password" not in user

    def test_email_normalized_to_lowercase(self, client: TestClient, admin_headers: dict) -> None:
        email_upper = f"GATE-{uuid.uuid4().hex[:6]}@TESTGATE.INVALID"
        user = _create_preview_user(client, admin_headers, email=email_upper)
        assert user["email"] == email_upper.lower()

    def test_duplicate_email_409(self, client: TestClient, admin_headers: dict) -> None:
        email = _unique_email()
        _create_preview_user(client, admin_headers, email=email)
        resp = client.post(
            BASE_ADMIN,
            json={"email": email, "password": "GatePasswort123!", "first_name": "X", "last_name": "Y"},
            headers=admin_headers,
        )
        assert resp.status_code == 409

    def test_short_password_rejected(self, client: TestClient, admin_headers: dict) -> None:
        resp = client.post(
            BASE_ADMIN,
            json={"email": _unique_email(), "password": "kurz", "first_name": "X", "last_name": "Y"},
            headers=admin_headers,
        )
        assert resp.status_code == 422

    def test_get_by_id_works(self, client: TestClient, admin_headers: dict) -> None:
        user = _create_preview_user(client, admin_headers)
        resp = client.get(f"{BASE_ADMIN}/{user['id']}", headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == user["id"]
        assert resp.json()["email"] == user["email"]

    def test_get_unknown_id_404(self, client: TestClient, admin_headers: dict) -> None:
        resp = client.get(f"{BASE_ADMIN}/999999", headers=admin_headers)
        assert resp.status_code == 404

    def test_update_name_and_note(self, client: TestClient, admin_headers: dict) -> None:
        user = _create_preview_user(client, admin_headers)
        resp = client.patch(
            f"{BASE_ADMIN}/{user['id']}",
            json={"first_name": "Geändert", "note": "Testnotiz"},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["first_name"] == "Geändert"
        assert data["note"] == "Testnotiz"

    def test_update_unknown_id_404(self, client: TestClient, admin_headers: dict) -> None:
        resp = client.patch(
            f"{BASE_ADMIN}/999999",
            json={"first_name": "X"},
            headers=admin_headers,
        )
        assert resp.status_code == 404


# ── Öffentliches Gate-Login ───────────────────────────────────────────────────

class TestPublicGateLogin:
    def test_valid_login_returns_ok(self, client: TestClient, admin_headers: dict) -> None:
        email = _unique_email()
        _create_preview_user(client, admin_headers, email=email, password="GatePasswort123!")
        resp = client.post(BASE_PUBLIC, json={"email_or_username": email, "password": "GatePasswort123!"})
        assert resp.status_code == 200
        assert resp.json() == {"ok": True}

    def test_valid_login_updates_last_used_at(self, client: TestClient, admin_headers: dict) -> None:
        email = _unique_email()
        user = _create_preview_user(client, admin_headers, email=email, password="GatePasswort123!")
        assert user["last_used_at"] is None
        client.post(BASE_PUBLIC, json={"email_or_username": email, "password": "GatePasswort123!"})
        detail = client.get(f"{BASE_ADMIN}/{user['id']}", headers=admin_headers).json()
        assert detail["last_used_at"] is not None

    def test_wrong_password_401(self, client: TestClient, admin_headers: dict) -> None:
        email = _unique_email()
        _create_preview_user(client, admin_headers, email=email, password="GatePasswort123!")
        resp = client.post(BASE_PUBLIC, json={"email_or_username": email, "password": "FalschesPasswort!"})
        assert resp.status_code == 401

    def test_unknown_email_401(self, client: TestClient) -> None:
        resp = client.post(BASE_PUBLIC, json={"email_or_username": "niemand@niemals.invalid", "password": "IrgendetwasXYZ!"})
        assert resp.status_code == 401

    def test_401_detail_does_not_reveal_existence(self, client: TestClient) -> None:
        resp = client.post(BASE_PUBLIC, json={"email_or_username": "niemand@niemals.invalid", "password": "IrgendetwasXYZ!"})
        assert resp.status_code == 401
        detail = resp.json().get("detail", "")
        assert "exist" not in detail.lower()
        assert "gefunden" not in detail.lower()
        assert "nicht vorhanden" not in detail.lower()

    def test_no_password_hash_in_401(self, client: TestClient) -> None:
        resp = client.post(BASE_PUBLIC, json={"email_or_username": "niemand@niemals.invalid", "password": "IrgendetwasXYZ!"})
        assert "password_hash" not in resp.text
        assert "hash" not in resp.text.lower()


# ── Aktivierung und Deaktivierung ─────────────────────────────────────────────

class TestActivation:
    def test_deactivate_prevents_gate_login(self, client: TestClient, admin_headers: dict) -> None:
        email = _unique_email()
        user = _create_preview_user(client, admin_headers, email=email, password="GatePasswort123!")
        client.post(f"{BASE_ADMIN}/{user['id']}/deactivate", headers=admin_headers)
        resp = client.post(BASE_PUBLIC, json={"email_or_username": email, "password": "GatePasswort123!"})
        assert resp.status_code == 401

    def test_activate_allows_gate_login(self, client: TestClient, admin_headers: dict) -> None:
        email = _unique_email()
        user = _create_preview_user(client, admin_headers, email=email, password="GatePasswort123!")
        client.post(f"{BASE_ADMIN}/{user['id']}/deactivate", headers=admin_headers)
        client.post(f"{BASE_ADMIN}/{user['id']}/activate", headers=admin_headers)
        resp = client.post(BASE_PUBLIC, json={"email_or_username": email, "password": "GatePasswort123!"})
        assert resp.status_code == 200
        assert resp.json()["ok"] is True

    def test_activate_returns_updated_user(self, client: TestClient, admin_headers: dict) -> None:
        user = _create_preview_user(client, admin_headers)
        client.post(f"{BASE_ADMIN}/{user['id']}/deactivate", headers=admin_headers)
        resp = client.post(f"{BASE_ADMIN}/{user['id']}/activate", headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["is_active"] is True

    def test_deactivate_returns_updated_user(self, client: TestClient, admin_headers: dict) -> None:
        user = _create_preview_user(client, admin_headers)
        resp = client.post(f"{BASE_ADMIN}/{user['id']}/deactivate", headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["is_active"] is False

    def test_activate_unknown_id_404(self, client: TestClient, admin_headers: dict) -> None:
        resp = client.post(f"{BASE_ADMIN}/999999/activate", headers=admin_headers)
        assert resp.status_code == 404

    def test_deactivate_unknown_id_404(self, client: TestClient, admin_headers: dict) -> None:
        resp = client.post(f"{BASE_ADMIN}/999999/deactivate", headers=admin_headers)
        assert resp.status_code == 404


# ── Passwort-Reset ────────────────────────────────────────────────────────────

class TestPasswordReset:
    def test_reset_password_returns_ok(self, client: TestClient, admin_headers: dict) -> None:
        user = _create_preview_user(client, admin_headers)
        resp = client.post(
            f"{BASE_ADMIN}/{user['id']}/reset-password",
            json={"new_password": "NeuesGatePw2026!", "confirm_password": "NeuesGatePw2026!"},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert resp.json().get("ok") is True

    def test_old_password_fails_after_reset(self, client: TestClient, admin_headers: dict) -> None:
        email = _unique_email()
        user = _create_preview_user(client, admin_headers, email=email, password="GatePasswort123!")
        client.post(
            f"{BASE_ADMIN}/{user['id']}/reset-password",
            json={"new_password": "NeuesGatePw2026!", "confirm_password": "NeuesGatePw2026!"},
            headers=admin_headers,
        )
        resp = client.post(BASE_PUBLIC, json={"email_or_username": email, "password": "GatePasswort123!"})
        assert resp.status_code == 401

    def test_new_password_works_after_reset(self, client: TestClient, admin_headers: dict) -> None:
        email = _unique_email()
        user = _create_preview_user(client, admin_headers, email=email, password="GatePasswort123!")
        client.post(
            f"{BASE_ADMIN}/{user['id']}/reset-password",
            json={"new_password": "NeuesGatePw2026!", "confirm_password": "NeuesGatePw2026!"},
            headers=admin_headers,
        )
        resp = client.post(BASE_PUBLIC, json={"email_or_username": email, "password": "NeuesGatePw2026!"})
        assert resp.status_code == 200

    def test_password_mismatch_400(self, client: TestClient, admin_headers: dict) -> None:
        user = _create_preview_user(client, admin_headers)
        resp = client.post(
            f"{BASE_ADMIN}/{user['id']}/reset-password",
            json={"new_password": "NeuesGatePw2026!", "confirm_password": "AnderesPw2026!!"},
            headers=admin_headers,
        )
        assert resp.status_code == 400

    def test_short_new_password_422(self, client: TestClient, admin_headers: dict) -> None:
        user = _create_preview_user(client, admin_headers)
        resp = client.post(
            f"{BASE_ADMIN}/{user['id']}/reset-password",
            json={"new_password": "kurz", "confirm_password": "kurz"},
            headers=admin_headers,
        )
        assert resp.status_code == 422

    def test_reset_no_hash_in_response(self, client: TestClient, admin_headers: dict) -> None:
        user = _create_preview_user(client, admin_headers)
        resp = client.post(
            f"{BASE_ADMIN}/{user['id']}/reset-password",
            json={"new_password": "NeuesGatePw2026!", "confirm_password": "NeuesGatePw2026!"},
            headers=admin_headers,
        )
        assert "hash" not in resp.text.lower()
        assert "password" not in resp.text.lower()

    def test_reset_unknown_id_404(self, client: TestClient, admin_headers: dict) -> None:
        resp = client.post(
            f"{BASE_ADMIN}/999999/reset-password",
            json={"new_password": "NeuesGatePw2026!", "confirm_password": "NeuesGatePw2026!"},
            headers=admin_headers,
        )
        assert resp.status_code == 404


# ── Regressionstests ──────────────────────────────────────────────────────────

class TestRegression:
    def test_existing_app_login_still_works(self, client: TestClient) -> None:
        resp = client.post("/api/v1/auth/login", json={"email": "admin@access.test", "password": "Access123!"})
        assert resp.status_code == 200
        assert resp.json()["user"]["role"] == "platform_admin"

    def test_passenger_app_login_still_works(self, client: TestClient) -> None:
        resp = client.post("/api/v1/auth/login", json={"email": "passenger@access.test", "password": "Access123!"})
        assert resp.status_code == 200

    def test_platform_admin_users_endpoint_still_works(self, client: TestClient, admin_headers: dict) -> None:
        resp = client.get("/api/v1/platform-admin/users", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_public_gate_and_app_login_are_separate_tables(
        self, client: TestClient, admin_headers: dict
    ) -> None:
        """Gate-Benutzer dürfen sich nicht per App-Login einloggen."""
        email = _unique_email()
        _create_preview_user(client, admin_headers, email=email, password="GatePasswort123!")
        # App-Login muss scheitern (PreviewAccessUser ist kein app User)
        resp = client.post("/api/v1/auth/login", json={"email": email, "password": "GatePasswort123!"})
        assert resp.status_code == 401
