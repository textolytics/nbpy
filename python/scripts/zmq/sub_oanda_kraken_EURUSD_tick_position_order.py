#!/usr/bin/python3.5
from pyoanda import Client, PRACTICE, Order
import simplejson as json
import zmq

client = Client(
    environment=PRACTICE,
    account_id='9276489',
    access_token='2b557bdd4fa3dee56c8a159ece012a48-5f5a29d25cb2e7ea1aaeba98f4bbca40'
)

# Socket subscriber to topic "kr_eurusd_tick"
kr_eurusd_tick_port = "5559"
kr_eurusd_tick_context = zmq.Context()
kr_eurusd_tick_socket = kr_eurusd_tick_context.socket(zmq.SUB)
kr_eurusd_tick_topicfilter = "kr_eurusd_tick"
kr_eurusd_tick_socket.setsockopt_string(zmq.SUBSCRIBE, kr_eurusd_tick_topicfilter)
kr_eurusd_tick_socket.setsockopt_string(zmq.SUBSCRIBE, "1")

print("Collecting KR_EURUSD TICK updates from KRAKEN server...")
kr_eurusd_tick_socket.connect("tcp://192.168.0.13:%s" % kr_eurusd_tick_port)

# Socket subscriber to topic "oanda_tick"
oanda_tick_port = "5562"
oanda_tick_topicfilter_eurjpy = "EUR_JPY"
oanda_tick_topicfilter_usdjpy = "USD_JPY"

oanda_tick_context = zmq.Context()
oanda_eurjpy_tick_socket = oanda_tick_context.socket(zmq.SUB)
oanda_usdjpy_tick_socket = oanda_tick_context.socket(zmq.SUB)

oanda_eurjpy_tick_socket.setsockopt_string(zmq.SUBSCRIBE, oanda_tick_topicfilter_eurjpy)
oanda_eurjpy_tick_socket.setsockopt_string(zmq.SUBSCRIBE, "1")

oanda_usdjpy_tick_socket.setsockopt_string(zmq.SUBSCRIBE, oanda_tick_topicfilter_usdjpy)
oanda_usdjpy_tick_socket.setsockopt_string(zmq.SUBSCRIBE, "1")

print("Collecting TICK updates from OANDA server...")
oanda_usdjpy_tick_socket.connect("tcp://localhost:%s" % oanda_tick_port)
oanda_eurjpy_tick_socket.connect("tcp://localhost:%s" % oanda_tick_port)

def newOrder(instrument, p, bid, ask):
    units = 1000
    if instrument == 'XAG_USD':
        units = 1
    if instrument == 'XAU_USD':
        units = 1
    if instrument == 'BCO_USD':
        units = 1

    if oanda_usdjpy_topic[-3:] == "JPY":
        pip = float('0.001')
    else:
        pip = float('0.00001')

    if p > ask:
        side = 'buy'

        if pip == 0.00001:
            price = round(((ask - bid) / 2 + bid), 5)
            takeProfit = round((ask + 0.0005*ask),5)
            stopLoss = round((bid - 0.0005*ask),5)
            trailingStop = round((bid - 0.0007*ask),5)

        if pip == 0.001:
            price = round(((ask - bid) / 2 + bid), 3)
            takeProfit = round((ask + 0.0007*ask),3)
            stopLoss = round((bid - 0.0003*ask),3)
            trailingStop = round((bid - 0.0007*ask),3)

        if instrument =="USD_JPY":
            jpy_exposure = 1000 * float(oanda_eurjpy_bid)
            units = int(round(jpy_exposure/float(oanda_usdjpy_ask),0))
            print(units)
    if p < bid:
        side = 'sell'

        if pip == 0.00001:
            price = round(((ask - bid) / 2 + bid), 5)
            takeProfit = round((bid - 0.0007 * bid), 5)
            stopLoss = round((ask + 0.0003*bid), 5)
            trailingStop = round((ask + 0.0007*bid), 5)

        if pip == 0.001:
            price = round(((ask - bid) / 2 + bid), 3)
            takeProfit = round((bid - 0.0007 * bid), 3)
            stopLoss = round((ask + 0.0003*bid), 3)
            trailingStop = round((ask + 0.0007*bid), 3)

        if  instrument =="USD_JPY":
            jpy_exposure = 1000 * float(oanda_eurjpy_ask)
            units = int(round(jpy_exposure/float(oanda_usdjpy_bid),0))
            print (units)

    print(stopLoss, takeProfit)
    test_order = Order(
        instrument=instrument,
        units=units,
        side=side,
        type="market",
        stopLoss=stopLoss,
        trailingStop=20,
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
    kr_eurusd_tick_response = kr_eurusd_tick_socket.recv_string()
    kr_eurusd_tick_topic, kr_eurusd_tick_messagedata = kr_eurusd_tick_response.split(' ')
    instrument_t0, kraken_EURUSD_BID_5_t0, kraken_EURUSD_ASK_5_t0, instrument, kraken_EURUSD_BID_5_t1, kraken_EURUSD_ASK_5_t1, spread, spread_t_bid, spread_t_ask = kr_eurusd_tick_messagedata.split('\x01')
    spread_t_bid_f = float(spread_t_bid)
    spread_t_ask_f = float(spread_t_ask)
    print("KR_EURUSD TICK:", kr_eurusd_tick_messagedata)

    oanda_eurjpy_tick_response = oanda_eurjpy_tick_socket.recv_string()
    oanda_eurjpy_topic, oanda_eurjpu_tick_messagedata = oanda_eurjpy_tick_response.split(' ')
    oanda_eurjpy_timestamp, oanda_eurjpy_bid, oanda_eurjpy_ask = oanda_eurjpu_tick_messagedata.split('\x01')
    print("OANDA TICK:", oanda_eurjpy_topic, oanda_eurjpu_tick_messagedata)

    oanda_usdjpy_tick_response = oanda_usdjpy_tick_socket.recv_string()
    oanda_usdjpy_topic, oanda_usdjpy_tick_messagedata = oanda_usdjpy_tick_response.split(' ')
    oanda_usdjpy_timestamp, oanda_usdjpy_bid, oanda_usdjpy_ask = oanda_usdjpy_tick_messagedata.split('\x01')
    print("OANDA TICK:", oanda_usdjpy_topic, oanda_usdjpy_tick_messagedata)

    if spread_t_bid_f < - 0.0005:
        p = 0
        position_open(oanda_usdjpy_topic, p, oanda_usdjpy_bid, oanda_usdjpy_ask)
        p = 500
        position_open(oanda_eurjpy_topic, p, oanda_eurjpy_bid, oanda_eurjpy_ask)

    if spread_t_ask_f < - 0.0005:
        p = 500
        position_open(oanda_usdjpy_topic, p, oanda_usdjpy_bid, oanda_usdjpy_ask)
        p = 0
        position_open(oanda_eurjpy_topic, p, oanda_eurjpy_bid, oanda_eurjpy_ask)