"""Reverse geocoding via Nominatim (OpenStreetMap).

MVP/Preview: routes coordinates → street address through the public Nominatim API.

Production considerations:
- Check Nominatim usage policy (max 1 req/s, attribution required).
- For higher volume: self-hosted Nominatim or a commercial geocoding provider.
- No coordinates are stored or logged by this service.
- Provider can be swapped by replacing this module without touching the endpoint.
"""
from __future__ import annotations

import math

import httpx

from app.schemas.geocoding import ReverseGeocodeResponse

_NOMINATIM_REVERSE_URL = "https://nominatim.openstreetmap.org/reverse"
_NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"
_TIMEOUT_S = 5.0
_SOURCE = "nominatim"
_NEAREST_RADIUS_M = 100.0
_HEADERS = {"User-Agent": "access-mobility/1.0 (barrierefreie-mobilitaet)"}


def _extract_road(address: dict) -> str | None:
    return (
        address.get("road")
        or address.get("pedestrian")
        or address.get("path")
        or address.get("footway")
    )


def _extract_city(address: dict) -> str | None:
    return (
        address.get("city")
        or address.get("town")
        or address.get("village")
        or address.get("municipality")
        or address.get("county")
    )


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6_371_000.0
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _find_nearest_with_house_number(
    client: httpx.Client,
    lat: float,
    lon: float,
    road: str,
    city: str | None,
    postcode: str | None,
) -> dict | None:
    """Search Nominatim for the nearest address with a house number.

    Returns the closest search result within _NEAREST_RADIUS_M metres, or None.
    Never raises — all errors are silently swallowed so the caller falls back
    to the approximate result.
    """
    query_parts = [road]
    if city:
        query_parts.append(city)
    elif postcode:
        query_parts.append(postcode)

    try:
        resp = client.get(
            _NOMINATIM_SEARCH_URL,
            params={
                "q": " ".join(query_parts),
                "format": "jsonv2",
                "addressdetails": 1,
                "limit": 10,
            },
            headers=_HEADERS,
        )
        resp.raise_for_status()
        results = resp.json()
        if not isinstance(results, list):
            return None
    except Exception:
        return None

    best: dict | None = None
    best_dist = float("inf")
    for item in results:
        addr = item.get("address", {})
        if not addr.get("house_number"):
            continue
        try:
            rlat = float(item["lat"])
            rlon = float(item["lon"])
        except (KeyError, ValueError, TypeError):
            continue
        dist = _haversine_m(lat, lon, rlat, rlon)
        if dist <= _NEAREST_RADIUS_M and dist < best_dist:
            best_dist = dist
            best = item

    return best


def reverse_geocode(latitude: float, longitude: float) -> ReverseGeocodeResponse:
    """Resolve coordinates to a human-readable address.

    Always returns a usable value: precise address → nearest address with house
    number (within 100 m) → approximate address → coordinate string. Never raises.

    precision values:
      "precise"     – road + house number from reverse geocoding
      "nearest"     – road + house number from nearby address search (within 100 m)
      "approximate" – road without house number, or city/postcode only
      "coordinates" – no address found; formatted_address is "Standort: lat, lon"
    """
    coordinate_fallback = f"Standort: {latitude:.4f}, {longitude:.4f}"

    try:
        with httpx.Client(timeout=_TIMEOUT_S) as client:
            resp = client.get(
                _NOMINATIM_REVERSE_URL,
                params={
                    "format": "jsonv2",
                    "lat": latitude,
                    "lon": longitude,
                    "addressdetails": 1,
                },
                headers=_HEADERS,
            )
            resp.raise_for_status()
            data = resp.json()

            address = data.get("address", {})
            road = _extract_road(address)
            house_number = address.get("house_number")
            postcode = address.get("postcode")
            city = _extract_city(address)

            nearest: dict | None = None
            if road and not house_number:
                nearest = _find_nearest_with_house_number(
                    client, latitude, longitude, road, city, postcode
                )
    except Exception:
        return ReverseGeocodeResponse(
            formatted_address=coordinate_fallback,
            precision="coordinates",
            source=_SOURCE,
            message="Geocoding-Dienst nicht erreichbar.",
        )

    # If a nearby search result with house number was found, use it
    if nearest:
        n_addr = nearest.get("address", {})
        n_road = _extract_road(n_addr) or road
        n_hn = n_addr.get("house_number")
        n_pc = n_addr.get("postcode") or postcode
        n_city = _extract_city(n_addr) or city
        parts: list[str] = []
        if n_road:
            parts.append(f"{n_road} {n_hn}" if n_hn else n_road)
        if n_pc and n_city:
            parts.append(f"{n_pc} {n_city}")
        elif n_city:
            parts.append(n_city)
        elif n_pc:
            parts.append(n_pc)
        if parts:
            return ReverseGeocodeResponse(
                formatted_address=", ".join(parts),
                street=n_road,
                house_number=n_hn,
                postal_code=n_pc,
                city=n_city,
                precision="nearest",
                source=_SOURCE,
                message=None,
            )

    # Build response from the reverse geocoding result
    parts = []
    if road:
        parts.append(f"{road} {house_number}" if house_number else road)
    if postcode and city:
        parts.append(f"{postcode} {city}")
    elif city:
        parts.append(city)
    elif postcode:
        parts.append(postcode)

    if not parts:
        return ReverseGeocodeResponse(
            formatted_address=coordinate_fallback,
            street=road,
            house_number=None,
            postal_code=postcode,
            city=city,
            precision="coordinates",
            source=_SOURCE,
            message="Keine genaue Adresse gefunden. Koordinaten werden als Abholort verwendet.",
        )

    precision = "precise" if (road and house_number) else "approximate"
    return ReverseGeocodeResponse(
        formatted_address=", ".join(parts),
        street=road,
        house_number=house_number,
        postal_code=postcode,
        city=city,
        precision=precision,
        source=_SOURCE,
        message=None,
    )
