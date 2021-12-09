from datetime import date
from pymongo import MongoClient
from database.models import Route
from utils import date_str, str_date
from .database import Database


class MongoDatabase(Database):
    def __init__(self, mongo_uri: str) -> None:
        self._mongodb = MongoClient(mongo_uri)['rzd-analysis']

    def routes(self,
               collect_date: date | str,
               departure_date: date | str) -> list[Route]:
        if isinstance(collect_date, str):
            collect_date = str_date(collect_date)

        if isinstance(departure_date, str):
            departure_date = str_date(departure_date)

        collection = self._mongodb[date_str(collect_date)]

        routes = []
        for route_dict in collection.find({}):
            routes.append(Route.from_dict(route_dict))

        return routes
