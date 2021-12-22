import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import utils

from .database import Database
from .models import Car, Route, Train


class JSONDatabase(Database):
    """
    Implementation of database that reads/stores data from local folder

    Structure of that folder ("database") is following:
    <collect-date1>
      <departure-date1>.json
      <departure-date2>.json
      <departure-date3>.json
      ...
    <collect-date2>
      <departure-date1>.json
      <departure-date2>.json
      <departure-date3>.json
      ...
    ...
    """

    def __init__(self, data_dir: str):
        self._path = Path(data_dir)

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

    def store(self, collect_date: utils.Date,
              departure_date: utils.Date, routes: list[Any]):
        dir = self._path / str(utils.Date.today())
        fname = str(departure_date) + '.json'

        if not dir.exists():
            dir.mkdir(parents=True)

        with open(dir / fname, 'w') as f:
            json.dump(routes, f)

    @lru_cache
    def routes(self, collect_date: utils.Date,
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
