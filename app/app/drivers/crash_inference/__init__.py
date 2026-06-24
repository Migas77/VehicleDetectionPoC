from typing import Annotated

from fastapi import APIRouter, Depends

from app.drivers.crash_inference.backend import RoboflowCrashInferenceBackend
from app.drivers.crash_inference.callbacks import router as callbacks_router
from app.interfaces.crash_inference import CrashInferenceInterface

crash_inference_interface: CrashInferenceInterface = RoboflowCrashInferenceBackend()

router = APIRouter()
router.include_router(callbacks_router)


async def get_crash_inference_interface() -> CrashInferenceInterface:
    return crash_inference_interface


CrashInferenceInterfaceDep = Annotated[
    CrashInferenceInterface, Depends(get_crash_inference_interface)
]
