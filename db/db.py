from enum import Enum
from datetime import date

class CarType(Enum):
    COUPE = 'Купе'
    PLAZKART = 'Плац'
    LUX = 'Люкс'

class DataBase:
    def get_trip_cost(self, collect_day: date, departure_day: date, from_code: int, to_code: int, train: str, car_type: CarType):
        pass

    def get_train_list(self, collect_day: date, departure_day: date, from_code: int, to_code: int):
        pass
