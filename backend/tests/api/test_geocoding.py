"""Geocoding endpoint tests (Hotfix 12D-D).

All tests mock the external Nominatim HTTP call so no real network request
is made. The external service is never a test dependency.
"""
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


def _make_nominatim_response(address: dict) -> MagicMock:
    mock = MagicMock()
    mock.json.return_value = {"address": address}
    mock.raise_for_status = MagicMock()
    return mock


def _patch_nominatim(address: dict):
    mock_resp = _make_nominatim_response(address)
    patcher = patch("app.services.reverse_geocoding.httpx.Client")
    mock_client_cls = patcher.start()
    mock_client_cls.return_value.__enter__.return_value.get.return_value = mock_resp
    return patcher


class TestReverseGeocodeAuth:
    def test_unauthenticated_returns_401(self, client: TestClient):
        resp = client.get("/api/v1/geocoding/reverse?latitude=52.5&longitude=13.4")
        assert resp.status_code == 401

    def test_passenger_can_access(self, client: TestClient, auth_headers: dict):
        patcher = _patch_nominatim({"road": "Teststraße", "house_number": "1", "postcode": "10115", "city": "Berlin"})
        try:
            resp = client.get("/api/v1/geocoding/reverse?latitude=52.5&longitude=13.4", headers=auth_headers)
            assert resp.status_code == 200
        finally:
            patcher.stop()

    def test_driver_can_access(self, client: TestClient, driver_headers: dict):
        patcher = _patch_nominatim({"road": "Teststraße", "postcode": "10115", "city": "Berlin"})
        try:
            resp = client.get("/api/v1/geocoding/reverse?latitude=52.5&longitude=13.4", headers=driver_headers)
            assert resp.status_code == 200
        finally:
            patcher.stop()


class TestReverseGeocodeValidation:
    def test_latitude_too_high(self, client: TestClient, auth_headers: dict):
        resp = client.get("/api/v1/geocoding/reverse?latitude=91.0&longitude=13.4", headers=auth_headers)
        assert resp.status_code == 422

    def test_latitude_too_low(self, client: TestClient, auth_headers: dict):
        resp = client.get("/api/v1/geocoding/reverse?latitude=-91.0&longitude=13.4", headers=auth_headers)
        assert resp.status_code == 422

    def test_longitude_too_high(self, client: TestClient, auth_headers: dict):
        resp = client.get("/api/v1/geocoding/reverse?latitude=52.5&longitude=181.0", headers=auth_headers)
        assert resp.status_code == 422

    def test_longitude_too_low(self, client: TestClient, auth_headers: dict):
        resp = client.get("/api/v1/geocoding/reverse?latitude=52.5&longitude=-181.0", headers=auth_headers)
        assert resp.status_code == 422

    def test_missing_params_returns_422(self, client: TestClient, auth_headers: dict):
        resp = client.get("/api/v1/geocoding/reverse?latitude=52.5", headers=auth_headers)
        assert resp.status_code == 422


class TestReverseGeocodeResults:
    def test_full_address_returned(self, client: TestClient, auth_headers: dict):
        patcher = _patch_nominatim({
            "road": "Musterstraße",
            "house_number": "5",
            "postcode": "12345",
            "city": "Berlin",
        })
        try:
            resp = client.get("/api/v1/geocoding/reverse?latitude=52.5&longitude=13.4", headers=auth_headers)
            assert resp.status_code == 200
            data = resp.json()
            assert data["formatted_address"] == "Musterstraße 5, 12345 Berlin"
            assert data["street"] == "Musterstraße"
            assert data["house_number"] == "5"
            assert data["postal_code"] == "12345"
            assert data["city"] == "Berlin"
            assert data["source"] == "nominatim"
            assert data["message"] is None
        finally:
            patcher.stop()

    def test_road_without_house_number(self, client: TestClient, auth_headers: dict):
        patcher = _patch_nominatim({"road": "Waldweg", "postcode": "10000", "city": "München"})
        try:
            resp = client.get("/api/v1/geocoding/reverse?latitude=48.1&longitude=11.5", headers=auth_headers)
            assert resp.status_code == 200
            data = resp.json()
            assert data["formatted_address"] == "Waldweg, 10000 München"
            assert data["house_number"] is None
        finally:
            patcher.stop()

    def test_town_fallback_for_city(self, client: TestClient, auth_headers: dict):
        patcher = _patch_nominatim({"road": "Dorfstraße", "postcode": "99999", "town": "Kleinstadt"})
        try:
            resp = client.get("/api/v1/geocoding/reverse?latitude=51.0&longitude=10.0", headers=auth_headers)
            assert resp.status_code == 200
            data = resp.json()
            assert data["city"] == "Kleinstadt"
            assert "Kleinstadt" in (data["formatted_address"] or "")
        finally:
            patcher.stop()

    def test_empty_address_returns_null_with_message(self, client: TestClient, auth_headers: dict):
        patcher = _patch_nominatim({})
        try:
            resp = client.get("/api/v1/geocoding/reverse?latitude=0.0&longitude=0.0", headers=auth_headers)
            assert resp.status_code == 200
            data = resp.json()
            assert data["formatted_address"] is None
            assert data["message"] is not None
        finally:
            patcher.stop()


class TestReverseGeocodeProviderFailure:
    def test_network_error_returns_200_with_null_address(self, client: TestClient, auth_headers: dict):
        with patch("app.services.reverse_geocoding.httpx.Client") as mock_cls:
            mock_cls.return_value.__enter__.return_value.get.side_effect = Exception("connection refused")
            resp = client.get("/api/v1/geocoding/reverse?latitude=52.5&longitude=13.4", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["formatted_address"] is None
        assert data["message"] is not None
        assert data["source"] == "nominatim"

    def test_http_error_returns_200_with_null_address(self, client: TestClient, auth_headers: dict):
        with patch("app.services.reverse_geocoding.httpx.Client") as mock_cls:
            mock_cls.return_value.__enter__.return_value.get.side_effect = Exception("503 Service Unavailable")
            resp = client.get("/api/v1/geocoding/reverse?latitude=52.5&longitude=13.4", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["formatted_address"] is None
