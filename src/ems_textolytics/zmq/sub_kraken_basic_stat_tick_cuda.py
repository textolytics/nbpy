from datetime import datetime

import pandas as pd
import zmq
from influxdb import InfluxDBClient
from numpy import *
from pandas import Series

# from numpy import *
# InfluxDB connections settings
host = '192.168.0.33'
port = 8086
user = 'zmq'
password = 'zmq'
dbname = 'tick'

myclient = InfluxDBClient(host, port, user, password, dbname, use_udp=False)

port = "5558"

if len(sys.argv) > 1:
    port = sys.argv[1]
    int(port)

if len(sys.argv) > 2:
    port1 = sys.argv[2]
    int(port1)

# Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)
topicfilter = "kraken_tick"
socket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)
socket.setsockopt_string(zmq.SUBSCRIBE, "1")
print ("Collecting tick updates from kraken server...")
socket.connect("tcp://192.168.0.13:%s" % port)
if len(sys.argv) > 2:
    socket.connect("tcp://192.168.0.13:%s" % port1)

ask_whole_lot_volume_np = np.float32()
ask_price_np = np.float32()

A = np.empty((2,))

print (A)

np_ts_array = np.empty(( 1,))

while True:
    response = socket.recv_string()
    topic, messagedata = response.split()
    # print (response)
    # topic, messagedata= response.split(' b')

    instrument ,ask_price , ask_whole_lot_volume , ask_lot_volume, bid_price , bid_whole_lot_volume , bid_lot_volume,    last_trade_price , last_trade_lot_volume, volume_today, volume_last_24_hours ,vwap_today, vwap_last_24_hours ,number_of_trades_today,number_of_trades_last_24_hours ,low_today, low_last_24_hours ,high_today, high_last_24_hours ,opening_price = messagedata.split('\x01')
    now_ts = datetime.strptime(datetime.utcnow().isoformat(sep='T'), '%Y-%m-%dT%H:%M:%S.%f')

    if instrument[ 0 ] == 'X' and instrument[ -4 ] == 'Z':
        base_ccy = instrument[ 1:4 ]
        term_ccy = instrument[ -3: ]
        # print (base_ccy,term_ccy)

    if len ( instrument ) == 6 and instrument[ -4 ] != '_':
        base_ccy = instrument[ 0:3 ]
        term_ccy = instrument[ 3:6 ]
    
    if instrument[ 0 ] == 'X' and instrument[ -4 ] == 'X':
        base_ccy = instrument[ 1:4 ]
        term_ccy = instrument[ -3: ]

    if instrument[ 0 ] != 'X' and instrument[ -4 ] == 'Z':
        base_ccy = instrument[ 0:4 ]
        term_ccy = instrument[ -3: ]
        # print (base_ccy,term_ccy)

    if instrument[ 0:4 ] == 'DASH' :
        base_ccy = instrument[ 0:4 ]
        term_ccy = instrument[ -3: ]
        # print (base_ccy,term_ccy)


    ask_price_np = np.float32(ask_price)
    ask_whole_lot_volume_np = np.float32(ask_whole_lot_volume)
    A = np.vstack((A,(ask_price_np,ask_whole_lot_volume_np)))
    np_tick = np.array([ask_price_np,ask_whole_lot_volume_np])
    print (np_tick)

#-------------Numpy------------

    np_timestamp = np.datetime64(now_ts)
    np_ts_array = np.vstack((np_ts_array,(np_timestamp)))
    print(np_timestamp)

#--------------------------------

#---------Pandas-----------------
    t =pd.Timestamp(now_ts)
    rng = pd.date_range(datetime.now(),periods = 10,freq = 't')
    ts = Series(ask_price_np,index=rng)
    print (ts)
#--------------------------------------


    print (now_ts, topic, instrument ,base_ccy, term_ccy , ask_price, ask_whole_lot_volume , ask_lot_volume, bid_price , bid_whole_lot_volume , bid_lot_volume,    last_trade_price , last_trade_lot_volume, volume_today, volume_last_24_hours ,vwap_today, vwap_last_24_hours ,number_of_trades_today,number_of_trades_last_24_hours ,low_today, low_last_24_hours ,high_today, high_last_24_hours ,opening_price)
