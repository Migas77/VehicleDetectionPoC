from fastapi import APIRouter

from app.routers.endpoints import router as endpoints_router
from app.routers.websockets import router as websockets_router

router = APIRouter()
router.include_router(endpoints_router)
router.include_router(websockets_router)
