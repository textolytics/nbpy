#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#

import time
import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://192.168.0.100:5555")

def zmq():
    try:
        while True:
            #  Wait for next request from client
            message = socket.recv()
            print("Received request: %s" % message)

            #  Do some 'work'
            # time.sleep(1)

            #  Send reply back to client
            socket.send(b"World")
    except Exception as e:
        print str(e)

zmq()