from enum import Enum
from time import sleep

import httpx


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
        from_code: str,
        where_code: str,
        date: str,
        dir: Direction = Direction.ROUNDTRIP,
        vehicle: Vehicle = Vehicle.TRAIN,
        check_seats: bool = True,
        with_transfers: bool = True) -> str:
    params: dict[str, int | str] ={
        'layer_id': Layer.ROUTE_SELECTION.value,
        'dir': dir.value,
        'tfl': vehicle.value,
        'checkSeats': int(check_seats),
        'code0': from_code,
        'code1': where_code,
        'dt0': date,
        'md': int(with_transfers)
    }
    if not check_seats:
        params['withoutSeats'] = 0
    
    with httpx.Client() as client:
        result = client.get(TIMETABLE_ADDRESS, params=params).json()
        if result['result'] != 'RID':
            raise RuntimeError(f'Invalid response from server:\n{result}')
        params['rid'] = result['RID']

        sleep(3) # magic sleep
        
        return client.get(TIMETABLE_ADDRESS, params=params).json()['tp']
