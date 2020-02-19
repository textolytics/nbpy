import ccs
import json
import sys
import zmq

# sub-socket client
sub_port = "5559"
sub_context = zmq.Context()
sub_socket = sub_context.socket(zmq.SUB)
sub_topicfilter = "kr_eurusd_tick"
sub_socket.setsockopt_string(zmq.SUBSCRIBE, sub_topicfilter)
sub_socket.setsockopt_string(zmq.SUBSCRIBE, "1")
print ("Collecting updates from weather server...")
sub_socket.connect("tcp://zmq.nb.lan:%s" % sub_port)

# pub-socket server
pub_port = "5560"
pub_context = zmq.Context()
pub_socket = pub_context.socket(zmq.PUB)
# 'kr_depth' = 'kr_depth'

# Update
# socket.setsockopt(zmq.ZMQ_IMMEDIATE, 1)
pub_socket.setsockopt(zmq.SNDBUF, 10240)
pub_socket.setsockopt(zmq.SNDHWM, 10000)
# socket.setsockopt(zmq.SWAP, 25000000)
pub_socket.bind("tcp://*:%s" % pub_port)

while True:
    response = sub_socket.recv_string()
    topic, messagedata = response.split(' ')
    instrument_t0, kraken_EURUSD_BID_5_t0 , kraken_EURUSD_ASK_5_t0 , instrument , kraken_EURUSD_BID_5_t1 , kraken_EURUSD_ASK_5_t1 , spread, spread_t_bid, spread_t_ask = messagedata.split('\x01')
    # print (messagedata)

    if float(spread_t_bid) < 0:

        if instrument_t0[-3:] == "EUR":
            instrument_t0_cross = instrument_t0[:-3] + "USD"
            # print (instrument_t0_cross)
        if instrument_t0[-3:] == "USD":
            instrument_t0_cross = instrument_t0[:-3] + "EUR"
            # print (instrument_t0_cross)

        response_instrument_t0 = ccs.kraken.public.getOrderBook(instrument_t0, 1)
        order_book_t0 = json.loads(response_instrument_t0)
        pub_socket.send_string("%s %s" % ('kr_depth', response_instrument_t0))

        response_instrument_t0_cross = ccs.kraken.public.getOrderBook(instrument_t0_cross, 1)
        order_book_t0_cross = json.loads(response_instrument_t0_cross)
        pub_socket.send_string("%s %s" % ('kr_depth', response_instrument_t0_cross))

        if instrument[-3:] == "EUR":
            instrument_t1_cross = instrument[:-3] + "USD"
            # print (instrument_t1_cross)
        if instrument[-3:] == "USD":
            instrument_t1_cross = instrument[:-3] + "EUR"
            # print (instrument_t1_cross)

        response_instrument_t1 = ccs.kraken.public.getOrderBook(instrument, 1)
        order_book_t1 = json.loads(response_instrument_t1)
        pub_socket.send_string("%s %s" % ('kr_depth', response_instrument_t1))

        response_instrument_t1_cross = ccs.kraken.public.getOrderBook(instrument_t1_cross, 1)
        order_book_t1_cross = json.loads(response_instrument_t1_cross)
        pub_socket.send_string("%s %s" % ('kr_depth', response_instrument_t1_cross))

        print(response_instrument_t0, response_instrument_t0_cross)
        print(response_instrument_t1, response_instrument_t1_cross)

    if float(spread_t_ask) < 0:

        if instrument_t0[-3:] == "EUR":
            instrument_t0_cross = instrument_t0[:-3] + "USD"
            # print (instrument_t0_cross)
        if instrument_t0[-3:] == "USD":
            instrument_t0_cross = instrument_t0[:-3] + "EUR"
            # print (instrument_t0_cross)

        response_instrument_t0 = ccs.kraken.public.getOrderBook(instrument_t0, 1)
        order_book_t0 = json.loads(response_instrument_t0)
        pub_socket.send_string("%s %s" % ('kr_depth', response_instrument_t0))

        response_instrument_t0_cross = ccs.kraken.public.getOrderBook(instrument_t0_cross, 1)
        order_book_t0_cross = json.loads(response_instrument_t0_cross)
        pub_socket.send_string("%s %s" % ('kr_depth', response_instrument_t0_cross))

        if instrument[-3:] == "EUR":
            instrument_t1_cross = instrument[:-3] + "USD"
            # print (instrument_t1_cross)
        if instrument[-3:] == "USD":
            instrument_t1_cross = instrument[:-3] + "EUR"
            # print (instrument_t1_cross)

        response_instrument_t1 = ccs.kraken.public.getOrderBook(instrument, 1)
        order_book_t1 = json.loads(response_instrument_t1)
        pub_socket.send_string("%s %s" % ('kr_depth', response_instrument_t1))

        response_instrument_t1_cross = ccs.kraken.public.getOrderBook(instrument_t1_cross, 1)
        order_book_t1_cross = json.loads(response_instrument_t1_cross)
        pub_socket.send_string("%s %s" % ('kr_depth', response_instrument_t1_cross))

        print(response_instrument_t0, response_instrument_t0_cross)
        print(response_instrument_t1, response_instrument_t1_cross)

    response_instrument_t0 = ccs.kraken.public.getOrderBook(instrument_t0, 1)
    # response = ccs.kraken.public.getOrderBook('XXBTZEUR', 5)
    order_book_t0 = json.loads(response_instrument_t0)
    pub_socket.send_string("%s %s" % ('kr_depth', response_instrument_t0))
    response_instrument_t1 = ccs.kraken.public.getOrderBook(instrument, 1)
    order_book_t1 = json.loads(response_instrument_t1)
    pub_socket.send_string("%s %s" % ('kr_depth', response_instrument_t1))
    print (str(response_instrument_t0))
    print (str(response_instrument_t1))
