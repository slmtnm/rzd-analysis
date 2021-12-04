from pyspark.sql import SparkSession
from pyspark import SparkConf, SparkContext

thread_cnt = 4
conf = SparkConf().setAppName('trySpark')
sc = SparkContext(conf=conf)

with SparkSession(sc) as spark:
    res = sc.parallelize([1, 2, 3, 4]).map(lambda x: x + 1).collect()
    print(res)
