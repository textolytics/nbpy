
from influxdb import InfluxDBClient
import sys
import zmq
import simplejson as json
port = "5556"
if len(sys.argv) > 1:
    port = sys.argv[1]
    int(port)

if len(sys.argv) > 2:
    port1 = sys.argv[2]
    int(port1)

# Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)
topicfilter = "oanda_tick"
socket.setsockopt_string(zmq.SUBSCRIBE,topicfilter)
socket.setsockopt_string(zmq.SUBSCRIBE, "1")
print ("Collecting updates from weather server...")
socket.connect("tcp://localhost:%s" % port)

if len(sys.argv) > 2:
    socket.connect("tcp://localhost:%s" % port1)

# Subscribe to zipcode, default is NYC, 10001

# InfluxDB connections settings
host = '192.168.0.113'
port = 8086
user = 'oanda'
password = 'oanda'
dbname = 'tick'

myclient = InfluxDBClient(host, port, user, password, dbname,use_udp=False)




# Process 5 updates
total_value = 0
while True:
    response = socket.recv_string()
    topic, messagedata = response.split()
    instrument, time, bid, ask = messagedata.split('\x01')
    # msg = json.dumps(messagedata)
    # total_value += int(messagedata)
    print (topic,instrument, time, bid, ask)
    tick_json = [
        {
            "measurement": instrument,
            "tags": {
                "timestamp": time
            },
            "fields": {
                "bid": float(bid) ,
                "ask": float(ask)
            }
        }
    ]
    myclient.write_points ( tick_json , batch_size=500 , time_precision='u' )
print ("Average messagedata value for topic '%s' was %dF" % (topicfilter, total_value / update_nbr))
