"""Reverse geocoding via Nominatim (OpenStreetMap).

MVP/Preview: routes coordinates → street address through the public Nominatim API.

Production considerations:
- Check Nominatim usage policy (max 1 req/s, attribution required).
- For higher volume: self-hosted Nominatim or a commercial geocoding provider.
- No coordinates are stored or logged by this service.
- Provider can be swapped by replacing this module without touching the endpoint.
"""
from __future__ import annotations

import httpx

from app.schemas.geocoding import ReverseGeocodeResponse

_NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
_TIMEOUT_S = 5.0
_SOURCE = "nominatim"


def reverse_geocode(latitude: float, longitude: float) -> ReverseGeocodeResponse:
    """Resolve coordinates to a human-readable address.

    Returns a response with formatted_address=None and a message if the
    external service is unreachable or returns no usable address data.
    Never raises — callers always get a valid ReverseGeocodeResponse.
    """
    try:
        with httpx.Client(timeout=_TIMEOUT_S) as client:
            resp = client.get(
                _NOMINATIM_URL,
                params={
                    "format": "jsonv2",
                    "lat": latitude,
                    "lon": longitude,
                    "addressdetails": 1,
                },
                headers={"User-Agent": "access-mobility/1.0 (barrierefreie-mobilitaet)"},
            )
            resp.raise_for_status()
            data = resp.json()
    except Exception:
        return ReverseGeocodeResponse(
            source=_SOURCE,
            message="Geocoding-Dienst nicht erreichbar.",
        )

    address = data.get("address", {})
    road = (
        address.get("road")
        or address.get("pedestrian")
        or address.get("path")
        or address.get("footway")
    )
    house_number = address.get("house_number")
    postcode = address.get("postcode")
    city = (
        address.get("city")
        or address.get("town")
        or address.get("village")
        or address.get("municipality")
        or address.get("county")
    )

    parts: list[str] = []
    if road:
        parts.append(f"{road} {house_number}" if house_number else road)
    if postcode and city:
        parts.append(f"{postcode} {city}")
    elif city:
        parts.append(city)
    elif postcode:
        parts.append(postcode)

    formatted = ", ".join(parts) if parts else None

    return ReverseGeocodeResponse(
        formatted_address=formatted,
        street=road,
        house_number=house_number,
        postal_code=postcode,
        city=city,
        source=_SOURCE,
        message=None if formatted else "Adresse konnte nicht automatisch ermittelt werden.",
    )
