from app.drivers.sms.nef.backend import NefSMSBackend
from app.settings import settings

if settings.net_apis.api != "nef":
    raise RuntimeError("NefSMSBackend instantiated but net_apis.api isn't 'nef'")


nef_sms_interface = NefSMSBackend()
