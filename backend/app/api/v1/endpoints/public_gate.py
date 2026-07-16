from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import crud_preview_access
from app.schemas.preview_access import PublicGateLoginRequest

router = APIRouter(prefix="/public", tags=["public"])


@router.post("/test-access/login")
async def gate_login(payload: PublicGateLoginRequest, db: Session = Depends(get_db)) -> dict:
    """Validate preview-site access credentials. Returns ok:true or 401."""
    user = crud_preview_access.validate_login(db, payload.email_or_username, payload.password)
    if not user:
        # Always same 401 — never reveal whether user exists or is deactivated
        raise HTTPException(status_code=401, detail="Zugangsdaten nicht korrekt.")
    return {"ok": True}
