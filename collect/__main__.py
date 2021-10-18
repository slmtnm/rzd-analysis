from .utils import train_routes, Direction
from .city_codes import get_top100_cities
from asyncio import run

print('Collecting data...')

cities = get_top100_cities()
print(cities)

#routes = run(train_routes(
#    from_code='2004000',
#    where_code='2000000',
#    date='01.01.2022',
#    dir=Direction.ONEWAY,
#    with_transfers=False
#))
#print(routes)