from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.crud import crud_notification_preference
from app.models.mobility_profile import MobilityProfile
from app.models.user import User, UserRole
from app.schemas.notification_preference import NotificationPreferenceRead, NotificationPreferenceUpsert

router = APIRouter(prefix="/passenger/notification-preferences", tags=["notification-preferences"])


def _get_mobility_profile_or_403(db: Session, current_user: User) -> MobilityProfile:
    if current_user.role != UserRole.passenger:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Nur Fahrgäste können Benachrichtigungseinstellungen verwalten.")
    profile = db.query(MobilityProfile).filter(MobilityProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kein Mobilitätsprofil gefunden.")
    return profile


@router.get("", response_model=list[NotificationPreferenceRead])
def get_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[NotificationPreferenceRead]:
    profile = _get_mobility_profile_or_403(db, current_user)
    prefs = crud_notification_preference.get_preferences(db, profile.id)
    return [NotificationPreferenceRead.model_validate(p) for p in prefs]


@router.put("", response_model=list[NotificationPreferenceRead])
def save_preferences(
    body: list[NotificationPreferenceUpsert],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[NotificationPreferenceRead]:
    profile = _get_mobility_profile_or_403(db, current_user)

    results = []
    for item in body:
        pref = crud_notification_preference.upsert_preference(
            db,
            mobility_profile_id=profile.id,
            event_type=item.event_type,
            notify_trusted_persons=item.notify_trusted_persons,
            channel_in_app=item.channel_in_app,
            channel_email=item.channel_email,
            channel_sms=item.channel_sms,
        )
        results.append(pref)

    db.commit()
    for p in results:
        db.refresh(p)
    return [NotificationPreferenceRead.model_validate(p) for p in results]
