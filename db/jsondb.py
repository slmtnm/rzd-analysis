import json
from db.db import DataBase
from datetime import date
from pathlib import Path
from utils import dmy_from_date

class JSONDataBase(DataBase):
    def __init__(self, path_to_db: str):
        self.__path_to_db = path_to_db
        self.__data = {}

    def get_file_name(self, collect_day: date, departure_day: date):
        return Path.cwd() / self.__path_to_db / dmy_from_date(collect_day) / (dmy_from_date(departure_day) + '.json')

    def open_json_file(self, today: date, departure_day: date):
        file_name = self.get_file_name(today, departure_day)

        if self.__data.get(file_name, -1) != -1:
            return self.__data[file_name]

        file = Path(file_name)

        if not file.is_file():
            raise RuntimeError("File " + file_name + " does not exist")

        with open(file_name, 'r') as f:
            data = json.load(f)
            self.__data.update({file_name: data})
            return data

    def get_trip_cost(self, today: date, departure_day: date, from_code: int, to_code: int, car_type):
        '''
        returns: min cost, max cost, avg cost
        '''
        try:
            data = self.__open_json_file(today, departure_day)
            print(data[0])
        except RuntimeError as e:
            print('get_trip_cost: error while searching file: ' + str(e))
        except:
            print('get_trip_cost: error')

