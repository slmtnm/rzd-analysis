import json
from db.db import DataBase
from datetime import date
from pathlib import Path

class JSONDataBase(DataBase):
    def __init__(self, path_to_db: str):
        self.__path_to_db = path_to_db
        self.__data = {}

    def __get_file_name(self, today: date, departure_day: date):
        return Path.cwd() / self.__path_to_db / today.isoformat() / departure_day.isoformat() + '.json'

    def __open_json_file(self, today: date, departure_day: date):
        file_name = self.__get_file_name(today, departure_day)

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

