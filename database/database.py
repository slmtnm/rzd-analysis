from datetime import date
from abc import ABCMeta, abstractmethod
from typing import Callable
import utils
from .models import CarType, Route, Train, Car


class Database(metaclass=ABCMeta):
    @abstractmethod
    def routes(self, collect_date: date | str,
               departure_date: date | str) -> list[Route]:
        pass

    @abstractmethod
    def collect_dates(self) -> list[utils.Date]:
        pass

    @abstractmethod
    def deparute_dates(self, collect_date: utils.Date) -> list[utils.Date]:
        pass

    def trains(self,
               collect_date: date,
               departure_date: date,
               from_code: int,
               where_code: int) -> list[Train]:
        '''
        Returns list of trains that go from station with code 'from_code'
        to station with code 'where_code'.

        These trains leave at 'departure_date'
        and collected on 'collect_date'.
        '''
        routes = self.routes(collect_date, departure_date)
        trains = []
        for route in routes:
            if route.from_code == from_code and route.where_code == where_code:
                trains += route.trains
        return trains

    def tariffs(self,
                collect_date: date,
                departure_date: date,
                from_code: int,
                where_code: int,
                car_type: CarType) -> list[int]:
        '''
        Returns list of tariffs for tickets from station with code 'from_code'
        to station with code 'where_code'.

        Trains leave at 'departure_date' and collected on 'collect_date'.

        Cars have type 'car_type'.
        '''
        return self.car_params(lambda car: car.tariff, collect_date,
                               departure_date, from_code, where_code,
                               car_type)

    def seats(self,
              collect_date: date,
              departure_date: date,
              from_code: int,
              where_code: int,
              car_type: CarType) -> list[int]:
        '''
        Returns list of free seats for tickets from station
        with code 'from_code' to station with code 'where_code'.

        Trains leave at 'departure_date' and collected on 'collect_date'.

        Cars have type 'car_type'.
        '''
        return self.car_params(lambda car: car.free_seats, collect_date,
                               departure_date, from_code, where_code,
                               car_type)

    def car_params(self,
                   key: Callable[[Car], int],
                   collect_date: date,
                   departure_date: date,
                   from_code: int,
                   where_code: int,
                   car_type: CarType) -> list[int]:
        routes = self.routes(collect_date, departure_date)
        params = []
        for route in routes:
            if route.from_code != from_code or route.where_code != where_code:
                continue
            for train in route.trains:
                for car in train.cars:
                    if car.type == car_type.value:
                        params.append(key(car))
        return params
