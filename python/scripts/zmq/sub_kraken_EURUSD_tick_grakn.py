import datetime

import grakn
import zmq
from grakn import *
from grakn import *

port = "5559"
synthetic_instrument = "KR_EURUSD"

# Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)
topicfilter = "kr_eurusd_tick"
socket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)
socket.setsockopt_string(zmq.SUBSCRIBE, "1")
print("Collecting KR_EURUSD updates into grakn server...")
socket.connect("tcp://192.168.0.13:%s" % port)




# Grakn session start

client = grakn.Grakn(uri="192.168.0.154:48555")
session = client.session(keyspace="mykeyspace")
tx = session.transaction(grakn.TxType.WRITE)

def grakn_recorder(query):
    session = client.session(keyspace="mykeyspace")
    tx = session.transaction(grakn.TxType.WRITE)

    # Perform insert query that returns an iterator of ConceptMap of inserted concepts
    insert_iterator = tx.query(query)
    concepts = insert_iterator.collect_concepts()
    # print("Inserted a person with ID: {0}".format(concepts[0].id))
    # Don't forget to commit() to persist changes
    tx.commit()


#2018-09-27 20:19:03.817645 KR_EURUSD XZECZUSD 1.15956 1.17441 XETHZEUR 1.16386 1.16688 0.00302 0.01055 0.00732


while True:
    response = socket.recv_string()
    # now_timestamp = datetime.strptime(datetime.utcnow().isoformat(sep='T'), '%Y-%m-%dT%H:%M:%S.%f')

    topic, messagedata = response.split(' ')
    instrument_t0, kraken_EURUSD_BID_5_t0, kraken_EURUSD_ASK_5_t0, instrument, kraken_EURUSD_BID_5_t1, kraken_EURUSD_ASK_5_t1, spread, spread_t_bid, spread_t_ask = messagedata.split(
        '\x01')
    # msg = json.dumps(messagedata)
    # total_value += int(messagedata)
    now_m = datetime.datetime.now().strftime("%Y-%m-%d")
    now = str(now_m)
    # now.replace("\:", "-")
    print (now)


    # query = "insert isa alert has synthetic_instrument " + "\""+synthetic_instrument +"\""+ ", has instrument_t0 " + "\""+instrument_t0 + "\";"


    query = "insert $x isa alert has synthetic_instrument " + "\""+synthetic_instrument +"\""+ ", has instrument_t0 " + "\""+instrument_t0 +"\""+ ", has kraken_EURUSD_BID_5_t0 " + kraken_EURUSD_BID_5_t0 + ", has kraken_EURUSD_ASK_5_t0 " + kraken_EURUSD_ASK_5_t0 + ", has instrument "+ "\""+instrument+"\""+ ", has kraken_EURUSD_BID_5_t1 " +kraken_EURUSD_BID_5_t1+ ", has kraken_EURUSD_ASK_5_t1 " + kraken_EURUSD_ASK_5_t1+", has spread " + spread+ ", has spread_t_bid "+spread_t_bid+ ", has spread_t_ask "+ spread_t_ask+";"


    print(now, synthetic_instrument, instrument_t0, kraken_EURUSD_BID_5_t0, kraken_EURUSD_ASK_5_t0, instrument, kraken_EURUSD_BID_5_t1, kraken_EURUSD_ASK_5_t1, spread, spread_t_bid, spread_t_ask)
    print (query)
    grakn_recorder(query)

# define
#
# alert
# sub
# entity
# has
# now_timestamp
# has
# synthetic_instrument
# has
# instrument_t0
# has
# kraken_EURUSD_BID_5_t0
# has
# kraken_EURUSD_ASK_5_t0
# has
# instrument
# has
# kraken_EURUSD_BID_5_t1
# has
# kraken_EURUSD_ASK_5_t1
# has
# spread
# has
# spread_t_bid
# has
# spread_t_ask;
#
# now_timestamp
# sub
# attribute
# datatype
# date;
# synthetic_instrument
# sub
# attribute
# datatype
# string;
# instrument_t0
# sub
# attribute
# datatype
# string;
# kraken_EURUSD_BID_5_t0
# sub
# attribute
# datatype
# double;
# kraken_EURUSD_ASK_5_t0
# sub
# attribute
# datatype
# double;
# instrument
# sub
# attribute
# datatype
# string;
# kraken_EURUSD_BID_5_t1
# sub
# attribute
# datatype
# double;
# kraken_EURUSD_ASK_5_t1
# sub
# attribute
# datatype
# double;
# spread
# sub
# attribute
# datatype
# double;
# spread_t_bid
# sub
# attribute
# datatype
# double;
# spread_t_ask
# sub
# attribute
# datatype
# double;
