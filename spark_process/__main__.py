from operator import itemgetter
from pathlib import Path

from pyspark.conf import SparkConf
from database.jsondatabase import JSONDatabase
from process.chart import Chart, create_chart
from pyspark.sql import SparkSession
from pyspark import SparkContext
from database.models import CarType, Car
from spark_process.args import parse_args
from utils import read_codes


def code_chunks(filename: str) -> list[list[tuple[int, int]]]:
    codes = read_codes('codes.txt')
    chunk_size = len(codes) // 4
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

    context = SparkContext(conf=SparkConf().setAppName(options.appname).setMaster(options.master_url))
    # context = SparkContext(master=options.master_url, appName=options.appname)

    chunks = code_chunks('codes.txt')
    with SparkSession(context) as _:
        min_chart = None
        min_ratio = 0

        if options.type == 'tariff':
            def car_key(car: Car) -> int: return car.tariff
        else:
            def car_key(car: Car) -> int: return car.free_seats

        func = target(JSONDatabase(Path(options.data_dir)),
                      options.departure_date, car_key, min)
        
        print(context.parallelize([1,2,3]).map(lambda x: x+1).collect())
        return

        for charts in context.parallelize(chunks).map(func).collect():
            for chart, ratio in charts:
                if not min_chart or ratio < min_ratio:
                    min_chart, min_ratio = chart, ratio

        print(min_chart)


if __name__ == '__main__':
    main()
