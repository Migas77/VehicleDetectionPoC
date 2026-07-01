from fastapi import APIRouter

from app.routers.endpoints.cameras import router as cameras_router
from app.routers.endpoints.config import router as config_router
from app.routers.endpoints.crash_status import router as crash_status_router

router = APIRouter()
router.include_router(cameras_router)
router.include_router(config_router)
router.include_router(crash_status_router)
