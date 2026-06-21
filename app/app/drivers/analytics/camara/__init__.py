from app.drivers.analytics.camara.backend import CamaraAnalyticsBackend
from app.drivers.analytics.camara.callbacks import router as router
from app.settings import settings

if settings.net_apis.api != "camara":
    raise RuntimeError(
        "Analytics CAMARA driver instantiated but net_apis.api isn't 'camara'"
    )

camara_analytics_interface = CamaraAnalyticsBackend()
