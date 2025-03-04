import sys
import zmq
import zmsg

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
zsocket = zmsg.zsocket(socket)

print("Collecting updates from weather server...")
socket.connect("tcp://localhost:%s" % port)

if len(sys.argv) > 2:
    socket.connect("tcp://localhost:%s" % port1)

# Subscribe to zipcode, default is NYC, 10001
topicfilter = "10001"
socket.setsockopt(zmq.SUBSCRIBE, topicfilter.encode())

# Process 5 updates
total_value = 0
for update_nbr in range(5):
    topic, messagedata = zsocket.recv()
    total_value += messagedata
    print(topic, messagedata)

print("Average messagedata value for topic '%s' was %dF" %
      (topicfilter, total_value / update_nbr))