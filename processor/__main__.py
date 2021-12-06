import statistics
from pathlib import Path
from operator import itemgetter
from db.models import CarType
from processor.chart import create_chart
from db.jsondatabase import JSONDatabase
from utils import read_codes, str_date
import sys


USAGE = f'Usage: {sys.argv[0]} <path to data dir> <departure date> <tariff|seats>'


def main() -> None:
    if len(sys.argv) != 4:
        print(USAGE, file=sys.stderr)
        exit(1)

    departure_date = str_date(sys.argv[2])
    if sys.argv[3] == 'tariff':
        def car_key(car): return car.tariff
    elif sys.argv[3] == 'seats':
        def car_key(car): return car.free_seats
    else:
        print(USAGE, file=sys.stderr)
        exit(1)

    db = JSONDatabase(Path(sys.argv[1]))
    codes = read_codes('codes.txt')

    max_chart = None
    max_ratio = 0.
    for from_code, where_code in codes:
        chart = create_chart(db, departure_date, from_code,
                             where_code, CarType.PLAZKART, car_key,
                             statistics.mean)
        if not chart.points:
            continue
        _, min_tariff = min(chart.points, key=itemgetter(1))
        _, max_tariff = max(chart.points, key=itemgetter(1))
        ratio = min_tariff / max_tariff

        if not max_chart or ratio < max_ratio:
            max_chart, max_ratio = chart, ratio
    print(max_chart)
    print(max_ratio)


if __name__ == '__main__':
    main()
