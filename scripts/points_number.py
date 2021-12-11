from pathlib import Path
from datetime import date
from utils import date_str
from collections import defaultdict
from operator import itemgetter
from database.jsondatabase import JSONDatabase
import sys

USAGE = f"{sys.argv[0]} <path to data directory>"

date_count: defaultdict[date, int] = defaultdict(int)

if len(sys.argv) != 2:
    print(USAGE, file=sys.stderr)
    exit(1)

db = JSONDatabase(Path(sys.argv[1]))
for cd in db.collect_dates():
    for dd in db.deparute_dates(cd):
        date_count[dd] += 1

for k, v in sorted(date_count.items(), key=itemgetter(1), reverse=True):
    print(f"{k} points for {date_str(v)}")
