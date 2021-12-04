import json
from typing import Any
import numpy as np
from datetime import date
from db.db import DataBase, CarType
from pathlib import Path
from utils import dmy_from_date
from functools import lru_cache


class JSONDataBase(DataBase):
    def __init__(self, path_to_db: str):
        self.__path_to_db = path_to_db
        self.__data: dict[Path, Any] = {}

    def get_file_path(self, collect_day: date, departure_day: date) -> Path:
        return (Path.cwd() /
                self.__path_to_db /
                dmy_from_date(collect_day) /
                (dmy_from_date(departure_day) + '.json'))

    @lru_cache
    def open_json_file(self, collect_day: date, departure_day: date):
        '''Returns mapping from "from_code" to
           mapping from "where_code" to trains
        '''
        file = self.get_file_path(collect_day, departure_day)

        if not file.is_file():
            raise RuntimeError(f"File {file} does not exist")

        with open(file, 'r') as f:
            root = json.load(f)

        data_mapped: dict[str | int, Any] = {}
        for train_pair in root:
            for trains in train_pair:
                for train in trains['list']:
                    # Create list of car types:
                    cars = train['cars'] + train.get('seatCars', [])
                    car_type_list = {car['type'] for car in cars}
                    train.update({'car_type_list': car_type_list})

                # Create map: fromCode -> whereCode
                from_code = int(trains['fromCode'])
                if from_code not in data_mapped:
                    data_mapped[from_code] = {}

                # Create map: whereCode -> train
                data_mapped[from_code].update({
                    int(trains['whereCode']): trains
                })
        return data_mapped

    def get_trip_cost(self,
                      collect_day: date,
                      departure_day: date,
                      from_code: int,
                      to_code: int,
                      train_number: str,
                      car_type: CarType):
        '''
        Returns: min cost, max cost, avg cost
        Returns None if no such trains found
        '''
        data = self.open_json_file(collect_day, departure_day)

        if from_code not in data or to_code not in data[from_code]:
            return None

        train_list = data[from_code][to_code]['list']

        available_costs: np.ndarray = np.array([], dtype=int)

        trains = (t for t in train_list if t['number'] == train_number)
        for train in trains:
            cars = train['cars']
            cars += train.get('seatCars', [])

            for car in cars:
                if car['type'] == car_type.value:
                    available_costs = np.append(available_costs,
                                                int(car['tariff']))

        if available_costs.size == 0:
            return None

        return (np.min(available_costs),
                np.max(available_costs),
                np.average(available_costs))

    def train_has_car_type(self,
                           collect_day: date,
                           departure_day: date,
                           from_code: int,
                           to_code: int,
                           train_number: str,
                           car_type: CarType):
        data = self.open_json_file(collect_day, departure_day)

        if from_code not in data or to_code not in data[from_code]:
            return None

        train_list = data[from_code][to_code]['list']
        train = [t for t in train_list if t['number'] == train_number]

        if len(train) != 1:
            raise RuntimeError(f"Train was not found \
                or trains were repeated: {len(train)} trains found")

        return car_type.value in train[0]['car_type_list']

    def get_train_list(self,
                       collect_day: date,
                       departure_day: date,
                       from_code: int,
                       to_code: int):
        data = self.open_json_file(collect_day, departure_day)

        if from_code not in data or to_code not in data[from_code]:
            return None

        train_list = data[from_code][to_code]['list']
        # return [train['number'] for train in train_list]
        return map(lambda train: train['number'], train_list)
