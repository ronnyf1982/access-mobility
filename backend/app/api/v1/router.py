from fastapi import APIRouter

from app.api.v1.endpoints import auth, health, mobility_profile

router = APIRouter()
router.include_router(health.router, tags=["health"])
router.include_router(auth.router)
router.include_router(mobility_profile.router)
