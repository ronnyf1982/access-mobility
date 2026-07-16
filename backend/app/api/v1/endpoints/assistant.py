from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User, UserRole

router = APIRouter(prefix="/assistant", tags=["assistant"])

_PASSENGER_CAPABILITIES = [
    {"id": "onboarding", "label": "Ersteinrichtung", "available": True},
    {"id": "mobility_profile", "label": "Mobilitätsprofil", "available": True},
    {"id": "book_ride", "label": "Fahrt anfragen", "available": False, "planned_sprint": 14},
    {"id": "ride_status", "label": "Fahrtstatus abfragen", "available": False, "planned_sprint": 12},
    {"id": "share_location", "label": "Fahrt teilen", "available": False, "planned_sprint": 12},
]

_DRIVER_CAPABILITIES = [
    {"id": "shift_start", "label": "Schicht beginnen", "available": False, "planned_sprint": 10},
    {"id": "ride_status_update", "label": "Fahrstatus melden", "available": False, "planned_sprint": 11},
]

_PASSENGER_ROLES = {UserRole.passenger, UserRole.trusted_person, UserRole.organization_coordinator}


@router.get("/capabilities")
def get_capabilities(current_user: User = Depends(get_current_user)) -> dict:
    if current_user.role in _PASSENGER_ROLES:
        caps = _PASSENGER_CAPABILITIES
    elif current_user.role == UserRole.driver:
        caps = _DRIVER_CAPABILITIES
    else:
        caps = []
    return {
        "role": current_user.role.value,
        "voice_mode_enabled": current_user.voice_mode_enabled,
        "capabilities": caps,
    }
