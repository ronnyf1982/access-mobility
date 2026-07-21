from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.geocoding import ReverseGeocodeResponse
from app.services import reverse_geocoding

router = APIRouter(prefix="/geocoding", tags=["geocoding"])


@router.get("/reverse", response_model=ReverseGeocodeResponse)
def reverse_geocode(
    latitude: Annotated[float, Query(ge=-90.0, le=90.0, description="Breitengrad")],
    longitude: Annotated[float, Query(ge=-180.0, le=180.0, description="Längengrad")],
    current_user: User = Depends(get_current_user),
) -> ReverseGeocodeResponse:
    """Resolve coordinates to a street address via Nominatim.

    No coordinates or results are stored. Requires authentication to prevent
    unauthenticated bulk geocoding via the platform's proxy.
    """
    return reverse_geocoding.reverse_geocode(latitude, longitude)
