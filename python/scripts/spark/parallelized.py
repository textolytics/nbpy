import pyspark as sp
from pyspark import SparkContext

sc = SparkContext

# rdd = sc.parallelize(["b", "a", "c"])
# sorted(rdd.map(lambda x: (x, 1)).collect())

nSlices = 10
sc = sp.SparkContext(appName='myApp')
rdd = sc.parallelize([2,3,4],nSlices)