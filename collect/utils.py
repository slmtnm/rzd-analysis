import httpx
from enum import Enum
from fake_useragent import UserAgent


TIMETABLE_ADDRESS = 'https://pass.rzd.ru/timetable/public/ru'
SUGGSTION_ADDRESS = 'https://pass.rzd.ru/suggester'


class Direction(Enum):
    ONEWAY = 0
    ROUNDTRIP = 1


class Vehicle(Enum):
    TRAIN = 1
    ELECTRIC = 2
    TRAIN_AND_ELECTRIC = 3


class Layer(Enum):
    '''Request category

    * ROUTE_SELECTION - get list of trains
    * TRAIN_INFO - get detailed info about train and list of it's vans
    * ROUTE_INFO - get route info with all stopovers
    '''
    ROUTE_SELECTION = 5827
    TRAIN_INFO = 5764
    ROUTE_INFO = 5804


def train_routes(*, 
        departure_station_code: str,
        destination_station_code: str,
        date: str,
        dir: Direction = Direction.ROUNDTRIP,
        vehicle: Vehicle = Vehicle.TRAIN,
        check_seats: bool = True,
        with_transfers: bool = True) -> str:
    ''''''
    params={
        'layer_id': Layer.ROUTE_SELECTION.value,
        'dir': dir.value,
        'tfl': vehicle.value,
        'checkSeats': int(check_seats),
        'code0': departure_station_code,
        'code1': destination_station_code,
        'dt0': date,
        'md': int(with_transfers)
    }
    if not check_seats:
        params['withoutSeats'] = 0
    
    with httpx.Client() as client:
        result = client.get(TIMETABLE_ADDRESS, params=params).json()
        if result['result'] != 'RID':
            raise RuntimeError(f'Invalid response from server\n{result}')
        
        rid: int = result['RID']
        params = {
            'layer_id': Layer.ROUTE_SELECTION.value,
            'rid': str(rid),
        }
        u = UserAgent(cache=False).chrome
        return client.get(TIMETABLE_ADDRESS, params=params, headers={
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.5',
            'User-Agent': u,
            'Host': 'pass.rzd.ru',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
        }).json()