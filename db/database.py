from datetime import date
from abc import ABCMeta, abstractmethod
from .models import Route, Train


class Database(metaclass=ABCMeta):
    @abstractmethod
    def routes(self, collect_date: date | str,
               departure_date: date | str) -> list[Route]:
        pass

    @abstractmethod
    def train_list(self,
                   collect_date: date,
                   departure_date: date,
                   from_code: int,
                   where_code: int) -> list[Train]:
        pass

    @abstractmethod
    def trip_cost(self,
                  collect_date: date,
                  departure_date: date,
                  from_code: int,
                  where_code: int,
                  train_number: str,
                  car_type: str) -> tuple[float, float, float] | None:
        pass
