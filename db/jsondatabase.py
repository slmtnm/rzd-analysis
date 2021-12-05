import json
from datetime import date
from typing import Callable
from .statistic import Statistic
import numpy as np
import os
from .database import Database
from pathlib import Path
from .models import Car, Route, Train
from functools import lru_cache
from utils import date_str, str_date


class JSONDatabase(Database):
    def __init__(self, path: Path):
        self._path = path

    def available_collect_dates(self) -> list[str]:
        dates = []
        for date_dirname in os.listdir(self._path):
            if (self._path / date_dirname).is_dir():
                dates.append(date_dirname)
        return dates

    def available_deparute_dates(self, collect_date: date | str) -> list[str]:
        if isinstance(collect_date, date):
            collect_date = date_str(collect_date)
        return [
            file.rstrip('.json')
            for file in os.listdir(self._path / collect_date)
        ]

    @lru_cache
    def routes(self,
               collect_date: date | str,
               departure_date: date | str) -> list[Route]:
        if isinstance(collect_date, str):
            collect_date = str_date(collect_date)

        if isinstance(departure_date, str):
            departure_date = str_date(departure_date)

        file = (self._path /
                date_str(collect_date) /
                f"{date_str(departure_date)}.json")

        if not file.is_file():
            raise ValueError(f'File {file} does not exist')

        with open(file, 'r') as f:
            root = json.load(f)

        routes: list[Route] = []
        for route in root:
            if isinstance(route, list):
                inner_routes = route
            else:
                inner_routes = [route]

            for route in inner_routes:
                if 'list' not in route or len(route['list']) == 0:
                    continue

                trains: list[Train] = []
                for train in route['list']:
                    if 'cars' not in train or len(train['cars']) == 0:
                        continue

                    cars = []
                    for car in train['cars']:
                        cars.append(Car(tariff=car['tariff'],
                                        type=car['type'],
                                        type_loc=car['typeLoc'],
                                        free_seats=car['freeSeats']))

                    if 'seatCars' in train:
                        for car in train['seatCars']:
                            cars.append(Car(tariff=car['tariff'],
                                            type=car['type'],
                                            type_loc=car['typeLoc'],
                                            free_seats=car['freeSeats']))

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

    def train_list(self,
                   collect_date: date,
                   departure_date: date,
                   from_code: int,
                   where_code: int) -> list[Train]:
        routes = self.routes(collect_date, departure_date)

        trains = []
        for route in routes:
            if route.from_code == from_code and route.where_code == where_code:
                trains += route.trains

        return trains

    def trip_cost(self,
                  collect_date: date,
                  departure_date: date,
                  from_code: int,
                  where_code: int,
                  train_number: str,
                  car_type: str) -> tuple[float, float, float] | None:
        trains = self.train_list(collect_date, departure_date,
                                 from_code, where_code)

        costs = np.array([], dtype=int)
        for train in trains:
            if train.number == train_number:
                for car in train.cars:
                    if car.type == car_type:
                        costs = np.append(costs, car.tariff)

        if not costs:
            return None

        return (np.min(costs),
                np.max(costs),
                np.average(costs))

    def timeseries(self,
                   stat: Statistic,
                   from_code: int,
                   where_code: int,
                   car_key: Callable[[Car], int]) -> list[tuple[int, date]]:
        '''Returns timeseries of specific metric (min, max, avg)
           for key defined as function: car -> metrics
           for given pair of station codes'''
        ts: list[tuple[int, date]] = []
        return ts
