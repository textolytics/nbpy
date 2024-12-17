#!/usr/bin/python3.5
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
topicfilter = "kr_depth"
socket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)
socket.setsockopt_string(zmq.SUBSCRIBE, "1")
print("SUB :" + topicfilter + " >>> INFLUXDB." + dbname + " [ORDERS]...")
socket.connect("tcp://localhost:%s" % port)

while True:
    topic, response = socket.recv_string().split()
    msg = json.loads(response)
    ticks = msg['result']
    # print (ticks)
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
        # tier_id, top_bid, top_bid_volume, timestamp = tick['bids'].split('')
        #
        # print (tier_id, top_bid, top_bid_volume, timestamp)

        for index, item in enumerate(tick['bids']):
            tier_id = str(index)
            top_bid = str(item[0])
            top_bid_volume = str(item[1])
            timestamp = int(item[2])
            ms_timestamp = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%S.%f')
            # line = 'depth,instrument=' + instrument + ',base_ccy=' + base_ccy + ',term_ccy=' + term_ccy + ' tier_id=' + tier_id + ',top_bid=' + top_bid + ',top_bid_volume=' + top_bid_volume
            # myclient.write_points(line, protocol='line',batch_size=500,  time_precision='ms')
            # print(line)
        for index, item in enumerate(tick['asks']):
            tier_id = str(index)
            top_ask = str(item[0])
            top_ask_volume = str(item[1])
            timestamp = int(item[2])
            ms_timestamp = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%S.%f')
            # line = 'depth,instrument=' + instrument + ',base_ccy=' + base_ccy + ',term_ccy=' + term_ccy + ' tier_id=' + tier_id + ',top_ask=' + top_ask + ',top_ask_volume=' + top_ask_volume
            # myclient.write_points(line, protocol='line', batch_size=500, time_precision='ms')
            # print (line)
        line = 'exposure,instrument=' + instrument + ',base_ccy=' + base_ccy + ',term_ccy=' + term_ccy + ' bid_tier_id=' + tier_id + ',top_bid=' + top_bid + ',top_bid_volume=' + top_bid_volume + \
               ',bid_base_amount=' + top_bid_volume + ',bid_term_amount=' + str(float(top_bid_volume) * float(
                top_bid)) + ',ask_tier_id=' + tier_id + ',top_ask=' + top_ask + ',top_ask_volume=' + top_ask_volume + ',ask_base_amount=' + top_ask_volume + ',ask_term_amount=' + str(
            float(top_ask_volume) * float(top_ask))
        myclient.write_points(line, protocol='line', time_precision='ms')
        print(line)
