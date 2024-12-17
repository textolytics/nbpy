import sys
import zmq
import psycopg2

port = "5559"
synthetic_instrument = "KR_EURUSD"
if len(sys.argv) > 1:
    port = sys.argv[1]
    int(port)

if len(sys.argv) > 2:
    port1 = sys.argv[2]
    int(port1)

# Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)
topicfilter = "kr_eurusd_tick"
socket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)
socket.setsockopt_string(zmq.SUBSCRIBE, "1")
print("Collecting updates from weather server...")
socket.connect("tcp://192.168.0.13:%s" % port)

if len(sys.argv) > 2:
    socket.connect("tcp://192.168.0.13:%s" % port1)

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

def quote_recorder(synthetic_instrument, instrument_t0, kraken_EURUSD_BID_5_t0, kraken_EURUSD_ASK_5_t0, instrument, kraken_EURUSD_BID_5_t1, kraken_EURUSD_ASK_5_t1, spread, spread_t_bid, spread_t_askk):
    conn = recorder_connect()
    try:
        cur = conn.cursor()
        print(synthetic_instrument, instrument_t0, kraken_EURUSD_BID_5_t0, kraken_EURUSD_ASK_5_t0, instrument, kraken_EURUSD_BID_5_t1, kraken_EURUSD_ASK_5_t1, spread, spread_t_bid, spread_t_ask)
        cur.execute('INSERT INTO synthetic (synthetic_instrument, instrument_t0, kraken_EURUSD_BID_5_t0, kraken_EURUSD_ASK_5_t0, instrument, kraken_EURUSD_BID_5_t1, kraken_EURUSD_ASK_5_t1, spread, spread_t_bid, spread_t_ask)\
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);', ( synthetic_instrument, instrument_t0, kraken_EURUSD_BID_5_t0, kraken_EURUSD_ASK_5_t0, instrument, kraken_EURUSD_BID_5_t1, kraken_EURUSD_ASK_5_t1, spread, spread_t_bid, spread_t_ask))
        # print (instrument, timestamp, bid, ask)
        # conn.commit()
        # cur.close()
        # conn.close()


    except psycopg2.DatabaseError as e:
        print("DB_ERROR:", 'Error %s' % e)


while True:
    response = socket.recv_string()
    topic, messagedata = response.split(' ')
    instrument_t0, kraken_EURUSD_BID_5_t0, kraken_EURUSD_ASK_5_t0, instrument, kraken_EURUSD_BID_5_t1, kraken_EURUSD_ASK_5_t1, spread, spread_t_bid, spread_t_ask = messagedata.split(
        '\x01')
    quote_recorder( synthetic_instrument, instrument_t0, kraken_EURUSD_BID_5_t0, kraken_EURUSD_ASK_5_t0, instrument, kraken_EURUSD_BID_5_t1, kraken_EURUSD_ASK_5_t1, spread, spread_t_bid, spread_t_ask )
    # msg = json.dumps(messagedata)
    # total_value += int(messagedata)
#        print(topic, instrument, time, bid, ask)