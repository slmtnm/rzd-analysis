from pathlib import Path
from pymongo import MongoClient, database
from db.jsondatabase import JSONDatabase
import sys
from utils import str_date


USAGE = f'{sys.argv[0]} <mongodb-url> <path to json database>'


def structured(jsondb_path: str, mongodb: database.Database):
    jsondb = JSONDatabase(Path(jsondb_path))

    for collect_date in jsondb.collect_dates():
        collection = mongodb[collect_date]
        if collection.count_documents({}) != 0:
            continue

        routes_dicts = []
        for departure_date in jsondb.deparute_dates(str_date(collect_date)):
            routes = jsondb.routes(collect_date, departure_date)
            routes_dicts += [r.as_dict() for r in routes]

        collection.insert_many([r.as_dict() for r in routes])
        print(f'filled collection {collection.name}')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(USAGE, file=sys.stderr)
        exit(1)
    connstring = sys.argv[1]
    jsondb_path = sys.argv[2]

    client = MongoClient(connstring)
    mongodb = client['rzd-analysis']
    dbname = structured(jsondb_path, mongodb)
