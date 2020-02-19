import zmq
from influxdb import InfluxDBClient
import simplejson as json
from datetime import datetime

# InfluxDB connections settings
host = 'tick.nb.lan'
tcp_port = 8086
udp_port = 8189
user = 'zmq'
password = 'zmq'
dbname = 'tick'
myclient_tcp = InfluxDBClient(host, tcp_port, user, password, dbname, use_udp=False)

# ZeroMQ connections settings
port = "5560"
context = zmq.Context()
socket = context.socket(zmq.SUB)
topicfilter = "kr_depth"
socket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)
socket.setsockopt_string(zmq.SUBSCRIBE, "1")
print("SUB :"+topicfilter+" >>> INFLUXDB." +dbname+" [ORDERS]...")
socket.connect("tcp://zmq.nb.lan:%s" % port)

base_ccy = ""
term_ccy = ""
while True:
    try:
        topic, response = socket.recv_string().split()
    except Exception as e:
        print (e)
    # print (response)
    msg = json.loads(response)
    ticks = msg['result']
    for tick in ticks:
        # print (ticks)
        instrument = str(tick)
        if instrument[0] == 'X' and instrument[-4] == 'Z':
            base_ccy = instrument[1:4]
            term_ccy = instrument[-3:]
            # print (base_ccy,term_ccy)
        elif len(instrument) == 6 and instrument[-4] != '_':
            base_ccy = instrument[0:3]
            term_ccy = instrument[3:6]
            # print (base_ccy,term_ccy)
        elif len(instrument) == 7 and instrument[-3:] == 'XBT':
            base_ccy = instrument[0:4]
            term_ccy = instrument[4:7]
        elif len(instrument) == 8 and instrument[-4] == 'X' and instrument[0] == 'X':
            base_ccy = instrument[1:4]
            term_ccy = instrument[5:8]

        tick = ticks[instrument]
        for index, item in enumerate(tick['bids']):
            tier_id = str(index)
            top_bid = str(item[0])
            top_bid_volume = str(item[1])
            timestamp = str(item[2])
            # ms_timestamp = datetime.fromtimestamp ( timestamp ).strftime ( '%Y-%m-%dT%H:%M:%S.%f' )
            line = 'depth,instrument=' + instrument + ',base_ccy=' + base_ccy + ',term_ccy=' + term_ccy + ' tier_id=' + tier_id + ',top_bid=' + top_bid + ',top_bid_volume=' + top_bid_volume
        myclient_tcp.write_points(line, protocol='line',  time_precision='ms')
        print(line)

        for index, item in enumerate(tick['asks']):
            tier_id = str(index)
            top_ask = str(item[0])
            top_ask_volume = str(item[1])
            timestamp = (item[2])
            # ms_timestamp = datetime.fromtimestamp ( timestamp ).strftime ( '%Y-%m-%dT%H:%M:%S.%f' )
            line = 'depth,instrument=' + instrument + ',base_ccy=' + base_ccy + ',term_ccy=' + term_ccy + ' tier_id=' + tier_id + ',top_ask=' + top_ask + ',top_ask_volume=' + top_ask_volume
        myclient_tcp.write_points(line, protocol='line',  time_precision='ms')
        print (line)
