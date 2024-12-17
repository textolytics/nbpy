import sys
import zmq
from influxdb import InfluxDBClient
import simplejson as json
from datetime import datetime
from pyspark.sql import Row
from pyspark.sql import SparkSession
print (datetime.utcnow())
spark = SparkSession \
    .builder \
    .appName("Protob Conversion to Parquet") \
    .config("spark.some.config.option", "some-value") \
    .getOrCreate()
mergedDF = spark.read.option("mergeSchema", "true").parquet("data/test_table")
mergedDF.printSchema()
print
# spark is from the previous example.
# Create a simple DataFrame, stored into a partition directory
sc = spark.sparkContext

squaresDF = spark.createDataFrame(sc.parallelize(range(1, 6))
                                  .map(lambda i: Row(single=i, double=i ** 2)))
squaresDF.write.parquet("data/test_table/key=1")

# Create another DataFrame in a new partition directory,
# adding a new column and dropping an existing column
cubesDF = spark.createDataFrame(sc.parallelize(range(6, 11))
                                .map(lambda i: Row(single=i, triple=i ** 3)))
cubesDF.write.parquet("data/test_table/key=2")

# Read the partitioned table
mergedDF = spark.read.option("mergeSchema", "true").parquet("data/test_table")
mergedDF.printSchema()








# Socket to talk to server
context = zmq.Context()
port = "5558"
socket = context.socket(zmq.SUB)
topicfilter = "kraken_tick"
socket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)
socket.setsockopt_string(zmq.SUBSCRIBE, "1")
print ("Collecting updates from weather server...")
socket.connect("tcp://localhost:%s" % port)

# Process 5 updates
total_value = 0
while True:
    response = socket.recv_string()
    # response_json = json.dumps(response)
    # print (response_json)
    topic, messagedata = response.split()
    # topic_decoded = topic.decode('utf-8', 'strict')
    # messagedata_decoded = messagedata.decode('utf-8', 'strict')
    print (messagedata)
    # tick = messagedata.split(""\x01")

    # print (tick)
    instrument ,ask_price , ask_whole_lot_volume , ask_lot_volume, bid_price , bid_whole_lot_volume , bid_lot_volume,    last_trade_price , last_trade_lot_volume, volume_today, volume_last_24_hours ,vwap_today, vwap_last_24_hours ,number_of_trades_today,number_of_trades_last_24_hours ,low_today, low_last_24_hours ,high_today, high_last_24_hours ,opening_price = messagedata.split('\x01')
    # msg = json.dumps(messagedata)
    # total_value += int(messagedata)
    # if topic == 'tick':
    # instrument , volume_today , volume_last_24_hours , vwap_today , vwap_last_24_hours , number_of_trades_today , number_of_trades_last_24_hours , low_today , low_last_24_hours , high_today , high_last_24_hours , opening_price = messagedata.split (
    #     '\x01' )
    # msg = json.dumps(messagedata)
    # total_value += int(messagedata)
    # print ( topic , instrument, ask_price , ask_whole_lot_volume , ask_lot_volume, bid_price , bid_whole_lot_volume , bid_lot_volume,    last_trade_price , last_trade_lot_volume, volume_today, volume_last_24_hours ,vwap_today, vwap_last_24_hours ,number_of_trades_today,number_of_trades_last_24_hours ,low_today, low_last_24_hours ,high_today, high_last_24_hours ,opening_price)

    if instrument[0] == 'X' and instrument[-4] == 'Z':
        base_ccy = instrument[1:4]
        term_ccy = instrument[-3:]
        # print (base_ccy,term_ccy)

    if len(instrument) == 6 and instrument[-4] != '_':
        base_ccy = instrument[0:3]
        term_ccy = instrument[3:6]

    if instrument[0] == 'X' and instrument[-4] == 'X':
        base_ccy = instrument[1:4]
        term_ccy = instrument[-3:]

    if instrument[0] != 'X' and instrument[-4] == 'Z':
        base_ccy = instrument[0:4]
        term_ccy = instrument[-3:]
        # print (base_ccy,term_ccy)

    if instrument[0:4] == 'DASH':
        base_ccy = instrument[0:4]
        term_ccy = instrument[-3:]
        # print (base_ccy,term_ccy)

    # print (messagedata,str(instrument))
    tick_json = [
        {
            "measurement": "tick",
            "tags": {
                "instrument": str(instrument),
                "base_ccy": base_ccy,
                "term_ccy": term_ccy
            },
            "fields": {
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
        }
    ]
    print (base_ccy,term_ccy)
    # myclient.write_points(tick_json, batch_size=500, time_precision='ms')
    print (topic, instrument, volume_today, volume_last_24_hours ,vwap_today, vwap_last_24_hours ,number_of_trades_today,number_of_trades_last_24_hours ,low_today, low_last_24_hours ,high_today, high_last_24_hours ,opening_price)

# print ("Average messagedata value for topic '%s' was %dF" % (topicfilter, total_value / update_nbr))



# data = []
# for x in range(5):
#     data.append((random.randint(0,9), random.randint(0,9)))
# df = spark.createDataFrame(data, ("label", "data"))
#
# df.show()
#
#
# #Write data in gzip compressed data in parquet format
# # path_parquet_gzip = "/prueba_gzip.parquet"# Read from HDFS
# path_parquet_gzip = "E:\data\parquet"""
#
# # Read from local file
#
# df.write \
#     .mode("append") \
#     .format("parquet") \
#     .option("compression", "gzip") \
#     .save(path_parquet_gzip)
#
#
#
# #Read gzip compressed data in parquet format
# df2 = spark \
#     .read \
#     .option("multiline", "true") \
#     .parquet(path_parquet_gzip)
#
# df2.show()
#
# # df.write.mode('append').parquet('parquet_data_file')
#
#
#
