import ccs
import zmq
import sys

port = "5558"
if len(sys.argv) > 1:
    port = sys.argv[1]
    int(port)

context = zmq.Context()
socket = context.socket(zmq.PUB)

# Update
socket.setsockopt(zmq.IMMEDIATE, 1)
socket.setsockopt(zmq.SNDBUF, 10240)
socket.setsockopt(zmq.SNDHWM, 10000)
# socket.setsockopt(zmq.SWAP, 25000000)
socket.bind("tcp://*:%s" % port)


# response = ccs.kraken.public.getOrderBook ( "XBTEUR" ,3)

topic = 'kraken_stakan'
socket.send_string ( "%s %s" % ('kraken_stakan' , ccs.kraken.public.getOrderBook ( "XBTEUR" ,3)) )

# print ( response )
