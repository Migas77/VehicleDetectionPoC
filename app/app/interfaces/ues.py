from abc import ABC, abstractmethod
from typing import TypedDict

from app.schemas.poc import CarUE, DynamicCameraUE, PedestrianUE, PocUE, StaticCameraUE
from app.schemas.poc.ue import UE


class PocUEsByType(TypedDict):
    car_ues: list[CarUE]
    static_camera_ues: list[StaticCameraUE]
    dynamic_camera_ues: list[DynamicCameraUE]
    pedestrian_ues: list[PedestrianUE]


class UEsInterface(ABC):
    @abstractmethod
    async def get_ues(self) -> list[UE]:
        """Return the full UE list from the NEF."""

    @abstractmethod
    async def get_poc_ues(self) -> list[PocUE]:
        """Return UEs parsed and discriminated as PocUE types."""

    @abstractmethod
    async def get_poc_ues_by_type(self) -> PocUEsByType:
        """Return PocUEs grouped by UE type (car, static camera, dynamic camera, pedestrian)."""

    @abstractmethod
    async def start_movement(self, supi: str) -> bool:
        """Start the movement loop for the UE with the given SUPI. Returns True on success."""

    @abstractmethod
    async def stop_movement(self, supi: str) -> bool:
        """Stop the movement loop for the UE with the given SUPI. Returns True on success."""
