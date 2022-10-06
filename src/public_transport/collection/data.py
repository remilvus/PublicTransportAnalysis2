"""Enums and containers related to GTFS collection."""
from dataclasses import dataclass
from enum import Enum


class TransitCategory(Enum):
    """Types of static and real-time GTFS files."""

    static = "static"
    vehicle_position = "vehicle_position"
    trip_update = "trip_update"
    alert = "alert"


@dataclass(frozen=True)
class TransitFile:
    """GTFS file's contents and metadata."""

    category: TransitCategory
    content: bytes
    etag: str
