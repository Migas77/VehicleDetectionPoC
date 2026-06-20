import logging
from abc import ABC, abstractmethod

from app.schemas.camara.location import Location
from app.schemas.poc.ue import UE

LOG = logging.getLogger(__name__)


class LocationInterface(ABC):
    @abstractmethod
    async def retrieve_location(self, ue: UE) -> Location:
        """Retrieve the current location of the UE."""
