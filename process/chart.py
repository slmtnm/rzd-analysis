from dataclasses import dataclass
from datetime import date
from typing import Callable
from database.database import Database
from database.models import Car, CarType
import matplotlib.pyplot as plt


@dataclass
class Chart:
    '''Chart class represent relation of some statistic
       to number of days before departure.

       'points' - list of tuple (days_before_departure, statistic).
       'date' - date of departure.
       '''
    points: list[tuple[int, float]]

    date: date
    from_code: int
    where_code: int


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

    #if len(before_dates) < 7:
    #    raise ValueError(f'Fewer than 7 collect dates before {departure_date}')

    points = []
    for before_date in before_dates:
        if departure_date not in db.deparute_dates(before_date):
            continue
        tariffs = db.car_params(car_key, before_date, departure_date,
                                from_code, where_code, car_type)
        if tariffs:
            points.append(((departure_date - before_date).days,
                           statistic(tariffs)))

    return Chart(points, departure_date, from_code, where_code)


def plot( chart: Chart, title: str ):
    x = [int(-val[0]) for val in chart.points]                 
    y = [float(val[1]) for val in chart.points]               
    plt.plot(x, y, 'o-')
    plt.xlabel('Количество дней до отправления')
    plt.ylabel('Стоимость билета')
    plt.title(title)
    plt.xticks(x, [int(-val) for val in x])
    plt.show()
