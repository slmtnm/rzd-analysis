import json
import os
from .database import Database
from pathlib import Path
from .models import Car, Route, Train
from functools import lru_cache
import utils


class JSONDatabase(Database):
    def __init__(self, path: Path):
        self._path = path

    def collect_dates(self) -> list[utils.Date]:
        return [
            utils.Date.from_str(dirname)
            for dirname in os.listdir(self._path)
            if (self._path / dirname).is_dir()
        ]

    def deparute_dates(self, collect_date: utils.Date) -> list[utils.Date]:
        return [
            utils.Date.from_str(file.rstrip('.json'))
            for file in os.listdir(self._path / str(collect_date))
        ]

    @lru_cache
    def routes(self,
               collect_date: utils.Date,
               departure_date: utils.Date) -> list[Route]:
        file = (self._path / str(collect_date) /
                f"{str(departure_date)}.json")

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
                                        start_date=utils.Date.from_str(
                                            train['date0']),
                                        finish_date=utils.Date.from_str(
                                            train['date1']),
                                        number=train['number'],
                                        cars=cars))
                routes.append(Route(from_code=route['fromCode'],
                                    where_code=route['whereCode'],
                                    trains=trains,
                                    date=utils.Date.from_str(route['date'])))
        return routes
