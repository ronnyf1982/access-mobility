from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.crud.crud_mobility_profile import get_by_user_id
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserPublic

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


class OnboardingStatus(BaseModel):
    needs_onboarding: bool
    voice_mode_enabled: bool
    onboarding_completed_at: datetime | None
    mobility_profile_filled: bool


class OnboardingPreferences(BaseModel):
    voice_mode_enabled: bool


@router.get("/status", response_model=OnboardingStatus)
def get_onboarding_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OnboardingStatus:
    profile = get_by_user_id(db, current_user.id)
    mobility_profile_filled = profile is not None and bool(
        profile.uses_wheelchair
        or profile.uses_rollator
        or profile.is_blind_or_visually_impaired
        or profile.is_deaf_or_hard_of_hearing
        or profile.needs_escort
    )
    return OnboardingStatus(
        needs_onboarding=current_user.onboarding_completed_at is None,
        voice_mode_enabled=current_user.voice_mode_enabled,
        onboarding_completed_at=current_user.onboarding_completed_at,
        mobility_profile_filled=mobility_profile_filled,
    )


@router.post("/preferences", response_model=UserPublic)
def save_onboarding_preferences(
    payload: OnboardingPreferences,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserPublic:
    current_user.voice_mode_enabled = payload.voice_mode_enabled
    current_user.onboarding_completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(current_user)
    return UserPublic.model_validate(current_user)
