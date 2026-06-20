from fastapi import APIRouter

from app.routers.websockets import router as websockets_router

router = APIRouter()
router.include_router(websockets_router)
