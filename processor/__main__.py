from datetime import date, timedelta
from datetime import datetime
from db.jsondb import JSONDataBase
from db.db import CarType
import yaml
from typing import Any
from itertools import combinations
import numpy as np
import matplotlib.pyplot as plt

db = JSONDataBase('data')

def get_cost_date_plot():
    with open('codes.yaml') as f:
        cities: list[dict[str, Any]] = yaml.safe_load(f)

    pairs = list(combinations(map(lambda city: int(city['code']), cities), 2))

    start_date = date(2021, 11, 19)

    days_available = 90

    result = set()
    
    for car_type in [CarType.COUPE, CarType.PLAZKART, CarType.LUX, CarType.SEAT]:
        # [per day cost dependence] idx: collect day
        per_car_type_cost_dependence = []
        for collect_day in [start_date + timedelta(days=i) for i in range((datetime.today().date() - start_date).days + 1)]:
            # train_no -> {min -> [day]; max -> [day]; avg -> [day]};
            #     max_min_rel -> {train; max_cost, min_cost; max_min_rel}}
            per_day_cost_dependence = {}
            for days_to_depart in range(0, days_available + 1):
                for city_from, city_to in pairs:
                    try:
                        train_list =\
                            db.get_train_list(collect_day, collect_day + timedelta(days=days_to_depart), city_from, city_to)

                        if train_list is None:
                            continue

                        for train in train_list:
                            if not db.train_has_car_type(\
                                collect_day, collect_day + timedelta(days=days_to_depart), city_from, city_to, train, car_type):
                                continue
                            if per_day_cost_dependence.get(train, -1) == -1:
                                per_day_cost_dependence.update(\
                                    {
                                        train: 
                                            {
                                                'min': np.ones(days_available + 1),
                                                'max': np.ones(days_available + 1),
                                                'avg': np.ones(days_available + 1)
                                            },
                                        'max_min_rel': {'train': '', 'max': 1, 'min': 1, 'max_min': 1}
                                    })
                            costs = db.get_trip_cost(\
                                collect_day, collect_day + timedelta(days=days_to_depart), city_from, city_to, train, car_type)
                            match costs:
                                case min_cost, max_cost, avg_cost:
                                    per_day_cost_dependence[train]['min'][days_to_depart] = min_cost
                                    per_day_cost_dependence[train]['max'][days_to_depart] = max_cost
                                    per_day_cost_dependence[train]['avg'][days_to_depart] = avg_cost
                                case None:
                                    pass
                    except FileExistsError as e:
                        print('File not exists error: ' + str(e))
                        break
                    except RuntimeError as e:
                        print('Runtime error: ' + str(e))
                    except Exception as e:
                        print('Another error: ' + str(e))

            #normalize cost on maximum per train
            for train in per_day_cost_dependence.keys():
                if train == 'max_min_rel':
                    continue
                argmax_cost = np.argmax(per_day_cost_dependence[train]['max'])
                max_cost = per_day_cost_dependence[train]['max'][argmax_cost]

                argmin_cost = np.argmin(per_day_cost_dependence[train]['min'])
                min_cost = per_day_cost_dependence[train]['min'][argmin_cost]

                if per_day_cost_dependence['max_min_rel']['max_min'] > max_cost / min_cost:
                    per_day_cost_dependence['max_min_rel'].update(
                        {
                            'train': train,
                            'max': max_cost,
                            'min': min_cost,
                            'max_min': max_cost / min_cost
                        }
                    )

                for i in range(len(per_day_cost_dependence[train]['min'])):
                    per_day_cost_dependence[train]['max'][i] /= max_cost
                    per_day_cost_dependence[train]['min'][i] /= max_cost
                    per_day_cost_dependence[train]['avg'][i] /= max_cost

            per_car_type_cost_dependence.append(per_day_cost_dependence)

        per_car_type_cost_dependence.sort(key=lambda per_day_cost_dependence: per_day_cost_dependence['max_min_rel']['max_min'])
        result[car_type]['min_maxmin_rel'] = per_car_type_cost_dependence[0]
        result[car_type]['max_maxmin_rel'] = per_car_type_cost_dependence[-1]
        result[car_type]['avg_maxmin_rel'] = per_car_type_cost_dependence[len(per_car_type_cost_dependence) // 2]
    return result
        


if __name__ == '__main__':
    result = get_cost_date_plot()

    x = np.linspace(0, 91)
    for car_type in [CarType.SEAT, CarType.COUPE, CarType.PLAZKART, CarType.LUX]:
        plt.plot(x, result[car_type]['min_maxmin_rel'])
        plt.plot(x, result[car_type]['max_maxmin_rel'])
        plt.plot(x, result[car_type]['avg_maxmin_rel'])
