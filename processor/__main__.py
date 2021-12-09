import statistics
from pathlib import Path
from operator import itemgetter
from db.models import CarType
from processor.chart import create_chart, Chart, plot
from db.jsondatabase import JSONDatabase
from utils import read_codes, str_date
import sys
import yaml


USAGE = f'Usage: {sys.argv[0]} <path to data dir> <departure date> <tariff|seats> [<from> <to>]'


def main() -> None:
    if len(sys.argv) != 4 and len(sys.argv) != 6:
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

    charts: list[tuple[Chart, float]] = []

    cities = yaml.safe_load(open('codes.yaml'))

    if len(sys.argv) == 6:
        chart = create_chart(db, departure_date, int(sys.argv[4]),
                             int(sys.argv[5]), CarType.PLAZKART, car_key,
                             statistics.mean)
        if not chart.points:
            print('no data found')
            return

        _, min_tariff = min(chart.points, key=itemgetter(1))
        _, max_tariff = max(chart.points, key=itemgetter(1))
        ratio = min_tariff / max_tariff

        charts.append((chart, ratio))

        city_from = [el['city'] for el in cities if el['code'] == charts[0][0].from_code][0]
        city_to = [el['city'] for el in cities if el['code'] == charts[0][0].where_code][0]

        plot(charts[0][0], f'{charts[0][0].date.strftime("%d.%m.%Y")}. {city_from.title()} - {city_to.title()}',
        'Стоимость билета' if sys.argv[3] == 'tariff' else 'Количество свободных мест'
        if sys.argv[3] == 'seats' else '')
    else:
        for from_code, where_code in codes:
            chart = create_chart(db, departure_date, from_code,
                                where_code, CarType.COUPE, car_key,
                                statistics.mean)
            if not chart.points:
                continue

            _, min_tariff = min(chart.points, key=itemgetter(1))
            _, max_tariff = max(chart.points, key=itemgetter(1))
            ratio = min_tariff / max_tariff

            charts.append((chart, ratio))

        charts.sort(key=itemgetter(1))

        city_from = [el['city'] for el in cities if el['code'] == charts[0][0].from_code][0]
        city_to = [el['city'] for el in cities if el['code'] == charts[0][0].where_code][0]

        print(f'Chart with lowest ratio: {charts[0]}')
        print(f'Chart with highest ratio: {charts[-1]}')
        print(f'Median chart: {charts[len(charts) // 2]}')

        plot(charts[0][0], f'{charts[0][0].date.strftime("%d.%m.%Y")}. {city_from.title()} - {city_to.title()}',
        'Стоимость билета' if sys.argv[3] == 'tariff' else 'Количество свободных мест'
        if sys.argv[3] == 'seats' else '')


if __name__ == '__main__':
    main()
