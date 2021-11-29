from datetime import date, timedelta
from datetime import datetime
from db.jsondb import JSONDataBase
from db.db import CarType
import yaml
from typing import Any
from itertools import combinations
import numpy as np

db = JSONDataBase('data')

def get_cost_date_plot():
    with open('codes.yaml') as f:
        cities: list[dict[str, Any]] = yaml.safe_load(f)

    pairs = list(combinations(map(lambda city: int(city['code']), cities), 2))

    start_date = date(2021, 11, 19)

    days_available = 90

    for car_type in [CarType.COUPE, CarType.PLAZKART, CarType.LUX]:
        # [per day cost dependence]
        per_car_type_cost_dependence = []
        for collect_day in [start_date + timedelta(days=i) for i in range((datetime.today().date() - start_date).days + 1)]:
            # train_no -> {min -> [day]; max -> [day]; avg -> [day]; date_max_cost -> max_cost, date_min_cost -> min_cost}
            per_day_cost_dependence = {}
            for days_to_depart in range(0, days_available + 1):
                try:
                    train_list =\
                        db.get_train_list(collect_day, collect_day + timedelta(days=days_to_depart), city_from, city_to)

                    for train in train_list:
                        for city_from, city_to in pairs:
                            if per_day_cost_dependence.get(train, -1 ) == -1:
                                per_day_cost_dependence.update(\
                                    {train: \
                                        {'min': np.zeros(days_available + 1),\
                                         'max': np.zeros(days_available + 1),\
                                         'avg': np.zeros(days_available + 1)}})
                            costs = db.get_trip_cost(\
                                collect_day, collect_day + timedelta(days=days_to_depart), city_from, city_to, train, car_type)
                            match costs:
                                case min_cost, max_cost, avg_cost:
                                    per_day_cost_dependence[train]['min'][days_to_depart] = min_cost
                                    per_day_cost_dependence[train]['max'][days_to_depart] = max_cost
                                    per_day_cost_dependence[train]['avg'][days_to_depart] = avg_cost
                                case None:
                                    pass
                except RuntimeError as e:
                    print('Runtime error: ' + str(e))
                except Exception as e:
                    print('Another error: ' + str(e))

        #normalize cost on maximum per train
        for train in train_list:
            argmax_cost = np.argmax(per_day_cost_dependence[train]['max'])
            max_cost = per_day_cost_dependence[train]['max'][argmax_cost]

            per_day_cost_dependence[train]['date_max_cost'] = argmax_cost
            per_day_cost_dependence[train]['max_cost'] = max_cost

            argmin_cost = np.argmin(per_day_cost_dependence[train]['max'])
            min_cost = per_day_cost_dependence[train]['max'][argmin_cost]

            per_day_cost_dependence[train]['date_min_cost'] = argmin_cost
            per_day_cost_dependence[train]['min_cost'] = min_cost

            for days_to_depart in range(0, days_available + 1):
                per_day_cost_dependence[train]['min'][days_to_depart] /= max_cost
                per_day_cost_dependence[train]['max'][days_to_depart] /= max_cost
                per_day_cost_dependence[train]['avg'][days_to_depart] /= max_cost
        per_car_type_cost_dependence.append(per_day_cost_dependence)
        


if __name__ == '__main__':
    get_cost_date_plot()