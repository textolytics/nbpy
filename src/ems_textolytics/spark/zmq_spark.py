from pyspark import SparkContext
from pyspark.sql import SparkSession

sc = SparkContext

spark = SparkSession \
    .builder \
    .appName("Python Spark SQL basic example") \
    .config("spark.some.config.option", "some-value") \
    .getOrCreate()



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




    time, bid, ask = messagedata.split('\x01')
    sc = topic, time, bid, ask
    print (sc)

    print (topic, messagedata)



