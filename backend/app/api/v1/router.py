from fastapi import APIRouter

from app.api.v1.endpoints import assistant, auth, driver, drivers, geocoding, health, mobility_profile, notification_preferences, onboarding, passenger_contacts, platform_admin, preview_access_admin, public_gate, ride_status_events, spontaneous_rides, transport_options, transport_requests, vehicles

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
router.include_router(ride_status_events.router)
router.include_router(spontaneous_rides.router)
router.include_router(notification_preferences.router)
router.include_router(platform_admin.router)
router.include_router(preview_access_admin.router)
router.include_router(public_gate.router)
router.include_router(geocoding.router)
router.include_router(passenger_contacts.router)
