import json
from typing import overload
import numpy as np
from datetime import date
from db.db import DataBase, CarType
from pathlib import Path
from utils import dmy_from_date

class JSONDataBase(DataBase):
    def __init__(self, path_to_db: str):
        self.__path_to_db = path_to_db
        self.__data = {}

    def get_file_name(self, collect_day: date, departure_day: date):
        return Path.cwd() / self.__path_to_db / dmy_from_date(collect_day) / (dmy_from_date(departure_day) + '.json')

    def open_json_file(self, collect_day: date, departure_day: date):
        file_name = self.get_file_name(collect_day, departure_day)

        if self.__data.get(file_name, -1) != -1:
            return self.__data[file_name]

        file = Path(file_name)

        if not file.is_file():
            raise RuntimeError("File " + str(file_name) + " does not exist")

        with open(file_name, 'r') as f:
            data = json.load(f)
            data_mapped = {}

            for train_pair in data:
                for trains in train_pair:
                    for train in trains['list']:
                        # Create list of car types:
                        cars = train['cars'] + (train['seatCars'] if train.get('seatCars', -1) != -1 else [])
                        car_type_list = set(map(lambda car: car['type'], cars))
                        train.update({'car_type_list': car_type_list})

                    # Create map: fromCode -> whereCode
                    from_code = int(trains['fromCode'])
                    if data_mapped.get(from_code, -1) == -1:
                        data_mapped.update({from_code: {}})

                    # Create map: whereCode -> train
                    #if data_mapped[train['fromCode']].get(train['whereCode'], -1) == -1:
                    data_mapped[from_code].update({int(trains['whereCode']): trains})

            self.__data.update({file_name: data_mapped})
            return data_mapped

    def get_trip_cost(self, collect_day: date, departure_day: date, from_code: int, to_code: int, train_number: str, car_type: CarType):
        '''
        returns: min cost, max cost, avg cost
        '''
        data = self.open_json_file(collect_day, departure_day)

        if data.get(from_code, -1) == -1:
            return None

        if data[from_code].get(to_code, -1) == -1:
            return None

        train_list = data[from_code][to_code]['list']

        available_costs: np.array = np.array([], dtype=int)
        trains = filter(lambda train: train['number'] == train_number, train_list)
        for train in trains:
            cars = train['cars']
            if train.get('seatCars', -1) != -1:
                cars += train['seatCars']
            for car in filter(lambda car: car['type'] == car_type.value, cars):
                available_costs = np.append(available_costs, int(car['tariff']))

        if available_costs.size == 0:
            return None 
        return np.min(available_costs), np.max(available_costs), np.average(available_costs)

    def train_has_car_type(self, collect_day: date, departure_day: date, from_code: int, to_code: int, train_number: str, car_type: CarType):
        data = self.open_json_file(collect_day, departure_day)

        if data.get(from_code, -1) == -1:
            return None

        if data[from_code].get(to_code, -1) == -1:
            return None

        train_list = data[from_code][to_code]['list']
        train = list(filter(lambda train: train['number'] == train_number, train_list))
        if len(train) != 1:
            raise RuntimeError(f"Train was not found or trains were repeated: {len(train)} trains found")

        return car_type.value in train[0]['car_type_list']


    def get_train_list(self, collect_day: date, departure_day: date, from_code: int, to_code: int):
        data = self.open_json_file(collect_day, departure_day)

        if data.get(from_code, -1) == -1:
            return None

        if data[from_code].get(to_code, -1) == -1:
            return None

        train_list = data[from_code][to_code]['list']
        #return [train['number'] for train in train_list]
        return map(lambda train: train['number'], train_list)