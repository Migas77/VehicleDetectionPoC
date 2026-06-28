from fastapi import APIRouter

from app.routers.endpoints.crash_status import router as crash_status_router

router = APIRouter()
router.include_router(crash_status_router)
