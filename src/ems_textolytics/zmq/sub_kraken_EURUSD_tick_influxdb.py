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
print("Collecting KR_EURUSD updates into influxdb... ")
socket.connect("tcp://localhost:%s" % port)

if len(sys.argv) > 2:
    socket.connect("tcp://localhost:%s" % port1)

while True:
    response = socket.recv_string()
    topic, messagedata = response.split(' ')
    instrument_t0, kraken_EURUSD_BID_5_t0 , kraken_EURUSD_ASK_5_t0 , instrument , kraken_EURUSD_BID_5_t1 , kraken_EURUSD_ASK_5_t1 , spread, spread_t_bid, spread_t_ask = messagedata.split('\x01')


    tick_json = [
        {
            "measurement": 'synthetic',
            "tags": {
                "instrument": 'KR_EURUSD',
                "instrument_t0": instrument_t0,
                "instrument_t1": instrument,
            },
            "fields": {
                "hedge_instrument_t0": str(instrument_t0),
                "hedge_instrument_t1": str(instrument),
                "kraken_EURUSD_BID_5_t0": float ( kraken_EURUSD_BID_5_t0 ),
                "kraken_EURUSD_ASK_5_t0": float ( kraken_EURUSD_ASK_5_t0 ),
                "kraken_EURUSD_BID_5_t1": float ( kraken_EURUSD_BID_5_t1 ),
                "kraken_EURUSD_ASK_5_t1": float (kraken_EURUSD_ASK_5_t1 ),
                "spread_t_bid": float(spread_t_bid),
                "spread_t_ask": float(spread_t_ask),
                "spread": float(spread)
            }
        }
    ]
    # line = 'synthetic,instrument=KR_EURUSD,instrument_t0=' + instrument_t0 + ',instrument_t1=' + instrument + ' kraken_EURUSD_BID_5_t0=' + kraken_EURUSD_BID_5_t0 + ',kraken_EURUSD_ASK_5_t0=' + kraken_EURUSD_ASK_5_t0 + ',kraken_EURUSD_BID_5_t1=' + kraken_EURUSD_BID_5_t1 + ',kraken_EURUSD_ASK_5_t1=' + kraken_EURUSD_ASK_5_t1 + ',spread_t_bid=' + spread_t_bid + ',spread_t_ask=' + spread_t_ask + ',spread=' + spread
    # print ( line )
    # myclient_udp.send_packet ( line , protocol='line')
    # myclient_tcp.write_points( line , protocol='line')
    # myclient_udp._write_points ( line , protocol='line')
    myclient_tcp.write_points(tick_json, batch_size=500, time_precision='ms')
    # print ( tick_json)
