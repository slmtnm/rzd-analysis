from .utils import train_routes, Direction
from .city_codes import get_top_cities, get_top_city_codes
from asyncio import run

print('Collecting data...')

with open("city.html") as f:
    cities = get_top_cities(f)
    codes = run(get_top_city_codes(cities))

#routes = run(train_routes(
#    from_code='2004000',
#    where_code='2000000',
#    date='01.01.2022',
#    dir=Direction.ONEWAY,
#    with_transfers=False
#))
#print(routes)