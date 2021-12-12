import statistics
from pathlib import Path
from operator import itemgetter
from database.models import CarType
from process.chart import create_chart, Chart
from database.jsondatabase import JSONDatabase
from utils import read_codes, str_date
import sys


USAGE = f'Usage: {sys.argv[0]} <data dir> <departure date> <tariff|seats>'


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

    db = JSONDatabase(sys.argv[1])
    codes = read_codes('codes.txt')

    charts: list[tuple[Chart, float]] = []
    for from_code, where_code in codes:
        chart = create_chart(db, departure_date, from_code,
                             where_code, CarType.PLAZKART, car_key,
                             statistics.mean)
        if not chart.points:
            continue
        _, min_tariff = min(chart.points, key=itemgetter(1))
        _, max_tariff = max(chart.points, key=itemgetter(1))
        ratio = min_tariff / max_tariff

        charts.append((chart, ratio))

    charts.sort(key=itemgetter(1))

    print(f'Chart with lowest ratio: {charts[0]}')
    print(f'Chart with highest ratio: {charts[-1]}')
    print(f'Median chart: {charts[len(charts) // 2]}')


if __name__ == '__main__':
    main()
