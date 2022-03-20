from public_transport.source_interface.KrakowGTFSSource import KrakowGTFSSource
from public_transport.source_interface.LondonGTFSSource import LondonGTFSSource

krakow = KrakowGTFSSource()

london = LondonGTFSSource()

print('krakow.make_static_request()')
print(krakow.make_static_request())

print('krakow.make_alert_request()')
print(krakow.make_alert_request())

print('krakow.make_trip_update_request()')
print(krakow.make_trip_update_request())


print('london.make_static_request()')
print(london.make_static_request())

print('london.make_alert_request()')
print(london.make_alert_request())

print('london.make_trip_update_request()')
print(london.make_trip_update_request())