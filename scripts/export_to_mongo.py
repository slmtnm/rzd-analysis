import sys
from pathlib import Path

sys.path.append(str((Path.cwd() / sys.argv[0]).parent.parent))

import argparse
import sys
from pathlib import Path

from database.jsondatabase import JSONDatabase
from database.mongodatabase import MongoDatabase


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--mongodb_url', required=True)
    parser.add_argument('data_dir', help='Path to data directory')

    return parser.parse_args()


def main():
    args = parse_args()
    jsondb = JSONDatabase(args.data_dir)
    mongodb = MongoDatabase(args.mongodb_url)

    for collect_date in jsondb.collect_dates():
        routes = []
        for departure_date in jsondb.deparute_dates(collect_date):
            routes.extend(jsondb.routes(collect_date, departure_date))
        mongodb.store(collect_date, routes)
        print(f"filled collection {collect_date}")


if __name__ == "__main__":
    main()
