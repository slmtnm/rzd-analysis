from itertools import chain
import statistics
from pathlib import Path
from operator import itemgetter
from database.models import CarType
from process.chart import create_chart, Chart
from database.jsondatabase import JSONDatabase
from concurrent.futures import ProcessPoolExecutor
from utils import read_codes, str_date
import sys
from .chart import plot
import yaml

USAGE = f'Usage: {sys.argv[0]} <path to data dir> <departure date> <tariff|seats>'

db = JSONDatabase(Path(sys.argv[1]))

departure_date = str_date(sys.argv[2])


def target(batch):
    charts = []
    for from_code, where_code in batch:
        chart = create_chart(db, departure_date, from_code, where_code,
                             CarType.COUPE, lambda car: car.tariff,
                             statistics.mean)
        if not chart.points:
            continue
        _, min_tariff = min(chart.points, key=itemgetter(1))
        _, max_tariff = max(chart.points, key=itemgetter(1))
        ratio = min_tariff / max_tariff

        charts.append((chart, ratio))
    return charts


def main() -> None:
    if len(sys.argv) != 4:
        print(USAGE, file=sys.stderr)
        exit(1)

    codes = read_codes('codes.txt')

    batch_size = len(codes) // 16
    batches = [
        codes[i:i + batch_size] for i in range(0, len(codes), batch_size)
    ]

    with ProcessPoolExecutor(max_workers=16) as executor:
        result = executor.map(target, batches)
        charts = list(chain.from_iterable(result))

    charts.sort(key=itemgetter(1))

    print(f'Chart with lowest ratio: {charts[0]}')
    print(f'Chart with highest ratio: {charts[-1]}')
    print(f'Median chart: {charts[len(charts) // 2]}')

    cities = yaml.safe_load(open('codes.yaml'))
    city_from = [
        el['city'] for el in cities if el['code'] == charts[0].from_code
    ][0]
    city_to = [
        el['city'] for el in cities if el['code'] == charts[0].where_code
    ][0]

    plot(charts[0].points,
        f'{charts[0].date.strftime("%d.%m.%Y")}. {city_from.title()} - {city_to.title()}',
        'Количество дней до отправления' if sys.argv[3] == 'tariff' else
        'Количество свободных мест' if sys.argv[3] == 'seats' else '')


if __name__ == '__main__':
    main()
