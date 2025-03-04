import zmq
import random
import sys
import time
import zmsg

port = "5556"
if len(sys.argv) > 1:
    port = sys.argv[1]
    int(port)

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:%s" % port)
zsocket = zmsg.zsocket(socket)

while True:
    topic = random.randrange(9999, 10005)
    messagedata = random.randrange(1, 215) - 80
    print("%d %d" % (topic, messagedata))
    zsocket.send(topic, messagedata)
    time.sleep(.2)