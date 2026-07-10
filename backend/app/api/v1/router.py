from fastapi import APIRouter

from app.api.v1.endpoints import auth, drivers, health, mobility_profile, transport_options, vehicles

router = APIRouter()
router.include_router(health.router, tags=["health"])
router.include_router(auth.router)
router.include_router(mobility_profile.router)
router.include_router(vehicles.router)
router.include_router(drivers.router)
router.include_router(transport_options.router)
