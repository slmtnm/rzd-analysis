from pprint import pprint
from pathlib import Path
from db.jsondatabase import JSONDatabase
import sys

USAGE = f'{sys.argv[0]} <path to data directory>'

date_count = {}

if len(sys.argv) != 2:
    print(USAGE, file=sys.stderr)
    exit(1)

db = JSONDatabase(Path(sys.argv[1]))
for cd in db.collect_dates():
    for dd in db.deparute_dates(cd):
        if dd not in date_count:
            date_count[dd] = 0
        date_count[dd] += 1

pprint(date_count)
