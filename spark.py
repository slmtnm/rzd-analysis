import argparse
from dataclasses import dataclass
from datetime import date
from operator import itemgetter
from pathlib import Path

from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession

from database.jsondatabase import JSONDatabase
from database.models import Car, CarType
from process.chart import Chart, create_chart
from utils import read_codes, str_date


@dataclass
class Options:
    data_dir: str
    departure_date: date
    type: str
    appname: str


def parse_args() -> Options:
    parser = argparse.ArgumentParser(
        description='Find chart with maximum tariff/seats ratio')
    parser.add_argument('data_dir', help='path to data directory')
    parser.add_argument('departure_date', help='date when train leaves')
    parser.add_argument('type', help='characterisic to analyze',
                        choices=['tariff', 'seats'])
    parser.add_argument('--appname',
                        help='name of application to register in Hadoop',
                        default='rzd-analysis')
    args = parser.parse_args()
    return Options(args.data_dir, str_date(args.departure_date),
                   args.type, args.appname)


def code_chunks(filename: str) -> list[list[tuple[int, int]]]:
    codes = read_codes('codes.txt')
    chunk_size = 40
    return [codes[i: i + chunk_size]
            for i in range(0, len(codes), chunk_size)]


def target(db, departure_date, car_key, statistic):
    def inner(chunk: list[tuple[int, int]]) -> list[tuple[Chart, float]]:
        charts = []
        for from_code, where_code in chunk:
            chart = create_chart(db, departure_date, from_code,
                                 where_code, CarType.PLAZKART, car_key,
                                 statistic)
            if not chart.points:
                continue
            _, min_tariff = min(chart.points, key=itemgetter(1))
            _, max_tariff = max(chart.points, key=itemgetter(1))
            ratio = min_tariff / max_tariff

            charts.append((chart, ratio))
        charts.sort(key=itemgetter(1))
        return charts
    return inner


def main():
    options = parse_args()

    context = SparkContext(conf=SparkConf().setAppName(options.appname))

    chunks = code_chunks('codes.txt')
    with SparkSession(context) as _:
        min_chart = None
        min_ratio = 0

        if options.type == 'tariff':
            def car_key(car: Car) -> int: return car.tariff
        else:
            def car_key(car: Car) -> int: return car.free_seats

        func = target(JSONDatabase(options.data_dir),
                      options.departure_date, car_key, min)

        for charts in context.parallelize(chunks).map(func).collect():
            for chart, ratio in charts:
                if not min_chart or ratio < min_ratio:
                    min_chart, min_ratio = chart, ratio

        print(min_chart)


if __name__ == '__main__':
    main()
