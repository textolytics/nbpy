#!/usr/bin/python3.5
from pyoanda import Client, PRACTICE, Order
import simplejson as json
import requests
import zmq
stream_domain = 'stream-fxpractice.oanda.com'
api_domain = 'api-fxpractice.oanda.com'
# access_token = '5b2e1521432ad31ef69270b682394010-4df302be03bbefb18ad70e457f3db869'
account_id = '3914094'
accountID = "101-004-3748257-001"
access_token="2b557bdd4fa3dee56c8a159ece012a48-5f5a29d25cb2e7ea1aaeba98f4bbca40"
instruments_string = "EUR_USD,USD_JPY,GBP_USD,USD_CAD,USD_CHF,AUD_USD,CAD_JPY,EU50_EUR,SPX500_USD,HK33_HKD,SG30_SGD,XAU_EUR,XAG_EUR,DE10YB_EUR,BCO_USD,WHEAT_USD,CORN_USD"
granularity = "S5"

def connect_to_api():
    try:
        s = requests.Session()
        ilist_Url = "https://" + api_domain + "/v3/accounts"
        headers = {'Authorization' : 'Bearer ' + access_token +
                   # 'X-Accept-Datetime-Format' : 'unix'
                   'Content-Type: application/json'

                   }
        instparams = {'accountId':accountID}
        ilist_Req = requests.Request('PUT', ilist_Url, headers = headers, params = instparams)
        ilist_pre = ilist_Req.prepare()
        ilist = s.send(ilist_pre, stream = True, verify = False)
        print (ilist.text)
        return ilist
    except Exception as e:
        s.close()
        print ("Caught exception when connecting to stream\n" + str(e))

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

while True:
    orders = connect_to_api()
    print(orders)

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
    # position_view("EUR_USD")
    #
    # if spread_t_bid_f < -0.003:
    #     p = 1.21234
    #     position_open(oanda_tick_topic, p, oanda_bid, oanda_ask)
    # spread_t_ask_f = float(spread_t_ask)
    # if spread_t_ask_f < -0.003:
    #     p = 1.01212
    #     position_open(oanda_tick_topic, p, oanda_bid, oanda_ask)
    #
    # if oanda_ask < kraken_EURUSD_BID_5_t1 :
    #     p = 1.021234
    #     position_open(oanda_tick_topic, p, oanda_bid, oanda_ask)
    #     print("BUY ", instrument , oanda_ask , "SELL", instrument_t1,kraken_EURUSD_BID_5_t1, bid_t1)
    # if oanda_bid > kraken_EURUSD_ASK_5_t1 :
    #     p = 1.212
    #     position_open(oanda_tick_topic, p, oanda_bid, oanda_ask)
    #     print("SELL ", instrument, oanda_bid, "BUY", instrument_t1,kraken_EURUSD_ASK_5_t1, ask_t1)
