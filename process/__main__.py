from datetime import date, timedelta
from datetime import datetime
from typing import Any
from db.jsondatabase import JSONDatabase
from db.mongodatabase import MongoDatabase
import numpy as np


# db = JSONDatabase('data')
# START_DATE = date(2021, 11, 19)
# DAYS_AVAILABLE = 90


# def _parse_pairs() -> list[tuple[int, int]]:
#     '''Parses file with city codes and returns list of pairs
#        (from_code, where_code)'''
#     pairs: list[tuple[int]] = []
#     with open('codes.txt') as f:
#         for line in f:
#             pair = line.split()
#             pairs.append((int(pair[0]), int(pair[1])))
#     return pairs


# def _process_type(car_type: CarType,
#                   pairs: list[tuple[int, int]]) -> Any:
#     # [per day cost dependence] idx: collect day
#     per_car_type_cost_dependence = []

#     days_passed = (datetime.today().date() - START_DATE).days + 1
#     dates = [START_DATE + timedelta(days=i) for i in range(days_passed)]

#     for collect_day in dates:
#         # train_no -> {min -> [day]; max -> [day]; avg -> [day]};
#         #     max_min_rel -> {train; max_cost, min_cost; max_min_rel}}
#         per_day_cost_dependence = {}
#         for days_to_depart in range(0, DAYS_AVAILABLE + 1):
#             for from_code, where_code in pairs:
#                 try:
#                     train_list = db.get_train_list(
#                         collect_day,
#                         collect_day + timedelta(days=days_to_depart),
#                         from_code,
#                         where_code
#                     )

#                     if train_list is None:
#                         continue

#                     for train in train_list:
#                         # TODO check if this car type exist in
#                         # this train ('carTypes' key)
#                         if not db.train_has_car_type(
#                             collect_day,
#                             collect_day + timedelta(days=days_to_depart),
#                             from_code,
#                             where_code,
#                             train,
#                             car_type
#                         ):
#                             continue

#                         if train not in per_day_cost_dependence:
#                             per_day_cost_dependence[train] = {
#                                 'min': np.zeros(DAYS_AVAILABLE + 1),
#                                 'max': np.zeros(DAYS_AVAILABLE + 1),
#                                 'avg': np.zeros(DAYS_AVAILABLE + 1),
#                             }
#                             per_day_cost_dependence['max_min_rel'] = {
#                                 'train': '',
#                                 'max': 1,
#                                 'min': 1,
#                                 'max_min': 1,
#                             }
#                         costs = db.get_trip_cost(
#                             collect_day,
#                             collect_day + timedelta(days=days_to_depart),
#                             from_code,
#                             where_code,
#                             train,
#                             car_type
#                         )
#                         match costs:
#                             case min_cost, max_cost, avg_cost:
#                                 per_day_cost_dependence[train]['min'][days_to_depart] = min_cost
#                                 per_day_cost_dependence[train]['max'][days_to_depart] = max_cost
#                                 per_day_cost_dependence[train]['avg'][days_to_depart] = avg_cost
#                 except RuntimeError as e:
#                     print('Runtime error: ' + str(e))
#                     # FIXME kostyl
#                     break
#                 except Exception as e:
#                     print('Another error: ' + str(e))

#         # normalize cost on maximum per train
#         for train in per_day_cost_dependence.keys():
#             if train == 'max_min_rel':
#                 continue
#             argmax_cost = np.argmax(per_day_cost_dependence[train]['max'])
#             max_cost = per_day_cost_dependence[train]['max'][argmax_cost]

#             argmin_cost = np.argmin(per_day_cost_dependence[train]['max'])
#             min_cost = per_day_cost_dependence[train]['max'][argmin_cost]

#             if per_day_cost_dependence['max_min_rel']['max_min'] > max_cost / min_cost:
#                 per_day_cost_dependence['max_min_rel'].update(
#                     {
#                         'train': train,
#                         'max': max_cost,
#                         'min': min_cost,
#                         'max_min': max_cost / min_cost
#                     }
#                 )

#             for cost in per_day_cost_dependence[train]['min']:
#                 cost /= max_cost
#                 cost /= max_cost
#                 cost /= max_cost
#         per_car_type_cost_dependence.append(per_day_cost_dependence)

#     per_car_type_cost_dependence.sort(key=lambda per_day_cost_dependence: per_day_cost_dependence['max_min_rel']['max_min'])

#     return {
#         'min_maximum_rel': per_car_type_cost_dependence[0],
#         'max_maximum_rel': per_car_type_cost_dependence[-1],
#         'avg_maximum_rel': per_car_type_cost_dependence[
#             len(per_car_type_cost_dependence // 2)
#         ],
#     }


# def get_cost_date_plot():
#     pairs = _parse_pairs()
#     for car_type in [CarType.COUPE, CarType.PLAZKART,
#                      CarType.LUX, CarType.SEAT]:
#         _process_type(car_type, pairs)


if __name__ == '__main__':
    # get_cost_date_plot()
    db = MongoDatabase('mongodb+srv://rzd:rzd@rzd-analysis.jf5ca.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
    print(db.routes('28.11.2021', '29.12.2021'))
