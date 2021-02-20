import sys
from datetime import datetime

import numpy as np
import zmq
from influxdb import InfluxDBClient

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




# X = np.array[[],[],[]]
X = np.dtype=([('instrument', 'U10'),('ask_price', np.float32), ('ask_whole_volume', np.int32)])

Y = np.array([[],[],[]], dtype=[('instrument', 'U10'),('ask_price', np.float32), ('ask_whole_volume', np.int32)])


print (Y)

arr = np.zeros((5,), dtype=[('var1','f8'),('var2','f8')])
Y['instrument'] = np.arange(3,0)
print (arr)

Z = np.zeros(5, dtype = {'names': ['instrument' ,'ask_price' , 'ask_whole_lot_volume'], 'formats': ['a20', np.float32, np.int32]} )

z = 0

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
    X[0] = [instrument,ask_price_np,ask_whole_lot_volume_np]
    print (X)

    Z[z] = (instrument,ask_price_np,ask_whole_lot_volume_np)
    print(Z['instrument'],Z['ask_price'])
    z+=1
    print (now_ts, topic, instrument ,base_ccy, term_ccy , ask_price, ask_whole_lot_volume , ask_lot_volume, bid_price , bid_whole_lot_volume , bid_lot_volume,    last_trade_price , last_trade_lot_volume, volume_today, volume_last_24_hours ,vwap_today, vwap_last_24_hours ,number_of_trades_today,number_of_trades_last_24_hours ,low_today, low_last_24_hours ,high_today, high_last_24_hours ,opening_price)
