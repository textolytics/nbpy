import zmq
from jsonrpcserver import methods
from jsonrpcserver.response import NotificationResponse

socket = zmq.Context().socket(zmq.SUB)

@methods.add
def ping():
    return 'pong'

if __name__ == '__main__':
    socket.bind('tcp://*:5556')
    while True:
        request = socket.recv().decode()
        response = methods.dispatch(request)
        socket.send_string(str(response))

