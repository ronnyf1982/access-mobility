"""Tests für Platform-Admin-Benutzerverwaltung (Sprint FAHRANDO-COMING-SOON-TESTZUGANG-PLATTFORMADMIN-1)."""
import os
import sys
import uuid

import pytest
from fastapi.testclient import TestClient

BASE = "/api/v1/platform-admin"


# ── Hilfsfunktionen ──────────────────────────────────────────────────────────

def _unique_email() -> str:
    return f"test-{uuid.uuid4().hex[:8]}@testdomain.invalid"


def _create_user(client: TestClient, admin_headers: dict, **overrides) -> dict:
    payload = {
        "email": _unique_email(),
        "password": "TestPasswort123!",
        "first_name": "Test",
        "last_name": "Nutzer",
        "role": "passenger",
        **overrides,
    }
    resp = client.post(f"{BASE}/users", json=payload, headers=admin_headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


# ── Bootstrap-Script ─────────────────────────────────────────────────────────

class TestBootstrapScript:
    def test_aborts_without_email(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("FAHRANDO_BOOTSTRAP_ADMIN_EMAIL", raising=False)
        monkeypatch.setenv("FAHRANDO_BOOTSTRAP_ADMIN_PASSWORD", "x")
        monkeypatch.setenv("FAHRANDO_BOOTSTRAP_ADMIN_FIRST_NAME", "X")
        monkeypatch.setenv("FAHRANDO_BOOTSTRAP_ADMIN_LAST_NAME", "Y")
        from app.scripts.ensure_platform_admin import run
        with pytest.raises(SystemExit):
            run()

    def test_aborts_without_password(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("FAHRANDO_BOOTSTRAP_ADMIN_EMAIL", "x@x.test")
        monkeypatch.delenv("FAHRANDO_BOOTSTRAP_ADMIN_PASSWORD", raising=False)
        monkeypatch.setenv("FAHRANDO_BOOTSTRAP_ADMIN_FIRST_NAME", "X")
        monkeypatch.setenv("FAHRANDO_BOOTSTRAP_ADMIN_LAST_NAME", "Y")
        from app.scripts.ensure_platform_admin import run
        with pytest.raises(SystemExit):
            run()

    def test_aborts_without_first_name(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("FAHRANDO_BOOTSTRAP_ADMIN_EMAIL", "x@x.test")
        monkeypatch.setenv("FAHRANDO_BOOTSTRAP_ADMIN_PASSWORD", "x")
        monkeypatch.delenv("FAHRANDO_BOOTSTRAP_ADMIN_FIRST_NAME", raising=False)
        monkeypatch.setenv("FAHRANDO_BOOTSTRAP_ADMIN_LAST_NAME", "Y")
        from app.scripts.ensure_platform_admin import run
        with pytest.raises(SystemExit):
            run()

    def test_creates_platform_admin(self, monkeypatch: pytest.MonkeyPatch, client: TestClient) -> None:
        email = f"bootstrap-{uuid.uuid4().hex[:8]}@bootstrap.test"
        monkeypatch.setenv("FAHRANDO_BOOTSTRAP_ADMIN_EMAIL", email)
        monkeypatch.setenv("FAHRANDO_BOOTSTRAP_ADMIN_PASSWORD", "BootstrapPasswort2026!")
        monkeypatch.setenv("FAHRANDO_BOOTSTRAP_ADMIN_FIRST_NAME", "Boot")
        monkeypatch.setenv("FAHRANDO_BOOTSTRAP_ADMIN_LAST_NAME", "Strap")
        from app.scripts import ensure_platform_admin
        import importlib
        importlib.reload(ensure_platform_admin)
        ensure_platform_admin.run()

        # Verify via API login
        resp = client.post("/api/v1/auth/login", json={"email": email, "password": "BootstrapPasswort2026!"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["user"]["role"] == "platform_admin"
        assert data["user"]["is_active"] is True

    def test_idempotent_no_duplicate(self, monkeypatch: pytest.MonkeyPatch) -> None:
        email = f"idempotent-{uuid.uuid4().hex[:8]}@bootstrap.test"
        monkeypatch.setenv("FAHRANDO_BOOTSTRAP_ADMIN_EMAIL", email)
        monkeypatch.setenv("FAHRANDO_BOOTSTRAP_ADMIN_PASSWORD", "IdempotentPasswort2026!")
        monkeypatch.setenv("FAHRANDO_BOOTSTRAP_ADMIN_FIRST_NAME", "Idem")
        monkeypatch.setenv("FAHRANDO_BOOTSTRAP_ADMIN_LAST_NAME", "Potent")
        from app.scripts import ensure_platform_admin
        import importlib
        importlib.reload(ensure_platform_admin)
        ensure_platform_admin.run()
        ensure_platform_admin.run()  # zweiter Lauf darf kein Duplikat erzeugen

    def test_password_not_in_output(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture) -> None:
        email = f"pwtest-{uuid.uuid4().hex[:8]}@bootstrap.test"
        secret = "GeheimesPasswort9876!"
        monkeypatch.setenv("FAHRANDO_BOOTSTRAP_ADMIN_EMAIL", email)
        monkeypatch.setenv("FAHRANDO_BOOTSTRAP_ADMIN_PASSWORD", secret)
        monkeypatch.setenv("FAHRANDO_BOOTSTRAP_ADMIN_FIRST_NAME", "Pw")
        monkeypatch.setenv("FAHRANDO_BOOTSTRAP_ADMIN_LAST_NAME", "Test")
        from app.scripts import ensure_platform_admin
        import importlib
        importlib.reload(ensure_platform_admin)
        ensure_platform_admin.run()
        captured = capsys.readouterr()
        assert secret not in captured.out
        assert secret not in captured.err


# ── Berechtigungs-Matrix ─────────────────────────────────────────────────────

NON_ADMIN_ROLES = ["passenger", "provider", "dispatcher", "driver"]


@pytest.mark.parametrize("token_fixture", NON_ADMIN_ROLES)
class TestAccessControl:
    def test_list_forbidden(self, request: pytest.FixtureRequest, token_fixture: str, client: TestClient) -> None:
        token = request.getfixturevalue(f"{token_fixture}_token")
        resp = client.get(f"{BASE}/users", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403

    def test_create_forbidden(self, request: pytest.FixtureRequest, token_fixture: str, client: TestClient) -> None:
        token = request.getfixturevalue(f"{token_fixture}_token")
        resp = client.post(
            f"{BASE}/users",
            json={"email": "x@x.test", "password": "pw", "first_name": "X", "last_name": "Y", "role": "passenger"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403

    def test_patch_forbidden(self, request: pytest.FixtureRequest, token_fixture: str, client: TestClient) -> None:
        token = request.getfixturevalue(f"{token_fixture}_token")
        resp = client.patch(
            f"{BASE}/users/{uuid.uuid4()}",
            json={"first_name": "X"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403

    def test_reset_password_forbidden(self, request: pytest.FixtureRequest, token_fixture: str, client: TestClient) -> None:
        token = request.getfixturevalue(f"{token_fixture}_token")
        resp = client.post(
            f"{BASE}/users/{uuid.uuid4()}/reset-password",
            json={"new_password": "abc", "confirm_password": "abc"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403

    def test_deactivate_forbidden(self, request: pytest.FixtureRequest, token_fixture: str, client: TestClient) -> None:
        token = request.getfixturevalue(f"{token_fixture}_token")
        resp = client.post(
            f"{BASE}/users/{uuid.uuid4()}/deactivate",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403


class TestUnauthenticated:
    def test_list_401(self, client: TestClient) -> None:
        resp = client.get(f"{BASE}/users")
        assert resp.status_code == 401

    def test_create_401(self, client: TestClient) -> None:
        resp = client.post(f"{BASE}/users", json={})
        assert resp.status_code == 401


# ── Benutzerliste ────────────────────────────────────────────────────────────

class TestListUsers:
    def test_admin_can_list(self, client: TestClient, admin_headers: dict) -> None:
        resp = client.get(f"{BASE}/users", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_no_password_in_response(self, client: TestClient, admin_headers: dict) -> None:
        resp = client.get(f"{BASE}/users", headers=admin_headers)
        text = resp.text
        assert "password" not in text.lower() or "password_hash" not in text

    def test_search_by_email(self, client: TestClient, admin_headers: dict) -> None:
        resp = client.get(f"{BASE}/users?search=passenger%40access.test", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert any("passenger" in u["email"] for u in data)

    def test_filter_by_role(self, client: TestClient, admin_headers: dict) -> None:
        resp = client.get(f"{BASE}/users?role=passenger", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert all(u["role"] == "passenger" for u in data)

    def test_filter_by_active(self, client: TestClient, admin_headers: dict) -> None:
        resp = client.get(f"{BASE}/users?is_active=true", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert all(u["is_active"] is True for u in data)


# ── Benutzer anlegen ─────────────────────────────────────────────────────────

class TestCreateUser:
    def test_admin_can_create(self, client: TestClient, admin_headers: dict) -> None:
        user = _create_user(client, admin_headers)
        assert user["role"] == "passenger"
        assert user["is_active"] is True
        assert "password" not in user
        assert "password_hash" not in user

    def test_duplicate_email_409(self, client: TestClient, admin_headers: dict) -> None:
        email = _unique_email()
        _create_user(client, admin_headers, email=email)
        resp = client.post(
            f"{BASE}/users",
            json={"email": email, "password": "TestPasswort123!", "first_name": "X", "last_name": "Y", "role": "passenger"},
            headers=admin_headers,
        )
        assert resp.status_code == 409

    def test_password_too_short_rejected(self, client: TestClient, admin_headers: dict) -> None:
        resp = client.post(
            f"{BASE}/users",
            json={"email": _unique_email(), "password": "kurz", "first_name": "X", "last_name": "Y", "role": "passenger"},
            headers=admin_headers,
        )
        assert resp.status_code == 422

    def test_invalid_role_rejected(self, client: TestClient, admin_headers: dict) -> None:
        resp = client.post(
            f"{BASE}/users",
            json={"email": _unique_email(), "password": "TestPasswort123!", "first_name": "X", "last_name": "Y", "role": "superadmin"},
            headers=admin_headers,
        )
        assert resp.status_code == 422

    def test_created_user_can_login(self, client: TestClient, admin_headers: dict) -> None:
        email = _unique_email()
        _create_user(client, admin_headers, email=email, role="passenger")
        resp = client.post("/api/v1/auth/login", json={"email": email, "password": "TestPasswort123!"})
        assert resp.status_code == 200

    def test_password_not_in_response(self, client: TestClient, admin_headers: dict) -> None:
        resp = client.post(
            f"{BASE}/users",
            json={"email": _unique_email(), "password": "TestPasswort123!", "first_name": "X", "last_name": "Y", "role": "passenger"},
            headers=admin_headers,
        )
        assert resp.status_code == 201
        assert "password" not in resp.json()
        assert "password_hash" not in resp.json()


# ── Benutzer bearbeiten ──────────────────────────────────────────────────────

class TestUpdateUser:
    def test_admin_can_update_name(self, client: TestClient, admin_headers: dict) -> None:
        user = _create_user(client, admin_headers)
        resp = client.patch(
            f"{BASE}/users/{user['id']}",
            json={"first_name": "Geändert"},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["first_name"] == "Geändert"

    def test_cannot_remove_own_platform_admin_role(self, client: TestClient, admin_headers: dict, admin_token: str) -> None:
        me = client.get("/api/v1/auth/me", headers=admin_headers).json()
        resp = client.patch(
            f"{BASE}/users/{me['id']}",
            json={"role": "dispatcher"},
            headers=admin_headers,
        )
        assert resp.status_code == 400

    def test_cannot_deactivate_self(self, client: TestClient, admin_headers: dict) -> None:
        me = client.get("/api/v1/auth/me", headers=admin_headers).json()
        resp = client.patch(
            f"{BASE}/users/{me['id']}",
            json={"is_active": False},
            headers=admin_headers,
        )
        assert resp.status_code == 400

    def test_not_found_404(self, client: TestClient, admin_headers: dict) -> None:
        resp = client.patch(
            f"{BASE}/users/{uuid.uuid4()}",
            json={"first_name": "X"},
            headers=admin_headers,
        )
        assert resp.status_code == 404


# ── Aktivierung / Deaktivierung ──────────────────────────────────────────────

class TestActivation:
    def test_deactivate_prevents_login(self, client: TestClient, admin_headers: dict) -> None:
        email = _unique_email()
        user = _create_user(client, admin_headers, email=email)
        client.post(f"{BASE}/users/{user['id']}/deactivate", headers=admin_headers)

        resp = client.post("/api/v1/auth/login", json={"email": email, "password": "TestPasswort123!"})
        assert resp.status_code == 403

    def test_reactivate_allows_login(self, client: TestClient, admin_headers: dict) -> None:
        email = _unique_email()
        user = _create_user(client, admin_headers, email=email)
        client.post(f"{BASE}/users/{user['id']}/deactivate", headers=admin_headers)
        client.post(f"{BASE}/users/{user['id']}/activate", headers=admin_headers)

        resp = client.post("/api/v1/auth/login", json={"email": email, "password": "TestPasswort123!"})
        assert resp.status_code == 200

    def test_cannot_deactivate_self_via_endpoint(self, client: TestClient, admin_headers: dict) -> None:
        me = client.get("/api/v1/auth/me", headers=admin_headers).json()
        resp = client.post(f"{BASE}/users/{me['id']}/deactivate", headers=admin_headers)
        assert resp.status_code == 400

    def test_deactivated_user_blocked_by_api(self, client: TestClient, admin_headers: dict) -> None:
        email = _unique_email()
        user = _create_user(client, admin_headers, email=email)
        # login and get token
        login_resp = client.post("/api/v1/auth/login", json={"email": email, "password": "TestPasswort123!"})
        token = login_resp.json()["access_token"]
        # deactivate
        client.post(f"{BASE}/users/{user['id']}/deactivate", headers=admin_headers)
        # existing token must be blocked on next API call
        me_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me_resp.status_code == 401


# ── Passwort-Reset ───────────────────────────────────────────────────────────

class TestPasswordReset:
    def test_admin_can_reset_password(self, client: TestClient, admin_headers: dict) -> None:
        email = _unique_email()
        user = _create_user(client, admin_headers, email=email)
        resp = client.post(
            f"{BASE}/users/{user['id']}/reset-password",
            json={"new_password": "NeuesPasswort2026!", "confirm_password": "NeuesPasswort2026!"},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["message"]

    def test_old_password_fails_after_reset(self, client: TestClient, admin_headers: dict) -> None:
        email = _unique_email()
        user = _create_user(client, admin_headers, email=email)
        client.post(
            f"{BASE}/users/{user['id']}/reset-password",
            json={"new_password": "NeuesPasswort2026!", "confirm_password": "NeuesPasswort2026!"},
            headers=admin_headers,
        )
        resp = client.post("/api/v1/auth/login", json={"email": email, "password": "TestPasswort123!"})
        assert resp.status_code == 401

    def test_new_password_works_after_reset(self, client: TestClient, admin_headers: dict) -> None:
        email = _unique_email()
        user = _create_user(client, admin_headers, email=email)
        client.post(
            f"{BASE}/users/{user['id']}/reset-password",
            json={"new_password": "NeuesPasswort2026!", "confirm_password": "NeuesPasswort2026!"},
            headers=admin_headers,
        )
        resp = client.post("/api/v1/auth/login", json={"email": email, "password": "NeuesPasswort2026!"})
        assert resp.status_code == 200

    def test_mismatched_passwords_rejected(self, client: TestClient, admin_headers: dict) -> None:
        user = _create_user(client, admin_headers)
        resp = client.post(
            f"{BASE}/users/{user['id']}/reset-password",
            json={"new_password": "NeuesPasswort2026!", "confirm_password": "AnderesPw2026!"},
            headers=admin_headers,
        )
        assert resp.status_code == 400

    def test_password_not_in_reset_response(self, client: TestClient, admin_headers: dict) -> None:
        user = _create_user(client, admin_headers)
        resp = client.post(
            f"{BASE}/users/{user['id']}/reset-password",
            json={"new_password": "NeuesPasswort2026!", "confirm_password": "NeuesPasswort2026!"},
            headers=admin_headers,
        )
        assert "password" not in resp.json() or resp.json().get("password") is None
        assert "hash" not in resp.text.lower()


# ── Bestehende Tests dürfen nicht brechen ───────────────────────────────────

class TestRegressionAuth:
    def test_existing_demo_admin_still_works(self, client: TestClient) -> None:
        resp = client.post("/api/v1/auth/login", json={"email": "admin@access.test", "password": "Access123!"})
        assert resp.status_code == 200
        assert resp.json()["user"]["role"] == "platform_admin"

    def test_passenger_login_still_works(self, client: TestClient) -> None:
        resp = client.post("/api/v1/auth/login", json={"email": "passenger@access.test", "password": "Access123!"})
        assert resp.status_code == 200
