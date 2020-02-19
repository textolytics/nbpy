import zmq

context = zmq.Context()
socket = context.socket( zmq.SUB)
socket.connect("tcp://127.0.0.1:5550")
socket.setsockopt_string(zmq.SUBSCRIBE, "")

socket.setsockopt( zmq.RCVBUF, 1000)
while True:
  msg = socket.recv()
  print ("GOT: ", msg)