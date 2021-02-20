from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.types import *

#function to calculate number of seconds from number of days
days = lambda i: i * 86400

# import pyspark as spark
sc = SparkContext
# ssc = StreamingContext
spark = SparkSession.builder \
    .master("local") \
    .appName("oanda") \
    .getOrCreate()

schema = StructType([
    StructField("instrument", StringType(), True),
    StructField("time", StringType(), True),
    StructField("bid", StringType(), True),
    StructField("ask", StringType(), True)])

import zmq
port = "5562"
# Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)
print ("Collecting updates from kraken...")
socket.connect ("tcp://192.168.0.13:%s" % port)
topicfilter = ""
socket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)

while True:
    response = socket.recv_string()
    topic, messagedata = response.split(' ')
    # print (topic)
    time, bid, ask = messagedata.split('\x01')
    line = [(topic , time,  bid , ask)]
    df = spark._createFromLocal(line,schema=schema)
    print (df)

    schemaPeople = spark.createDataFrame(line, schema=schema)
    schemaPeople.createOrReplaceTempView('instruments')
    results = spark.sql("SELECT * FROM instruments")
    for result in results:
        print (result)
    # print (results.value)
    print (topic, messagedata)



