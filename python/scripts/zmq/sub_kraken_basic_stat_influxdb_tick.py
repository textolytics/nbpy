import sys

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


X = [[],[]]
base_ccy =""
term_ccy = ""
response = socket.recv_string()
topic, messagedata = response.split()
instrument ,ask_price , ask_whole_lot_volume , ask_lot_volume, bid_price , bid_whole_lot_volume , bid_lot_volume,    last_trade_price , last_trade_lot_volume, volume_today, volume_last_24_hours ,vwap_today, vwap_last_24_hours ,number_of_trades_today,number_of_trades_last_24_hours ,low_today, low_last_24_hours ,high_today, high_last_24_hours ,opening_price = messagedata.split('\x01')


ask_price_np = np.float(ask_price)
print (ask_price_np)
ask_whole_lot_volume_np = np.float(ask_whole_lot_volume)
Y = np.dtype([('instrument', 'U12'), ('ask_price', np.float32), ('ask_whole_lot_volume', np.int32)])
print (Y.names)

# X = np.array([[topic, instrument, base_ccy, term_ccy, ask_price, ask_whole_lot_volume, ask_lot_volume, bid_price,
#               bid_whole_lot_volume, bid_lot_volume, last_trade_price, last_trade_lot_volume, volume_today,
#               volume_last_24_hours, vwap_today, vwap_last_24_hours, number_of_trades_today,
#               number_of_trades_last_24_hours, low_today, low_last_24_hours, high_today, high_last_24_hours,
#               opening_price]],
#              dtype=[('topic', 'S12'), (' instrument ', 'U10'), ('base_ccy', 'U10'), (' term_ccy ', 'U10'),
#                     (' ask_price', 'U10'), (' ask_whole_lot_volume ', 'U10'), (' ask_lot_volume', 'U10'),
#                     (' bid_price ', 'U10'), (' bid_whole_lot_volume ', 'U10'), (' bid_lot_volume', 'U10'),
#                     ('last_trade_price ', 'U10'), (' last_trade_lot_volume', 'U10'), (' volume_today', 'U10'),
#                     (' volume_last_24_hours ', 'U10'), ('vwap_today', 'U10'), (' vwap_last_24_hours ', 'U10'),
#                     ('number_of_trades_today', 'U10'), ('number_of_trades_last_24_hours ', 'U10'), ('low_today', 'U10'),
#                     (' low_last_24_hours ', 'U10'), ('high_today', 'U10'), (' high_last_24_hours ', 'U10'),
#                     ('opening_price', 'U10')])

while True:
    response = socket.recv_string()
    topic, messagedata = response.split()
    # print (response)
    # topic, messagedata= response.split(' b')

    instrument ,ask_price , ask_whole_lot_volume , ask_lot_volume, bid_price , bid_whole_lot_volume , bid_lot_volume,    last_trade_price , last_trade_lot_volume, volume_today, volume_last_24_hours ,vwap_today, vwap_last_24_hours ,number_of_trades_today,number_of_trades_last_24_hours ,low_today, low_last_24_hours ,high_today, high_last_24_hours ,opening_price = messagedata.split('\x01')
    # msg = json.dumps(messagedata)
    # total_value += int(messagedata)
    # if topic == 'tick':
    # instrument , volume_today , volume_last_24_hours , vwap_today , vwap_last_24_hours , number_of_trades_today , number_of_trades_last_24_hours , low_today , low_last_24_hours , high_today , high_last_24_hours , opening_price = messagedata.split (
    #     '\x01' )
    # msg = json.dumps(messagedata)
    # total_value += int(messagedata)
    # print ( topic , instrument, ask_price , ask_whole_lot_volume , ask_lot_volume, bid_price , bid_whole_lot_volume , bid_lot_volume,    last_trade_price , last_trade_lot_volume, volume_today, volume_last_24_hours ,vwap_today, vwap_last_24_hours ,number_of_trades_today,number_of_trades_last_24_hours ,low_today, low_last_24_hours ,high_today, high_last_24_hours ,opening_price)

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
    print (topic, instrument ,base_ccy, term_ccy , ask_price, ask_whole_lot_volume , ask_lot_volume, bid_price , bid_whole_lot_volume , bid_lot_volume,    last_trade_price , last_trade_lot_volume, volume_today, volume_last_24_hours ,vwap_today, vwap_last_24_hours ,number_of_trades_today,number_of_trades_last_24_hours ,low_today, low_last_24_hours ,high_today, high_last_24_hours ,opening_price)
#----------------------------------------------------------------
    # print (X)
    # X = np.append(X, [[ask_price],[bid_price]])
    # df = pd.DataFrame(X[:])
    # print(df.describe(include='all'))
    # # np.array([],[])
    # # np.append(np,[[i,j]], axis=0)
    # # np.roll(ask_price, 1, axis=0)
    # print (X[0:])

#-----------------------------------------------------------------
    # # np.append(np,[[i,j]], axis=0)
    Y.append([[instrument], [ask_price_np]], [ask_whole_lot_volume_np], axis=0)

    # Y[['instrument'], ['ask_price'], ['ask_whole_lot_volume']] = (instrument,ask_price,ask_whole_lot_volume)

    print (Y)
    # X = array([topic, instrument ,base_ccy, term_ccy , ask_price, ask_whole_lot_volume , ask_lot_volume, bid_price , bid_whole_lot_volume , bid_lot_volume,    last_trade_price , last_trade_lot_volume, volume_today, volume_last_24_hours ,vwap_today, vwap_last_24_hours ,number_of_trades_today,number_of_trades_last_24_hours ,low_today, low_last_24_hours ,high_today, high_last_24_hours ,opening_price])



    #
    # # print (messagedata,str(instrument))
    # tick_json = [
    #     {
    #         "measurement": "tick",
    #         "tags": {
    #             "instrument": str(instrument),
    #             "base_ccy": base_ccy,
    #             "term_ccy": term_ccy
    #         },
    #         "fields": {
    #             "ask_price": float ( ask_price ) ,
    #             "ask_whole_lot_volume": float ( ask_whole_lot_volume ) ,
    #             "ask_lot_volume": float ( ask_lot_volume ) ,
    #             "bid_price": float ( bid_price ) ,
    #             "bid_whole_lot_volume": float ( bid_whole_lot_volume ) ,
    #             "bid_lot_volume": float ( bid_lot_volume ) ,
    #             "last_trade_price": float ( last_trade_price ) ,
    #             "last_trade_lot_volume": float ( last_trade_lot_volume ) ,
    #             "volume_today": float ( volume_today ) ,
    #             "volume_last_24_hours": float ( volume_last_24_hours ) ,
    #             "vwap_today": float ( vwap_today ) ,
    #             "vwap_last_24_hours": float ( vwap_last_24_hours ) ,
    #             "number_of_trades_today": float ( number_of_trades_today ) ,
    #             "number_of_trades_last_24_hours": float ( number_of_trades_last_24_hours ) ,
    #             "low_today": float ( low_today ) ,
    #             "low_last_24_hours": float ( low_last_24_hours ) ,
    #             "high_today": float ( high_today ) ,
    #             "high_last_24_hours": float ( high_last_24_hours ) ,
    #             "opening_price": float ( opening_price )
    #         }
    #     }
    # ]

    # print (base_ccy,term_ccy)
    # myclient.write_points(tick_json, batch_size=500, time_precision='ms')
# def window_stack(a, stepsize=1, width=3):
#         return np.hstack(a[i:1 + i - width or None:stepsize] for i in range(0, width))


    # arr = [[],[]]
    # lenX = 10
    # lenY = 50
    # for i in range(1, lenX):
    #     for j in range(1, lenY):
    #         arr[1:-1, 1:-1] = .25 * (arr[:-2, 1:-1] + arr[2:, 1:-1] + arr[1:-1, :-2] + arr[1:-1, 2:])
    #

# print ("Average messagedata value for topic '%s' was %dF" % (topicfilter, total_value / update_nbr))

