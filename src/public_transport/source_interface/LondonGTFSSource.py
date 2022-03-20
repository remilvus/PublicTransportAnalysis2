import requests

from public_transport.source_interface.GTFSSource import GTFSSource


class LondonGTFSSource(GTFSSource):

    GTFS_STATIC='https://www.londontransit.ca/gtfsfeed/google_transit.zip'
    GTFS_TRIP_UPDATES='http://gtfs.ltconline.ca/TripUpdate/TripUpdates.pb'
    GTFS_ALERTS='http://gtfs.ltconline.ca/Alert/Alerts.pb'

    def make_static_request(self):
        return requests.get(self.GTFS_STATIC)

    def make_trip_update_request(self):
        return requests.get(self.GTFS_TRIP_UPDATES)

    def make_alert_request(self):
        return requests.get(self.GTFS_ALERTS)