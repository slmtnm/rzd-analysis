from datetime import date
from pymongo import MongoClient
from database.models import Route
import utils
from .database import Database


class MongoDatabase(Database):
    def __init__(self, mongo_url: str) -> None:
        self._mongodb = MongoClient(mongo_url)['rzd-analysis']

    def routes(self,
               collect_date: date | str,
               departure_date: date | str) -> list[Route]:
        if isinstance(collect_date, str):
            collect_date = utils.Date.from_str(collect_date)

        if isinstance(departure_date, str):
            departure_date = utils.Date.from_str(departure_date)

        collection = self._mongodb[str(collect_date)]

        routes = []
        for route_dict in collection.find({}):
            routes.append(Route.from_dict(route_dict))

        return routes

    def store(self, collect_date: utils.Date,
              routes: list[Route]):
        collection = self._mongodb[str(collect_date)]
        collection.insert_many(map(Route.as_dict, routes))

    def collect_dates(self) -> list[utils.Date]:
        pass

    def deparute_dates(self, collect_date: utils.Date) -> list[utils.Date]:
        pass
