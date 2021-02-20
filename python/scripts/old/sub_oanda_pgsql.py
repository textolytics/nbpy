
import sys

# import httplib as http_client
import psycopg2
import psycopg2.extensions
import psycopg2.extras
import zmq

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

print ("Collecting updates from weather server...")
socket.connect("tcp://192.168.0.13:%s" % port)


def recorder_connect():
    try:
        conn=psycopg2.connect("host='192.168.0.120' port='5432' dbname='oanda' user='oanda' password='oanda'")
        conn.autocommit = True
        return conn
    except psycopg2.DatabaseError as e:
        print ("I am unable to connect to the database.")
        print ('Error %s' % e)
    return conn

def quote_recorder(instrument, timestamp, bid, ask):
    conn = recorder_connect()
    try:
        cur = conn.cursor()
        cur.execute('INSERT INTO oanda_tick (timestmp, instrument,  bid, ask)\
        VALUES (%s,%s,%s,%s);', (instrument, timestamp, bid, ask))
        # print (instrument, timestamp, bid, ask)
        # conn.commit()
        # cur.close()
        # conn.close()
        print (instrument, timestamp, bid, ask)

    except psycopg2.DatabaseError as e:
        print ("DB_ERROR:",'Error %s' % e)


while True:
    response = socket.recv_string()
    topic, messagedata = response.split(' ')
    # if topic == 'oanda_tick':
    instrument, time, bid, ask = messagedata.split('\x01')
    quote_recorder(instrument, time, bid, ask)
    # msg = json.dumps(messagedata)
    # total_value += int(messagedata)
#        print(topic, instrument, time, bid, ask)