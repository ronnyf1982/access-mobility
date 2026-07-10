from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import create_access_token, verify_password
from app.crud.crud_user import get_by_email
from app.db.session import get_db
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import LoginRequest, UserPublic

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> Token:
    user = get_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-Mail-Adresse oder Passwort ungültig",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Konto ist deaktiviert",
        )
    token = create_access_token(str(user.id), user.role.value)
    return Token(access_token=token, user=UserPublic.model_validate(user))


@router.get("/me", response_model=UserPublic)
def me(current_user: User = Depends(get_current_user)) -> UserPublic:
    return UserPublic.model_validate(current_user)


@router.post("/logout")
def logout() -> dict:
    return {"message": "Abgemeldet. Token clientseitig entfernen."}
