from fastapi import APIRouter

from app.routers.websockets.crash_status import router as crash_status_router
from app.routers.websockets.location import router as location_router

router = APIRouter(prefix="/ws")
router.include_router(location_router)
router.include_router(crash_status_router)
