import zmq
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.streaming import StreamingContext

#function to calculate number of seconds from number of days
days = lambda i: i * 86400
import pyspark as sp

# import pyspark as spark
sc = sp.SparkContext(appName='oanda')
ssc = StreamingContext(sc, 1)
# lines = ssc.socketTextStream("localhost", 9999)

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



port = "5558"
# Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)
topicfilter = ''
socket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)
socket.setsockopt_string(zmq.SUBSCRIBE, "1")
print ("Collecting depth updates from kraken server...")
socket.connect("tcp://192.168.0.13:%s" % port)
List = []

# Subscribe to zipcode, default is NYC, 10001

while True:
    response = socket.recv_string()
    topic, messagedata = response.split()


    # print (topic,messagedata)

    instrument ,ask_price , ask_whole_lot_volume , ask_lot_volume, bid_price , bid_whole_lot_volume , bid_lot_volume,    last_trade_price , last_trade_lot_volume, volume_today, volume_last_24_hours ,vwap_today, vwap_last_24_hours ,number_of_trades_today,number_of_trades_last_24_hours ,low_today, low_last_24_hours ,high_today, high_last_24_hours ,opening_price = messagedata.split('\x01')

    nSlices = 1
    rdd = sc.parallelize([messagedata.split('\x01')], nSlices).collect()

    streaming_rdd = ssc.socketTextStream("localhost", 9999)
    windowed_streaming_rdd = streaming_rdd.window(20)
    # kraken_tick = rdd.broadcast([rdd])
    print (rdd)
    print (streaming_rdd)
    # print (kraken_tick.value)

    # print (topic, messagedata)



