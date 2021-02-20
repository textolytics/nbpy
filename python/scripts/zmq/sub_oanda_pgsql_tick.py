#!/usr/bin/python3.5
import sys
import zmq
import requests
# import httplib as http_client
from optparse import OptionParser
import psycopg2
import psycopg2.extras
import psycopg2.extensions
import simplejson as json
from datetime import datetime
import simplejson as json
port = "5556"
if len(sys.argv) > 1:
    port = sys.argv[1]
    int(port)

# if len(sys.argv) > 2:
#     port1 = sys.argv[2]
#     int(port1)

# Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)
topicfilter = "oanda_tick"
socket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)
socket.setsockopt_string(zmq.SUBSCRIBE, "1")

print ("Collecting updates to pqsql from oanda")
socket.connect("tcp://localhost:%s" % port)


def recorder_connect():
    try:
        conn=psycopg2.connect("host='192.168.0.120' port='5432' dbname='oanda' user='oanda' password='oanda'")
        conn.autocommit = True
        # print(conn)
        return conn
    except psycopg2.DatabaseError as e:
        print("I am unable to connect to the database.")
        print('Error %s' % e)
    return conn

def quote_recorder(timestamp, instrument, bid, ask):
    conn = recorder_connect()
    try:
        cur = conn.cursor()
        cur.execute('INSERT INTO oanda_tick (timestmp, instrument,  bid, ask)\
        VALUES (%s,%s,%s,%s);', ( timestamp, instrument,bid, ask))
        # print (instrument, timestamp, bid, ask)
        # conn.commit()
        # cur.close()
        # conn.close()
        # print(instrument, timestamp, bid, ask)

    except psycopg2.DatabaseError as e:
        print("DB_ERROR:", 'Error %s' % e)


while True:
    response = socket.recv_string()
    topic, messagedata = response.split(' ')
    # if topic == 'oanda_tick':
    instrument, time, bid, ask = messagedata.split('\x01')
    quote_recorder( time, instrument,bid, ask)
    # msg = json.dumps(messagedata)
    # total_value += int(messagedata)
#        print(topic, instrument, time, bid, ask)