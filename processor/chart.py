from dataclasses import dataclass
from datetime import date
from typing import Callable
from db.database import Database
from db.models import Car, CarType


@dataclass
class Chart:
    '''Chart class represent relation of some statistic
       to number of days before departure.

       'points' - list of tuple (days_before_departure, statistic).
       'date' - date of departure.
       '''
    points: list[tuple[int, float]]
    date: date


def create_chart(
        db: Database,
        departure_date: date,
        from_code: int,
        where_code: int,
        car_type: CarType,
        car_key: Callable[[Car], int],
        statistic: Callable[[list[int]], float]) -> Chart:
    collect_dates = sorted(db.collect_dates())
    before_dates = [d for d in collect_dates if d < departure_date]

    if len(before_dates) < 7:
        raise ValueError(f'Fewer than 7 collect dates before {departure_date}')

    points = []
    for before_date in before_dates:
        if departure_date not in db.deparute_dates(before_date):
            continue
        tariffs = db.car_params(car_key, before_date, departure_date,
                                from_code, where_code, car_type)
        if tariffs:
            points.append(((departure_date - before_date).days,
                           statistic(tariffs)))

    return Chart(points, departure_date)
