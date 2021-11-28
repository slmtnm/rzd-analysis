import json
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
            raise RuntimeError("File " + file_name + " does not exist")

        with open(file_name, 'r') as f:
            data = json.load(f)
            data_mapped = {}

            for train_pair in data:
                for train in train_pair:
                    # Create map: fromCode -> whereCode
                    if data_mapped.get(train['fromCode'], -1) == -1:
                        data_mapped.update({train['fromCode']: {}})

                    # Create map: whereCode -> train
                    #if data_mapped[train['fromCode']].get(train['whereCode'], -1) == -1:
                    data_mapped[train['fromCode']].update({train['whereCode']: train})

            self.__data.update({file_name: data_mapped})
            return data

    def get_trip_cost(self, collect_day: date, departure_day: date, from_code: int, to_code: int, car_type: CarType):
        '''
        returns: min cost, max cost, avg cost
        '''
        data = self.open_json_file(collect_day, departure_day)
        train_list = data[from_code][to_code]['list']

        available_costs = np.array([], dtype=int)
        for train in train_list:
            for car in filter(lambda car: car['type'] == car_type.value, train['cars']):
                available_costs = np.append(available_costs, int(car['tariff']))

        return np.min(available_costs), np.max(available_costs), np.average(available_costs)
