from enum import Enum
from asyncio import sleep

import httpx


TIMETABLE_ADDRESS = 'https://pass.rzd.ru/timetable/public/ru'
SUGGSTION_ADDRESS = 'https://pass.rzd.ru/suggester'
TIMEOUT = 60


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


async def train_routes(*, 
        from_code: str,
        where_code: str,
        date: str,
        dir: Direction = Direction.ROUNDTRIP,
        vehicle: Vehicle = Vehicle.TRAIN,
        check_seats: bool = True,
        with_transfers: bool = True) -> str:
    params: dict[str, int | str] = {
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
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(TIMETABLE_ADDRESS, params=params)
        content = response.json()
        if content['result'] != 'RID':
            raise RuntimeError(f'Invalid response from server:\n{content}')
        params['rid'] = content['RID']

        await sleep(3) # magic sleep
        
        response = await client.get(TIMETABLE_ADDRESS, params=params)
        content = response.json()
        return content['tp']


async def station_code(station_name: str) -> int:
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(SUGGSTION_ADDRESS, params={
            'compatMode': 'y',
            'lang': 'ru',
            'stationNamePart': station_name.upper(),
        })

        if not response.content:
            raise ValueError(
                f'Empty reply from server (possibly invalid station name')

        codes = [s['c'] for s in response.json()
            if s['n'] == station_name.upper()]
        match codes:
            case [code]:
                return code
            case []:
                raise ValueError(f'Could not find station name')
            case _:
                raise RuntimeError(f'Invalid response from server:\n{codes}')
