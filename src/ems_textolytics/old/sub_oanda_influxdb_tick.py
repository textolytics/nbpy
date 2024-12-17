from influxdb import InfluxDBClient
import sys
import zmq
import simplejson as json

# Socket to talk to server
port = "5556"
context = zmq.Context()
socket = context.socket(zmq.SUB)
topicfilter = "oanda_tick"
socket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)
socket.setsockopt_string(zmq.SUBSCRIBE, "1")

print ("Collecting updates from oanda_tick topic...")
socket.connect("tcp://localhost:%s" % port)

# InfluxDB connections settings
host = '192.168.0.33'
port = 8086
user = 'zmq'
password = 'zmq'
dbname = 'tick'

myclient = InfluxDBClient(host, port, user, password, dbname, use_udp=False)

# Process 5 updates
total_value = 0
while True:
    response = socket.recv_string()
    topic, messagedata = response.split(' ')
    # if topic == 'oanda_tick':
    instrument, time, bid, ask = messagedata.split('\x01')
    # msg = json.dumps(messagedata)
    # total_value += int(messagedata)
#        print(topic, instrument, time, bid, ask)
    tick_json = [
        {
            "measurement": 'tick',
            "tags": {
                "instrument": instrument
            },
            "fields": {
                "bid": float(bid),
                "ask": float(ask)
            }
        }
    ]
    myclient.write_points (tick_json , batch_size=500, time_precision='ms')
    print (instrument, time, bid, ask)
    # tick_line= str(instrument)+" timestamp="+ str(time)+" bid=" +str(bid) + " ask="+str(ask)
    # print (tick_line)
    # try:
    #
    #     myclient.write_points (tick_line,protocol='line')
    # except InfluxDBClient.Exception as e:
    #     print (str(e))

    # print ( tick_line )
    # myclient.write_points (tick_json,protocol='json')
    # print (instrument, time, bid, ask)
# print ("Average messagedata value for topic '%s' was %dF" % (topicfilter, total_value / update_nbr))
