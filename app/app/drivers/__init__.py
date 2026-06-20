from fastapi import APIRouter

from app.drivers.qod_provisioning import router as qod_provisioning_router

router = APIRouter()
router.include_router(qod_provisioning_router)
