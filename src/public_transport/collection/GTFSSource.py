from abc import ABC, abstractmethod

class GTFSSource(ABC):

    @abstractmethod
    def make_static_request(self):
        pass

    @abstractmethod
    def make_trip_update_request(self):
        pass

    @abstractmethod
    def make_alert_request(self):
        pass