import zmq
from influxdb import InfluxDBClient
import simplejson as json
from datetime import datetime

# InfluxDB connections settings
host = '192.168.0.14'
port = 9092
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
print("SUB KRAKEN >>> INFLUXDB." +dbname+" [ORDERS]...")
socket.connect("tcp://192.168.0.13:%s" % port)

while True:
    topic, response = socket.recv_string().split()
    msg = json.loads(response)
    ticks = msg['result']
    for tick in ticks:
        instrument = str(tick)
        tick = ticks[instrument]
        for index, item in enumerate(tick['bids']):
            tier_id = str(index)
            top_bid = str(item[0])
            top_bid_volume = str(item[1])
            timestamp = str(item[2])
            # ms_timestamp = datetime.fromtimestamp ( timestamp ).strftime ( '%Y-%m-%dT%H:%M:%S.%f' )
            line = 'depth,instrument=' + instrument + ' tier_id=' + tier_id + ',top_bid=' + top_bid + ',top_bid_volume=' + top_bid_volume
            myclient.write_points(line, batch_size=500, protocol='line',time_precision='ms')
            # print(line)

        for index, item in enumerate(tick['asks']):
            tier_id = str(index)
            top_ask = str(item[0])
            top_ask_volume = str(item[1])
            timestamp = (item[2])
            # ms_timestamp = datetime.fromtimestamp ( timestamp ).strftime ( '%Y-%m-%dT%H:%M:%S.%f' )
            line = 'depth,instrument=' + instrument + ' tier_id=' + tier_id + ',top_ask=' + top_ask + ',top_ask_volume=' + top_ask_volume
            myclient.write_points(line, protocol='line', time_precision='ms')
            # print (line)
