from .utils import train_routes, Direction


print('Collecting data...')
routes = train_routes(
    departure_station_code='2004000',
    destination_station_code='2000000',
    date='01.01.2022',
    dir=Direction.ONEWAY,
    with_transfers=False
)
print(routes)
print('Done!')