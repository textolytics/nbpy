import re
import json

try:
    import msgpack
    MPACK = True
except ImportError:
    MPACK = False

UNPACK = re.compile(b'(.*)\x00(.*)').match


class Packer:
    def __init__(self, packer=None):
        if packer is None:
            self.packer = msgpack if MPACK else json
        else:
            self.packer = packer

    def loads(self, data):
        name, data = UNPACK(data).groups()
        return name.decode(), self.packer.loads(data)

    def dumps(self, name, data):
        return b'\x00'.join((name.encode(), self.packer.dumps(data)))


class zsocket(Packer):
    '''Layers on top of an existing zmq socket to give better
    data packing
    Names must NOT use the `\x00` character'''
    def __init__(self, socket, packer=None):
        self.socket = socket
        super().__init__(packer)

    def send(self, name, data):
        self.socket.send(self.dumps(str(name), data))

    def recv(self):
        return self.loads(self.socket.recv())
