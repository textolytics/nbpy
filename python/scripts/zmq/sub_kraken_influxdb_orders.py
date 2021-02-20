import zmq
from influxdb import InfluxDBClient
import simplejson as json
from datetime import datetime

# InfluxDB connections settings
host = '192.168.0.33'
port = 8086
user = 'zmq'
password = 'zmq'
dbname = 'tick'
myclient = InfluxDBClient(host, port, user, password, dbname, use_udp=False)

# ZeroMQ connections settings
port = "5560"
context = zmq.Context()
socket = context.socket(zmq.SUB)
topicfilter = "kr_order_book"
socket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)
socket.setsockopt_string(zmq.SUBSCRIBE, "1")
print("SUB :"+topicfilter+" >>> INFLUXDB." +dbname+" [ORDERS]...")
socket.connect("tcp://192.168.0.13:%s" % port)

while True:
    topic, response = socket.recv_string().split()
    msg = json.loads(response)
    ticks = msg['result']
    for tick in ticks:
        instrument = str(tick)
        if instrument[0] == 'X' and instrument[-4] == 'Z':
            base_ccy = instrument[1:4]
            term_ccy = instrument[-3:]
            # print (base_ccy,term_ccy)
        elif len(instrument) == 6 and instrument[-4] != '_':
            base_ccy = instrument[0:3]
            term_ccy = instrument[3:6]
            # print (base_ccy,term_ccy)
        tick = ticks[instrument]
        for index, item in enumerate(tick['bids']):
            tier_id = str(index)
            top_bid = str(item[0])
            top_bid_volume = str(item[1])
            timestamp = str(item[2])
            # ms_timestamp = datetime.fromtimestamp ( timestamp ).strftime ( '%Y-%m-%dT%H:%M:%S.%f' )
            line = 'depth,instrument=' + instrument + ',base_ccy=' + base_ccy + ',term_ccy=' + term_ccy + ' tier_id=' + tier_id + ',top_bid=' + top_bid + ',top_bid_volume=' + top_bid_volume
            myclient.write_points(line, protocol='line',batch_size=500,  time_precision='ms')
            # print(line)

        for index, item in enumerate(tick['asks']):
            tier_id = str(index)
            top_ask = str(item[0])
            top_ask_volume = str(item[1])
            timestamp = (item[2])
            # ms_timestamp = datetime.fromtimestamp ( timestamp ).strftime ( '%Y-%m-%dT%H:%M:%S.%f' )
            line = 'depth,instrument=' + instrument + ',base_ccy=' + base_ccy + ',term_ccy=' + term_ccy + ' tier_id=' + tier_id + ',top_ask=' + top_ask + ',top_ask_volume=' + top_ask_volume
            myclient.write_points(line, protocol='line', batch_size=500, time_precision='ms')
            print (line)
