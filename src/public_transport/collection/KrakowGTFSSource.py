import requests

from public_transport.source_interface.GTFSSource import GTFSSource


class KrakowGTFSSource(GTFSSource):

    GTFS_STATIC='https://gtfs.ztp.krakow.pl/GTFS_KRK_A.zip'
    GTFS_TRIP_UPDATES='https://gtfs.ztp.krakow.pl/TripUpdates_A.pb'
    GTFS_ALERTS='https://gtfs.ztp.krakow.pl/ServiceAlerts_A.pb'

    def make_static_request(self):
        return requests.get(self.GTFS_STATIC)

    def make_trip_update_request(self):
        return requests.get(self.GTFS_TRIP_UPDATES)

    def make_alert_request(self):
        return requests.get(self.GTFS_ALERTS)