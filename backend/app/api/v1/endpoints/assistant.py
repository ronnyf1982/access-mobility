from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User, UserRole

router = APIRouter(prefix="/assistant", tags=["assistant"])

_PASSENGER_CAPABILITIES = [
    {"id": "onboarding", "label": "Ersteinrichtung", "available": True},
    {
        "id": "mobility_profile",
        "label": "Mobilitätsprofil",
        "available": True,
        "guided_check": True,
        "guided_check_route": "/mobility-profile/assistant",
        "offline_supported": True,
        "online_ai_supported": False,
    },
    {"id": "book_ride", "label": "Fahrt anfragen", "available": False, "planned_sprint": 14},
    {"id": "ride_status", "label": "Fahrtstatus abfragen", "available": False, "planned_sprint": 12},
    {"id": "share_location", "label": "Fahrt teilen", "available": False, "planned_sprint": 12},
]

_DRIVER_CAPABILITIES = [
    {
        "id": "driver_shift",
        "label": "Schicht & Fahrzeugwahl",
        "available": True,
        "route": "/driver",
        "actions": ["start_shift", "select_vehicle_by_license_plate", "end_shift", "pause_shift", "resume_shift"],
        "confirmation_required": ["start_shift", "end_shift", "vehicle_selection"],
        "voice_mode": "voice_later",
        "offline_supported": False,
        "safety_notes": [
            "Keine Statusänderung ohne Bestätigung",
            "Fahrer-App darf nicht ablenken",
            "Spracheingabe kommt in späterem Sprint",
        ],
    },
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
