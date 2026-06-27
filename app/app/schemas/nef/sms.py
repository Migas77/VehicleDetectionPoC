from pydantic import BaseModel, model_validator

from app.schemas.nef.analytics_exposure import Supi
from app.schemas.nef.commonData import Gpsi


class SMSSendRequest(BaseModel):
    gpsi: Gpsi | None = None
    supi: Supi | None = None
    text: str

    @model_validator(mode="after")
    def _at_least_one_identifier(self) -> "SMSSendRequest":
        if self.gpsi is None and self.supi is None:
            raise ValueError("at least one of gpsi or supi must be provided")
        return self
