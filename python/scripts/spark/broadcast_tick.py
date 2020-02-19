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


import zmq


port = "5558"
# Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)
topicfilter = ''
socket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)
socket.setsockopt_string(zmq.SUBSCRIBE, "1")
print ("Collecting tick updates from kraken server...")
socket.connect("tcp://localhost:%s" % port)
List = []

# Subscribe to zipcode, default is NYC, 10001

while True:
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

    # sql_df = SQLContext.createDataFrame((instrument ,ask_price , ask_whole_lot_volume , ask_lot_volume, bid_price , bid_whole_lot_volume , bid_lot_volume,    last_trade_price , last_trade_lot_volume, volume_today, volume_last_24_hours ,vwap_today, vwap_last_24_hours ,number_of_trades_today,number_of_trades_last_24_hours ,low_today, low_last_24_hours ,high_today, high_last_24_hours ,opening_price), (['instrument','ask_price','ask_whole_lot_volume','ask_lot_volume','bid_price','bid_whole_lot_volume','bid_lot_volume','last_trade_price','last_trade_lot_volume','volume_today','volume_last_24_hours','vwap_today','vwap_last_24_hours','number_of_trades_today','number_of_trades_last_24_hours','low_today','low_last_24_hours','high_today','high_last_24_hours','opening_price'])).collect()
    nSlices = 1
    rdd = sc.parallelize((instrument ,ask_price , ask_whole_lot_volume , ask_lot_volume, bid_price , bid_whole_lot_volume , bid_lot_volume,    last_trade_price , last_trade_lot_volume, volume_today, volume_last_24_hours ,vwap_today, vwap_last_24_hours ,number_of_trades_today,number_of_trades_last_24_hours ,low_today, low_last_24_hours ,high_today, high_last_24_hours ,opening_price), nSlices)
    tick_df = rdd.map(lambda x: (x, )).toDF()
    peopleDF = spark.read.json(rdd)

    tick_df.write.parquet("kraken_tick.parquet")
    streaming_rdd = ssc.socketTextStream("localhost", 9999)
    windowed_streaming_rdd = streaming_rdd.window(20)
    # kraken_tick = sc.broadcast([rdd])

    # print (tick_json_df)
    print(rdd)
    print (tick_df)
    print ("window:",windowed_streaming_rdd)

    # print (topic, messagedata)



