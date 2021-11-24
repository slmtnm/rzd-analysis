from datetime import date
from db.jsondb import JSONDataBase

db = JSONDataBase('../data')
db.get_trip_cost(date(2021, 11, 24), date(2022, 1, 2))