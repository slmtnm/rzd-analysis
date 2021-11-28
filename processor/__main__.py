from datetime import date, timedelta
from datetime import datetime
from db.jsondb import JSONDataBase
from db.db import CarType
import yaml
from typing import Any
from itertools import combinations

db = JSONDataBase('data')

def get_cost_date_plot():
    with open('codes.yaml') as f:
        cities: list[dict[str, Any]] = yaml.safe_load(f)

    pairs = list(combinations(cities, 2))

    start_date = date(2021, 11, 19)

    for car_type in [CarType.COUPE, CarType.PLAZKART, CarType.LUX]:
        min_cost_dependence = {i: [] for i in range(0, 91)}
        max_cost_dependence = {i: [] for i in range(0, 91)}
        avg_cost_dependence = {i: [] for i in range(0, 91)}
        for collect_day in [start_date + i for i in range((datetime.today() - start_date).day)]:
            for days_to_depart in range(0, 91):
                for city_from, city_to in pairs:
                        try:
                            min_cost, max_cost, avg_cost =\
                                db.get_trip_cost(collect_day, collect_day + timedelta(days=days_to_depart), city_from, city_to, car_type)
                            min_cost_dependence[days_to_depart].append(min_cost)
                        except RuntimeError as e:
                            print('get_trip_cost: error while searching file: ' + str(e))
                        except Exception as e:
                            print('get_trip_cost: another error: ' + str(e))