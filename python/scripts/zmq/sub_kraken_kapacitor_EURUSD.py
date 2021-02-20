import sys
import zmq
from influxdb import InfluxDBClient

# InfluxDB connections settings
host = '192.168.0.14'
port = 9092
user = 'zmq'
password = 'zmq'
dbname = 'tick'

myclient = InfluxDBClient(host, port,user,password, use_udp=False)
port = "5559"

if len(sys.argv) > 1:
    port = sys.argv[1]
    int(port)

if len(sys.argv) > 2:
    port1 = sys.argv[2]
    int(port1)

# Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)
topicfilter = "kr_eurusd_tick"
socket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)
socket.setsockopt_string(zmq.SUBSCRIBE, "1")
print("Collecting updates from weather server...")
socket.connect("tcp://192.168.0.13:%s" % port)

if len(sys.argv) > 2:
    socket.connect("tcp://192.168.0.13:%s" % port1)

while True:
    response = socket.recv_string()
    topic, messagedata = response.split(' ')
    instrument_t0, kraken_EURUSD_BID_5_t0 , kraken_EURUSD_ASK_5_t0 , instrument , kraken_EURUSD_BID_5_t1 , kraken_EURUSD_ASK_5_t1 , spread, spread_t_bid, spread_t_ask = messagedata.split('\x01')
    #
    #
    # tick_json = [
    #     {
    #         "measurement": 'synthetic',
    #         "tags": {
    #             "instrument": 'KR_EURUSD',
    #             "instrument_t0": instrument_t0,
    #             "instrument_t1": instrument,
    #
    #         },
    #         "fields": {
    #             "kraken_EURUSD_BID_5_t0": float ( kraken_EURUSD_BID_5_t0 ),
    #             "kraken_EURUSD_ASK_5_t0": float ( kraken_EURUSD_ASK_5_t0 ),
    #             "kraken_EURUSD_BID_5_t1": float ( kraken_EURUSD_BID_5_t1 ),
    #             "kraken_EURUSD_ASK_5_t1": float (kraken_EURUSD_ASK_5_t1 ),
    #             "spread_t_bid": float(spread_t_bid),
    #             "spread_t_ask": float(spread_t_ask),
    #             "spread": float(spread)
    #
    #         }
    #     }
    # ]
    line = 'synthetic,instrument=KR_EURUSD,instrument_t0=' + instrument_t0 + ',instrument_t1=' + instrument + ' kraken_EURUSD_BID_5_t0='+kraken_EURUSD_BID_5_t0+',kraken_EURUSD_ASK_5_t0='+kraken_EURUSD_ASK_5_t0+',kraken_EURUSD_BID_5_t1='+kraken_EURUSD_BID_5_t1+',kraken_EURUSD_ASK_5_t1='+kraken_EURUSD_ASK_5_t1+',spread_t_bid='+spread_t_bid+',spread_t_ask='+spread_t_ask+',spread='+spread
    # print (line)
    myclient.write_points( line , protocol='line',batch_size=500,  time_precision='ms')
    # myclient.write_points(tick_json, batch_size=500, time_precision='u')
    # print(instrument_t0, kraken_EURUSD_BID_5_t0, kraken_EURUSD_ASK_5_t0, instrument , kraken_EURUSD_BID_5_t1 , kraken_EURUSD_ASK_5_t1 , spread, spread_t_bid, spread_t_ask)
