import sys
import zmq
from influxdb import InfluxDBClient


# InfluxDB connections settings
host = '192.168.0.33'
tcp_port = 8086
udp_port = 8189
user = 'zmq'
password = 'zmq'
dbname = 'tick'
myclient_tcp = InfluxDBClient(host, tcp_port, user, password, dbname ,use_udp=False)
# myclient_udp = InfluxDBClient(host, udp_port, user, password, dbname, use_udp=True)

port = "5561"

# Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)
topicfilter = "kr_eurusd_depth"
socket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)
socket.setsockopt_string(zmq.SUBSCRIBE, "1")
print("Collecting updates from weather server...")
socket.connect("tcp://zmq.nb.lan:%s" % port)



while True:
    response = socket.recv_string()
    topic, messagedata = response.split(' ')
    instrument_t0, kraken_EURUSD_BID_5_t0, kraken_EURUSD_ASK_5_t0, bid_t0, bid_volume_t0, ask_t0, ask_volume_t0, instrument_t1, kraken_EURUSD_BID_5_t1, kraken_EURUSD_ASK_5_t1, bid_t1, bid_volume_t1, ask_t1, ask_volume_t1, spread, spread_t_bid, spread_t_ask = messagedata.split('\x01')
    if float(spread_t_bid) < 0:
        print ("BID ARRIVED")
        print(instrument_t0, "bid_instrument_t0*")
        print (instrument_t1)
        print(instrument_t1, "ask_instrument_t1*")

    tick_json = [
        {
            "measurement": 'orders',
            "tags": {
                "instrument": 'KR_EURUSD_ORDER',
                "instrument_t0": instrument_t0,
                "instrument_t1": instrument_t1,
            },
            "fields": {
                "kraken_EURUSD_depth_BID_5_t0": float ( kraken_EURUSD_BID_5_t0 ),
                "kraken_EURUSD_depth_ASK_5_t0": float ( kraken_EURUSD_ASK_5_t0 ),
                "kraken_EURUSD_depth_BID_5_t1": float ( kraken_EURUSD_BID_5_t1 ),
                "kraken_EURUSD_depth_ASK_5_t1": float (kraken_EURUSD_ASK_5_t1 ),
                "spread_depth_t_bid": float(spread_t_bid),
                "spread_depth_t_ask": float(spread_t_ask),
                "spread_depth": float(spread)
            }
        }
    ]
    # line = 'synthetic,instrument=KR_EURUSD,instrument_t0=' + instrument_t0 + ',instrument_t1=' + instrument + ' kraken_EURUSD_BID_5_t0=' + kraken_EURUSD_BID_5_t0 + ',kraken_EURUSD_ASK_5_t0=' + kraken_EURUSD_ASK_5_t0 + ',kraken_EURUSD_BID_5_t1=' + kraken_EURUSD_BID_5_t1 + ',kraken_EURUSD_ASK_5_t1=' + kraken_EURUSD_ASK_5_t1 + ',spread_t_bid=' + spread_t_bid + ',spread_t_ask=' + spread_t_ask + ',spread=' + spread
    # print ( line )
    # myclient_udp.send_packet ( line , protocol='line')
    # myclient_tcp.write_points( line , protocol='line')
    # myclient_udp._write_points ( line , protocol='line')
    myclient_tcp.write_points(tick_json, time_precision='ms')
    # print ( instrument_t0 , kraken_EURUSD_BID_5_t0 , kraken_EURUSD_ASK_5_t0 , instrument , kraken_EURUSD_BID_5_t1 ,
    #         kraken_EURUSD_ASK_5_t1 , spread , spread_t_bid , spread_t_ask )
