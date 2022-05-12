"""Downloading GTFS files - constants and utilities."""
from dataclasses import dataclass
from typing import Dict, Optional

import requests

from . import data


@dataclass(frozen=True)
class TransitUrls:
    """Urls from which static and real-time GTFS files can be downloaded."""

    static: str
    vehicle_positions: str
    trip_updates: str
    alerts: str

    def __iter__(self):
        return iter(
            [self.static, self.vehicle_positions, self.trip_updates, self.alerts]
        )

    def __getitem__(self, category: data.TransitCategory):
        return {
            data.TransitCategory.static: self.static,
            data.TransitCategory.vehicle_position: self.vehicle_positions,
            data.TransitCategory.trip_update: self.trip_updates,
            data.TransitCategory.alert: self.alerts,
        }[category]


class TransitDownloader:
    """Utility for downloading GTFS files in a controlled way.

    GTFS files are downloaded only when their etags change.
    """

    def __init__(self, links: TransitUrls):
        self.links = links
        self._etags: Dict[data.TransitCategory, str] = {
            category: "" for category in data.TransitCategory
        }

    def get_file(self, category: data.TransitCategory):
        """Download GTFS file of type `category`."""
        return self._get_with_etag(url=self.links[category], category=category)

    def _get_with_etag(
        self, url: str, category: data.TransitCategory
    ) -> Optional[data.TransitFile]:
        """Download a file of type `category` and update it's etag."""
        etag = self._etags[category]
        response = requests.get(
            url,
            headers={"If-None-Match": etag},
        )
        if response.status_code == 200:
            file = data.TransitFile(
                content=response.content,
                category=category,
                etag=response.headers["etag"],
            )
            self._etags[category] = file.etag
            return file
        elif response.status_code == 304:  # resource didn't change
            return None
        else:
            raise RuntimeError(
                f"Failed to fetch resource `{url}`!!! Status code: {response.status_code}"
            )


LINKS_BUS_CRACOW = TransitUrls(
    static="https://gtfs.ztp.krakow.pl/GTFS_KRK_A.zip",
    vehicle_positions="https://gtfs.ztp.krakow.pl/VehiclePositions_A.pb",
    trip_updates="https://gtfs.ztp.krakow.pl/TripUpdates_A.pb",
    alerts="https://gtfs.ztp.krakow.pl/ServiceAlerts_A.pb",
)
LINKS_TRAM_CRACOW = TransitUrls(
    static="https://gtfs.ztp.krakow.pl/GTFS_KRK_T.zip",
    vehicle_positions="https://gtfs.ztp.krakow.pl/VehiclePositions_T.pb",
    trip_updates="https://gtfs.ztp.krakow.pl/TripUpdates_T.pb",
    alerts="https://gtfs.ztp.krakow.pl/ServiceAlerts_T.pb",
)
LINKS_LONDON = TransitUrls(
    static="https://www.londontransit.ca/gtfsfeed/google_transit.zip",
    vehicle_positions="http://gtfs.ltconline.ca/Vehicle/VehiclePositions.pb",
    trip_updates="http://gtfs.ltconline.ca/TripUpdate/TripUpdates.pb",
    alerts="http://gtfs.ltconline.ca/Alert/Alerts.pb",
)
