"""Geocoding endpoint tests (Hotfix 12D-D / 12D-E, Sprint 12F-C).

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


def _patch_nominatim_with_search(reverse_address: dict, search_results: list):
    """Mock two sequential get() calls: reverse then search."""
    reverse_resp = MagicMock()
    reverse_resp.json.return_value = {"address": reverse_address}
    reverse_resp.raise_for_status = MagicMock()

    search_resp = MagicMock()
    search_resp.json.return_value = search_results
    search_resp.raise_for_status = MagicMock()

    patcher = patch("app.services.reverse_geocoding.httpx.Client")
    mock_client_cls = patcher.start()
    mock_client_cls.return_value.__enter__.return_value.get.side_effect = [
        reverse_resp,
        search_resp,
    ]
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
            assert data["precision"] == "precise"
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
            assert data["precision"] == "approximate"
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

    def test_empty_address_returns_coordinate_fallback(self, client: TestClient, auth_headers: dict):
        patcher = _patch_nominatim({})
        try:
            resp = client.get("/api/v1/geocoding/reverse?latitude=0.0&longitude=0.0", headers=auth_headers)
            assert resp.status_code == 200
            data = resp.json()
            assert data["formatted_address"] == "Standort: 0.0000, 0.0000"
            assert data["precision"] == "coordinates"
            assert data["message"] is not None
        finally:
            patcher.stop()


class TestReverseGeocodeProviderFailure:
    def test_network_error_returns_coordinate_fallback(self, client: TestClient, auth_headers: dict):
        with patch("app.services.reverse_geocoding.httpx.Client") as mock_cls:
            mock_cls.return_value.__enter__.return_value.get.side_effect = Exception("connection refused")
            resp = client.get("/api/v1/geocoding/reverse?latitude=52.5&longitude=13.4", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["formatted_address"] == "Standort: 52.5000, 13.4000"
        assert data["precision"] == "coordinates"
        assert data["message"] is not None
        assert data["source"] == "nominatim"

    def test_http_error_returns_coordinate_fallback(self, client: TestClient, auth_headers: dict):
        with patch("app.services.reverse_geocoding.httpx.Client") as mock_cls:
            mock_cls.return_value.__enter__.return_value.get.side_effect = Exception("503 Service Unavailable")
            resp = client.get("/api/v1/geocoding/reverse?latitude=52.5&longitude=13.4", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["formatted_address"] == "Standort: 52.5000, 13.4000"
        assert data["precision"] == "coordinates"


class TestReverseGeocodePrecision:
    def test_road_and_house_number_is_precise(self, client: TestClient, auth_headers: dict):
        patcher = _patch_nominatim({"road": "Hauptstraße", "house_number": "12", "city": "Hamburg"})
        try:
            resp = client.get("/api/v1/geocoding/reverse?latitude=53.5&longitude=10.0", headers=auth_headers)
            data = resp.json()
            assert data["precision"] == "precise"
        finally:
            patcher.stop()

    def test_city_only_is_approximate(self, client: TestClient, auth_headers: dict):
        patcher = _patch_nominatim({"city": "Köln", "postcode": "50667"})
        try:
            resp = client.get("/api/v1/geocoding/reverse?latitude=50.9&longitude=6.9", headers=auth_headers)
            data = resp.json()
            assert data["precision"] == "approximate"
            assert data["formatted_address"] == "50667 Köln"
        finally:
            patcher.stop()

    def test_coordinate_fallback_formatted_address_uses_4_decimals(self, client: TestClient, auth_headers: dict):
        patcher = _patch_nominatim({})
        try:
            resp = client.get("/api/v1/geocoding/reverse?latitude=48.1234&longitude=11.5678", headers=auth_headers)
            data = resp.json()
            assert data["formatted_address"] == "Standort: 48.1234, 11.5678"
            assert data["precision"] == "coordinates"
        finally:
            patcher.stop()

    def test_coordinate_fallback_message_set(self, client: TestClient, auth_headers: dict):
        patcher = _patch_nominatim({})
        try:
            resp = client.get("/api/v1/geocoding/reverse?latitude=52.0&longitude=13.0", headers=auth_headers)
            data = resp.json()
            assert "Koordinaten" in data["message"]
        finally:
            patcher.stop()


class TestNearestHouseNumber:
    """Sprint 12F-C: secondary search for house number when reverse returns none."""

    def test_nearest_search_finds_nearby_address_with_house_number(
        self, client: TestClient, auth_headers: dict
    ):
        # Reverse: road but no house_number. Search: one result 65 m away with house_number.
        patcher = _patch_nominatim_with_search(
            reverse_address={"road": "Teststraße", "postcode": "10115", "city": "Berlin"},
            search_results=[
                {
                    "lat": "52.5005",
                    "lon": "13.4005",
                    "address": {
                        "road": "Teststraße",
                        "house_number": "7",
                        "postcode": "10115",
                        "city": "Berlin",
                    },
                }
            ],
        )
        try:
            resp = client.get(
                "/api/v1/geocoding/reverse?latitude=52.5&longitude=13.4",
                headers=auth_headers,
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["precision"] == "nearest"
            assert data["house_number"] == "7"
            assert "Teststraße 7" in data["formatted_address"]
            assert data["message"] is None
        finally:
            patcher.stop()

    def test_nearest_search_result_too_far_away_falls_back_to_approximate(
        self, client: TestClient, auth_headers: dict
    ):
        # Search result is ~1.1 km away — beyond 100 m radius → not used.
        patcher = _patch_nominatim_with_search(
            reverse_address={"road": "Waldweg", "postcode": "10000", "city": "München"},
            search_results=[
                {
                    "lat": "48.11",  # ~1.1 km from 48.1
                    "lon": "11.5",
                    "address": {
                        "road": "Waldweg",
                        "house_number": "99",
                        "postcode": "10000",
                        "city": "München",
                    },
                }
            ],
        )
        try:
            resp = client.get(
                "/api/v1/geocoding/reverse?latitude=48.1&longitude=11.5",
                headers=auth_headers,
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["precision"] == "approximate"
            assert data["house_number"] is None
            assert "99" not in (data["formatted_address"] or "")
        finally:
            patcher.stop()

    def test_nearest_search_returns_empty_list_falls_back_to_approximate(
        self, client: TestClient, auth_headers: dict
    ):
        patcher = _patch_nominatim_with_search(
            reverse_address={"road": "Feldstraße", "postcode": "20000", "city": "Hamburg"},
            search_results=[],
        )
        try:
            resp = client.get(
                "/api/v1/geocoding/reverse?latitude=53.5&longitude=10.0",
                headers=auth_headers,
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["precision"] == "approximate"
            assert data["formatted_address"] == "Feldstraße, 20000 Hamburg"
        finally:
            patcher.stop()

    def test_nearest_search_returns_results_without_house_number_falls_back_to_approximate(
        self, client: TestClient, auth_headers: dict
    ):
        # All search results lack house_number → no usable result.
        patcher = _patch_nominatim_with_search(
            reverse_address={"road": "Parkweg", "postcode": "30000", "city": "Hannover"},
            search_results=[
                {
                    "lat": "52.3701",
                    "lon": "9.7302",
                    "address": {"road": "Parkweg", "postcode": "30000", "city": "Hannover"},
                }
            ],
        )
        try:
            resp = client.get(
                "/api/v1/geocoding/reverse?latitude=52.37&longitude=9.73",
                headers=auth_headers,
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["precision"] == "approximate"
            assert data["house_number"] is None
        finally:
            patcher.stop()

    def test_nearest_search_network_failure_falls_back_to_approximate(
        self, client: TestClient, auth_headers: dict
    ):
        # First call (reverse) succeeds; second call (search) raises → falls back gracefully.
        reverse_resp = MagicMock()
        reverse_resp.json.return_value = {"address": {"road": "Bergstraße", "city": "Dresden"}}
        reverse_resp.raise_for_status = MagicMock()

        with patch("app.services.reverse_geocoding.httpx.Client") as mock_cls:
            mock_cls.return_value.__enter__.return_value.get.side_effect = [
                reverse_resp,
                Exception("search network error"),
            ]
            resp = client.get(
                "/api/v1/geocoding/reverse?latitude=51.0&longitude=13.7",
                headers=auth_headers,
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["precision"] == "approximate"
        assert data["house_number"] is None
