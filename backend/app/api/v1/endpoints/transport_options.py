from fastapi import APIRouter
from app.core.transport_presets import TRANSPORT_PRESETS

router = APIRouter(prefix="/transport-options", tags=["transport-options"])


@router.get("")
def get_transport_options() -> list:
    """Gibt alle verfügbaren Transporttypen zurück — ohne Auth nutzbar."""
    return TRANSPORT_PRESETS
