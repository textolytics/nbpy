import sys
import zmq
from influxdb import InfluxDBClient

# InfluxDB connections settings
host = '192.168.0.33'
port = 8086
user = 'zmq'
password = 'zmq'
dbname = 'tick'

myclient = InfluxDBClient(host, port, user, password, dbname,use_udp=False)




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
socket.setsockopt_string(zmq.SUBSCRIBE,topicfilter)
socket.setsockopt_string(zmq.SUBSCRIBE, "1")
print ("Collecting updates from weather server...")
socket.connect("tcp://localhost:%s" % port)

if len(sys.argv) > 2:
    socket.connect("tcp://localhost:%s" % port1)

# Subscribe to zipcode, default is NYC, 10001


# Process 5 updates
total_value = 0
while True:
    response = socket.recv_string()
    topic, messagedata = response.split()

    # print (response)
    # topic, messagedata= response.split(' b')

    now_ts, instrument ,ask_price , ask_whole_lot_volume , ask_lot_volume, bid_price , bid_whole_lot_volume , bid_lot_volume,    last_trade_price , last_trade_lot_volume, volume_today, volume_last_24_hours ,vwap_today, vwap_last_24_hours ,number_of_trades_today,number_of_trades_last_24_hours ,low_today, low_last_24_hours ,high_today, high_last_24_hours ,opening_price = messagedata.split('\x01')
    # msg = json.dumps(messagedata)
    # total_value += int(messagedata)
    # if topic == 'tick':
    # instrument , volume_today , volume_last_24_hours , vwap_today , vwap_last_24_hours , number_of_trades_today , number_of_trades_last_24_hours , low_today , low_last_24_hours , high_today , high_last_24_hours , opening_price = messagedata.split (
    #     '\x01' )
    # msg = json.dumps(messagedata)
    # total_value += int(messagedata)
    print ( topic , instrument, ask_price , ask_whole_lot_volume , ask_lot_volume, bid_price , bid_whole_lot_volume , bid_lot_volume,    last_trade_price , last_trade_lot_volume, volume_today, volume_last_24_hours ,vwap_today, vwap_last_24_hours ,number_of_trades_today,number_of_trades_last_24_hours ,low_today, low_last_24_hours ,high_today, high_last_24_hours ,opening_price)

    tick_json = [
        {
            "measurement": "tick",
            "tags": {
                "instrument": str(instrument),
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
    myclient.write_points ( tick_json ,batch_size=500,  time_precision='ms' )
# print (topic, instrument, volume_today, volume_last_24_hours ,vwap_today, vwap_last_24_hours ,number_of_trades_today,number_of_trades_last_24_hours ,low_today, low_last_24_hours ,high_today, high_last_24_hours ,opening_price)

# print ("Average messagedata value for topic '%s' was %dF" % (topicfilter, total_value / update_nbr))

