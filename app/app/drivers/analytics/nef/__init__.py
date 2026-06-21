from app.drivers.analytics.nef.backend import NefAnalyticsBackend
from app.drivers.analytics.nef.callbacks import router as router
from app.settings import settings

if settings.net_apis.api != "nef":
    raise RuntimeError("Analytics NEF driver instantiated but net_apis.api isn't 'nef'")

nef_analytics_interface = NefAnalyticsBackend()
