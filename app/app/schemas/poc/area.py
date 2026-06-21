from functools import cached_property
from typing import Annotated

from pydantic import BaseModel, Field
from shapely import Polygon as ShapelyPolygon

from app.schemas.camara.common import Point


class SurveyedArea(BaseModel):
    """A camera's surveilled area, passed to the geofencing interface.

    The CAMARA backend always uses ``center`` + ``radius`` (a Circle); the NEF backend
    may additionally use ``points`` to refine the geofence into a polygon.
    """

    camera_id: int  # owning camera UE id — used in callback URLs + occupant set
    center: Point  # camera location (lat/long); CAMARA Circle center
    radius: Annotated[int, Field(ge=1, le=200000)]  # metres; CAMARA Circle radius
    points: list[Point] | None = None  # optional polygon vertices (NEF refinement)

    @cached_property
    def polygon(self) -> ShapelyPolygon | None:
        """Surveyed polygon in (lon, lat) order, decoded once on first access.

        None when no points are configured (the NEF backend then falls back to the circle).
        Planar/Cartesian approximation — fine for small surveyed areas.
        """
        if not self.points:
            return None
        return ShapelyPolygon(
            [(point.longitude, point.latitude) for point in self.points]
        )
