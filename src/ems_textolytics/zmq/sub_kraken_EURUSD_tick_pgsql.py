import sys
import zmq
import psycopg2
from datetime import datetime
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
print("Collecting KR_EURUSD updates into pgsql server...")
socket.connect("tcp://localhost:%s" % port)

if len(sys.argv) > 2:
    socket.connect("tcp://localhost:%s" % port1)

def recorder_connect():
    try:
        conn=psycopg2.connect("host='192.168.0.120' port='5432' dbname='kraken' user='kraken' password='kraken'")
        conn.autocommit = True
        # print(conn)
        return conn
    except psycopg2.DatabaseError as e:
        print("I am unable to connect to the database.")
        print('Error %s' % e)
    return conn

def quote_recorder(sub_kraken_eurusd_tick_pgsql_timestamp, synthetic_instrument, instrument_t0, kraken_EURUSD_BID_5_t0, kraken_EURUSD_ASK_5_t0, instrument, kraken_EURUSD_BID_5_t1, kraken_EURUSD_ASK_5_t1, spread, spread_t_bid, spread_t_askk):
    conn = recorder_connect()
    try:
        cur = conn.cursor()
        # print(sub_kraken_eurusd_tick_pgsql_timestamp, synthetic_instrument, instrument_t0, kraken_EURUSD_BID_5_t0, kraken_EURUSD_ASK_5_t0, instrument, kraken_EURUSD_BID_5_t1, kraken_EURUSD_ASK_5_t1, spread, spread_t_bid, spread_t_ask)
        cur.execute('INSERT INTO synthetic(sub_kraken_eurusd_tick_pgsql_timestamp, synthetic_instrument, instrument_t0, kraken_eurusd_bid_5_t0, kraken_eurusd_ask_5_t0, instrument, kraken_eurusd_bid_5_t1, kraken_eurusd_ask_5_t1, spread, spread_t_bid, spread_t_ask)\
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);', (sub_kraken_eurusd_tick_pgsql_timestamp, synthetic_instrument, instrument_t0, kraken_EURUSD_BID_5_t0, kraken_EURUSD_ASK_5_t0, instrument, kraken_EURUSD_BID_5_t1, kraken_EURUSD_ASK_5_t1, spread, spread_t_bid, spread_t_ask))
        # print (instrument, timestamp, bid, ask)
        # conn.commit()
        # cur.close()
        # conn.close()


    except psycopg2.DatabaseError as e:
        print("DB_ERROR:", 'Error %s' % e)


while True:
    response = socket.recv_string()
    now_timestamp = datetime.strptime(datetime.utcnow().isoformat(sep='T'), '%Y-%m-%dT%H:%M:%S.%f')

    topic, messagedata = response.split(' ')
    instrument_t0, kraken_EURUSD_BID_5_t0, kraken_EURUSD_ASK_5_t0, instrument, kraken_EURUSD_BID_5_t1, kraken_EURUSD_ASK_5_t1, spread, spread_t_bid, spread_t_ask = messagedata.split(
        '\x01')
    quote_recorder(now_timestamp, synthetic_instrument, instrument_t0, kraken_EURUSD_BID_5_t0, kraken_EURUSD_ASK_5_t0, instrument, kraken_EURUSD_BID_5_t1, kraken_EURUSD_ASK_5_t1, spread, spread_t_bid, spread_t_ask )
    # msg = json.dumps(messagedata)
    # total_value += int(messagedata)
    # print(now_timestamp, synthetic_instrument, instrument_t0, kraken_EURUSD_BID_5_t0, kraken_EURUSD_ASK_5_t0, instrument, kraken_EURUSD_BID_5_t1, kraken_EURUSD_ASK_5_t1, spread, spread_t_bid, spread_t_ask)