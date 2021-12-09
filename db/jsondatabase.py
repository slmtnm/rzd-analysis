import json
from datetime import date
import os
from .database import Database
from pathlib import Path
from .models import Car, Route, Train
from functools import lru_cache
from utils import date_str, str_date


class JSONDatabase(Database):
    def __init__(self, path: Path):
        self._path = path

    def collect_dates(self) -> list[date]:
        return [
            str_date(dirname)
            for dirname in os.listdir(self._path)
            if (self._path / dirname).is_dir()
        ]

    def deparute_dates(self, collect_date: date) -> list[date]:
        return [
            str_date(file.rstrip('.json'))
            for file in os.listdir(self._path / date_str(collect_date)) if Path(file).suffix == '.json'\
                and 'spbmsk' not in file
        ]

    @lru_cache
    def routes(self,
               collect_date: date,
               departure_date: date) -> list[Route]:
        file = (self._path / date_str(collect_date) /
                f"{date_str(departure_date)}.json")

        if not file.is_file():
            raise ValueError(f'File {file} does not exist')

        with open(file, 'r') as f:
            root = json.load(f)

        routes: list[Route] = []
        for route in root:
            inner_routes = route if isinstance(route, list) else [route]
            for route in inner_routes:
                if 'list' not in route or not route['list']:
                    continue

                trains: list[Train] = []
                for train in route['list']:
                    if 'cars' not in train or not train['cars']:
                        continue

                    cars = []
                    for car in train['cars'] + train.get('seatCars', []):
                        cars.append(Car(tariff=int(car['tariff']),
                                        type=car['type'],
                                        type_loc=car['typeLoc'],
                                        free_seats=int(car['freeSeats'])))
                    trains.append(Train(from_code=int(train['code0']),
                                        where_code=int(train['code1']),
                                        start_date=str_date(train['date0']),
                                        finish_date=str_date(train['date1']),
                                        number=train['number'],
                                        cars=cars))
                routes.append(Route(from_code=route['fromCode'],
                                    where_code=route['whereCode'],
                                    trains=trains,
                                    date=str_date(route['date'])))
        return routes
