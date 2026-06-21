from typing import Annotated

from fastapi import APIRouter, Depends

from app.interfaces.analytics import AnalyticsInterface
from app.settings import settings

analytics_interface: AnalyticsInterface
router = APIRouter(prefix="/callbacks/analytics")

match settings.net_apis.api:
    case "nef":
        from .nef import nef_analytics_interface
        from .nef import router as nef_router

        analytics_interface = nef_analytics_interface
        router.include_router(nef_router)
    case "camara":
        from .camara import camara_analytics_interface
        from .camara import router as camara_router

        analytics_interface = camara_analytics_interface
        router.include_router(camara_router)


async def get_analytics_interface() -> AnalyticsInterface:
    return analytics_interface


AnalyticsInterfaceDep = Annotated[AnalyticsInterface, Depends(get_analytics_interface)]
