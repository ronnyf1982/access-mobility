import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.trusted_relationship import TrustedRelationship, TrustStatus
from app.models.user import User, UserRole
from app.schemas.spontaneous_ride import SpontaneousRideMatchRequest, SpontaneousRideMatchResult
from app.services import spontaneous_matching

router = APIRouter(prefix="/spontaneous-rides", tags=["spontaneous-rides"])

_STAFF_ROLES = {
    UserRole.dispatcher,
    UserRole.organization_coordinator,
    UserRole.provider_admin,
    UserRole.platform_admin,
}


def _resolve_passenger_id(
    body: SpontaneousRideMatchRequest,
    current_user: User,
    db: Session,
) -> uuid.UUID:
    """Resolve which passenger's profile to use for capability matching."""
    if current_user.role == UserRole.passenger:
        if body.passenger_user_id and body.passenger_user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Fahrgäste können nur für sich selbst suchen.",
            )
        return current_user.id

    if current_user.role == UserRole.trusted_person:
        target_id = body.passenger_user_id
        if not target_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Vertrauenspersonen müssen passenger_user_id angeben.",
            )
        rel = (
            db.query(TrustedRelationship)
            .filter(
                TrustedRelationship.trusted_user_id == current_user.id,
                TrustedRelationship.passenger_user_id == target_id,
                TrustedRelationship.can_view_rides.is_(True),
                TrustedRelationship.status == TrustStatus.active,
            )
            .first()
        )
        if not rel:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Keine aktive Vertrauensbeziehung für diesen Fahrgast.",
            )
        return target_id

    if current_user.role in _STAFF_ROLES:
        return body.passenger_user_id or current_user.id

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Zugriff verweigert.")


@router.post(
    "/matches",
    response_model=list[SpontaneousRideMatchResult],
)
def find_spontaneous_matches(
    body: SpontaneousRideMatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[SpontaneousRideMatchResult]:
    passenger_id = _resolve_passenger_id(body, current_user, db)
    return spontaneous_matching.find_matches(
        db=db,
        pickup_lat=body.pickup_latitude,
        pickup_lon=body.pickup_longitude,
        passenger_user_id=passenger_id,
    )
