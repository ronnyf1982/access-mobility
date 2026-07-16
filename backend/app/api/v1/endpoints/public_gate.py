import os
import secrets

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/public", tags=["public"])


class GateRequest(BaseModel):
    code: str


@router.post("/test-access")
async def validate_test_access(payload: GateRequest) -> dict:
    """Validate the preview-site access code against the TEST_ACCESS_CODE env var."""
    expected = os.environ.get("TEST_ACCESS_CODE", "")
    if not expected:
        raise HTTPException(status_code=503, detail="Testzugang nicht konfiguriert.")
    # constant-time comparison — avoids timing attacks
    if not secrets.compare_digest(payload.code, expected):
        raise HTTPException(status_code=401, detail="Zugangsdaten nicht korrekt.")
    return {"ok": True}
