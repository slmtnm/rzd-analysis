import sys
from pathlib import Path
sys.path.append(str((Path.cwd() / sys.argv[0]).parent.parent))

import argparse
from collections import defaultdict
from datetime import date
from operator import itemgetter
from pathlib import Path

from database.jsondatabase import JSONDatabase


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Show collected routes statistic'
    )
    parser.add_argument('data_dir', help='path to data directory')
    return parser.parse_args()


def main():
    args = parse_arguments()
    db = JSONDatabase(args.data_dir)

    date_count: defaultdict[date, int] = defaultdict(int)
    for cd in db.collect_dates():
        for dd in db.deparute_dates(cd):
            date_count[dd] += 1

    for k, v in sorted(date_count.items(), key=itemgetter(1), reverse=True):
        print(f"{v} points for {str(k)}")


if __name__ == '__main__':
    main()
