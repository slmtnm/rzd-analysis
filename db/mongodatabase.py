from datetime import date
from typing import Callable
import numpy as np
from pymongo import MongoClient
from db.statistic import Statistic
from utils import date_str, str_date

from db.models import Car, Route, Train
from .database import Database


class MongoDatabase(Database):
    def __init__(self, mongo_uri: str) -> None:
        self._mongodb = MongoClient(mongo_uri)['rzd-analysis']

    def routes(self,
               collect_date: date | str,
               departure_date: date | str) -> list[Route]:
        '''Returns list of available routes on departure_day,
           which is collected on collect_day'''
        if isinstance(collect_date, str):
            collect_date = str_date(collect_date)

        if isinstance(departure_date, str):
            departure_date = str_date(departure_date)

        collection = self._mongodb[date_str(collect_date)]

        routes = []
        for route_dict in collection.find({}):
            routes.append(Route.from_dict(route_dict))

        return routes

    def train_list(self,
                   collect_day: date,
                   departure_day: date,
                   from_code: int,
                   where_code: int) -> list[Train]:
        collection = self._mongodb[date_str(collect_day)]
        trains = []
        for route_dict in collection.find({
            'date': date_str(departure_day),
            'from_code': from_code,
            'where_code': where_code,
        }):
            trains.append(Train.from_dict(route_dict['trains']))

        return trains

    def trip_cost(self,
                  collect_day: date,
                  departure_day: date,
                  from_code: int,
                  where_code: int,
                  train_number: str,
                  car_type: str) -> tuple[float, float, float] | None:
        collection = self._mongodb[date_str(collect_day)]
        costs = np.array([], dtype=int)

        for route_dict in collection.find({
            'date': date_str(departure_day),
            'from_code': from_code,
            'where_code': where_code,
        }):
            trains = [
                Train.from_dict(t)
                for t in route_dict['trains']
                if t['number'] == train_number
            ]

            for train in trains:
                for car in train.cars:
                    if car.tariff == car_type:
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
