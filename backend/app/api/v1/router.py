from fastapi import APIRouter

from app.api.v1.endpoints import assistant, auth, driver, drivers, health, mobility_profile, onboarding, platform_admin, preview_access_admin, public_gate, transport_options, transport_requests, vehicles

router = APIRouter()
router.include_router(health.router, tags=["health"])
router.include_router(auth.router)
router.include_router(onboarding.router)
router.include_router(assistant.router)
router.include_router(mobility_profile.router)
router.include_router(vehicles.router)
router.include_router(drivers.router)
router.include_router(driver.router)
router.include_router(transport_options.router)
router.include_router(transport_requests.router)
router.include_router(platform_admin.router)
router.include_router(preview_access_admin.router)
router.include_router(public_gate.router)
