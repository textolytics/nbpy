#!/usr/bin/python3.5
from pyoanda import Client, PRACTICE, Order
import simplejson as json
import zmq

from oandapyV20 import API
from oandapyV20.exceptions import V20Error
from oandapyV20.endpoints.pricing import PricingStream

accountID = "101-004-3748257-001"
access_token="2b557bdd4fa3dee56c8a159ece012a48-5f5a29d25cb2e7ea1aaeba98f4bbca40"
instruments = "EUR_USD"

client = Client(
    environment=PRACTICE,
    account_id='9276489',
    access_token='2b557bdd4fa3dee56c8a159ece012a48-5f5a29d25cb2e7ea1aaeba98f4bbca40'
)


# Socket subscriber to topic "kr_eurusd_depth"
kr_eurusd_depth_port = "5561"
kr_eurusd_depth_context = zmq.Context()
kr_eurusd_depth_socket = kr_eurusd_depth_context.socket(zmq.SUB)
kr_eurusd_depth_topicfilter = "kr_eurusd_depth"
kr_eurusd_depth_socket.setsockopt_string(zmq.SUBSCRIBE, kr_eurusd_depth_topicfilter)
kr_eurusd_depth_socket.setsockopt_string(zmq.SUBSCRIBE, "1")
print("Collecting KR_EURUSD DEPTH updates from KRAKEN server...")
kr_eurusd_depth_socket.connect("tcp://zmq.nb.lan:%s" % kr_eurusd_depth_port)

# Socket subscriber to topic "oanda_tick"
oanda_tick_port = "5556"
oanda_tick_context = zmq.Context()
oanda_tick_socket = oanda_tick_context.socket(zmq.SUB)
oanda_tick_topicfilter = "EUR_USD"
oanda_tick_socket.setsockopt_string(zmq.SUBSCRIBE, oanda_tick_topicfilter)
oanda_tick_socket.setsockopt_string(zmq.SUBSCRIBE, "1")
print("Collecting TICK updates from OANDA server...")
oanda_tick_socket.connect("tcp://zmq.nb.lan:%s" % oanda_tick_port)



pip = float(0.00001)

def newOrder(instrument, p, bid, ask):
    units = 1000
    if instrument == 'XAG_USD':
        units = 1
    if instrument == 'XAU_USD':
        units = 1
    if instrument == 'BCO_USD':
        units = 1

    if p > ask:
        side = 'buy'
        if pip == 0.00001:
            price = round(((ask - bid) / 2 + bid), 5)
            takeProfit = round((ask + 0.0011*ask),5)
            stopLoss = round((bid - 0.001*ask),5)
            trailingStop = round((bid - 0.0007*ask),5)

    if p < bid:
        side = 'sell'
        if pip == 0.00001:
            price = round(((ask - bid) / 2 + bid), 5)
            takeProfit = round((bid - 0.0011 * bid), 5)
            stopLoss = round((ask + 0.001*bid), 5)
            trailingStop = round((ask + 0.0007*bid), 5)

    print(stopLoss, takeProfit)
    test_order = Order(
        instrument=instrument,
        units=units,
        side=side,
        type="market",
        stopLoss=stopLoss,
        #trailingStop=5,
        # distance= (2),
        takeProfit=takeProfit,
        price=price,
        # now = datetime.datetime.now()
        # expire = now + datetime.timedelta(days=1)
        expiry="GTC"
        # expiry=(datetime.datetime.now() + datetime.timedelta(days=50)).isoformat('T') + "Z"
        # expiry=(datetime.datetime.now() + datetime.timedelta(days=1))
        # expiry=datetime.datetime.now()
    )
    # print(instrument, takeProfit, stopLoss, trailingStop)
    return test_order

def position_open(instrument, prediction, bid, ask):
    try:
        try:
            position = client.get_position(instrument)
            print(position)
        except Exception as e:
            if str(e) == "OCode-404: Position not found":
                prediction = round(p, 5)
                test_order = newOrder(instrument, float(prediction), float(bid), float(ask))
                client.create_order(order=test_order)
            print(str(e))
    except Exception as e:
        print(str(e))

while True:
    kr_eurusd_depth_response = kr_eurusd_depth_socket.recv_string()
    topic, kr_eurusd_depth_messagedata = kr_eurusd_depth_response.split(' ')
    instrument_t0, kraken_EURUSD_BID_5_t0, kraken_EURUSD_ASK_5_t0, bid_t0, bid_volume_t0, ask_t0, ask_volume_t0, instrument_t1, kraken_EURUSD_BID_5_t1, kraken_EURUSD_ASK_5_t1, bid_t1, bid_volume_t1, ask_t1, ask_volume_t1, spread, spread_t_bid, spread_t_ask = kr_eurusd_depth_messagedata.split('\x01')
    print("KR_EURUSD DEPTH:", kr_eurusd_depth_messagedata)

    oanda_tick_response = oanda_tick_socket.recv_string()
    oanda_tick_topic, oanda_tick_messagedata = oanda_tick_response.split(' ')
    print (oanda_tick_messagedata)
    instrument, time, oanda_bid, oanda_ask = oanda_tick_messagedata.split('\x01')
    print("OANDA TICK:", oanda_tick_topic,oanda_tick_messagedata)

    spread_t_bid_f = float(spread_t_bid)
    if spread_t_bid_f <  -0.003:

        p = 1.21234
        position_open(oanda_tick_topic, p, oanda_bid, oanda_ask)
    spread_t_ask_f = float(spread_t_ask)
    if spread_t_ask_f <  -0.003:
        p = 1.01212
        position_open(oanda_tick_topic, p, oanda_bid, oanda_ask)

    if oanda_ask < kraken_EURUSD_BID_5_t1 :
        p = 1.021234
        position_open(oanda_tick_topic, p, oanda_bid, oanda_ask)
        print ("BUY ", instrument , oanda_ask , "SELL", instrument_t1,kraken_EURUSD_BID_5_t1,bid_t1)
    if oanda_bid > kraken_EURUSD_ASK_5_t1 :
        p = 1.212
        position_open(oanda_tick_topic, p, oanda_bid, oanda_ask)
        print ("SELL ", instrument , oanda_bid , "BUY", instrument_t1,kraken_EURUSD_ASK_5_t1,ask_t1)
