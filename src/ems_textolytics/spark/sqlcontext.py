from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.streaming import StreamingContext
from pyspark.sql import HiveContext
import time
#function to calculate number of seconds from number of days
days = lambda i: i * 86400
import pyspark as sp

# import pyspark as spark
sc = sp.SparkContext(appName='oanda')
ssc = StreamingContext(sc, 1)
sqlCtx = HiveContext(sc)

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


# def convert_to_row(d: dict) -> Row:
#     return Row(**OrderedDict(sorted(d.items())))


import zmq


port = "5558"
# Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)
topicfilter = ''
socket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)
socket.setsockopt_string(zmq.SUBSCRIBE, "1")
print ("Collecting tick updates from kraken server...")
socket.connect("tcp://192.168.0.13:%s" % port)
List = []

# Subscribe to zipcode, default is NYC, 10001

# while True:
response = socket.recv_string()
topic, messagedata = response.split()
print (topic,messagedata)
instrument ,ask_price , ask_whole_lot_volume , ask_lot_volume, bid_price , bid_whole_lot_volume , bid_lot_volume,    last_trade_price , last_trade_lot_volume, volume_today, volume_last_24_hours ,vwap_today, vwap_last_24_hours ,number_of_trades_today,number_of_trades_last_24_hours ,low_today, low_last_24_hours ,high_today, high_last_24_hours ,opening_price = messagedata.split('\x01')

tick_json = [
    {
        "instrument": str(instrument),
        "ask_price": float ( ask_price ) ,
        "ask_whole_lot_volume": float ( ask_whole_lot_volume ) ,
        "ask_lot_volume": float ( ask_lot_volume ) ,
        "bid_price": float ( bid_price ) ,
        "bid_whole_lot_volume": float ( bid_whole_lot_volume ) ,
        "bid_lot_volume": float ( bid_lot_volume ) ,
        "last_trade_price": float ( last_trade_price ) ,
        "last_trade_lot_volume": float ( last_trade_lot_volume ) ,
        "volume_today": float ( volume_today ) ,
        "volume_last_24_hours": float ( volume_last_24_hours ) ,
        "vwap_today": float ( vwap_today ) ,
        "vwap_last_24_hours": float ( vwap_last_24_hours ) ,
        "number_of_trades_today": float ( number_of_trades_today ) ,
        "number_of_trades_last_24_hours": float ( number_of_trades_last_24_hours ) ,
        "low_today": float ( low_today ) ,
        "low_last_24_hours": float ( low_last_24_hours ) ,
        "high_today": float ( high_today ) ,
        "high_last_24_hours": float ( high_last_24_hours ) ,
        "opening_price": float ( opening_price )
    }
]

tick_df = sc.parallelize(tick_json).toDF()
ticks_df = tick_df.collect()
tick_df.registerTempTable("my_table")
time.sleep(3)
sqlCtx.sql("CREATE TABLE my_table_two AS SELECT * from my_table")

print(tick_df)
print(ticks_df)