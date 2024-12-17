import sys
import zmq
from influxdb import InfluxDBClient

# Socket to talk to server
port = "5561"
context = zmq.Context()
socket = context.socket(zmq.SUB)
topicfilter = "kr_eurusd_depth"
socket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)
socket.setsockopt_string(zmq.SUBSCRIBE, "1")
print("Collecting updates from kr_eurusd_depth")
socket.connect("tcp://zmq.nb.lan:%s" % port)

# InfluxDB connections settings
host = 'tick.nb.lan'
tcp_port = 8086
udp_port = 8189
user = 'zmq'
password = 'zmq'
dbname = 'tick'
myclient_tcp = InfluxDBClient(host, tcp_port, user, password, dbname, use_udp=False)
# myclient_udp = InfluxDBClient(host, udp_port, user, password, dbname, use_udp=True)


while True:
    response = socket.recv_string()
    topic, messagedata = response.split(' ')

    instrument_t0, kraken_EURUSD_BID_5_t0, kraken_EURUSD_ASK_5_t0, bid_t0, bid_volume_t0, ask_t0, ask_volume_t0, instrument_t1, kraken_EURUSD_BID_5_t1, kraken_EURUSD_ASK_5_t1, bid_t1, bid_volume_t1, ask_t1, ask_volume_t1, spread, spread_t_bid, spread_t_ask = messagedata.split('\x01')

    print ("DEPTH", instrument_t0, kraken_EURUSD_BID_5_t0, kraken_EURUSD_ASK_5_t0, bid_t0, bid_volume_t0, ask_t0, ask_volume_t0, instrument_t1, kraken_EURUSD_BID_5_t1, kraken_EURUSD_ASK_5_t1, bid_t1, bid_volume_t1, ask_t1, ask_volume_t1, float(spread), float(spread_t_bid), float(spread_t_ask),)

    depth_json = [
        {
            "measurement": 'MESSAGES',
            "tags": {
                "MSGTYPE": "DEPTH",
                "instrument": "KR_EURUSD_DEPTH",
                "instrument_t0": instrument_t0,
                "instrument_t1": instrument_t1,
            },
            "fields": {
                "instrument_t0": instrument_t0,
                "instrument_t1": instrument_t1,
                "kraken_EURUSD_depth_BID_5_t0": float ( kraken_EURUSD_BID_5_t0 ),
                "kraken_EURUSD_depth_ASK_5_t0": float ( kraken_EURUSD_ASK_5_t0 ),
                "bid_t0": float(bid_t0),
                "bid_volume_t0": float(bid_volume_t0),
                "ask_t0": float(ask_t0),
                "ask_volume_t0": float(ask_volume_t0),
                "kraken_EURUSD_depth_BID_5_t1": float ( kraken_EURUSD_BID_5_t1 ),
                "kraken_EURUSD_depth_ASK_5_t1": float (kraken_EURUSD_ASK_5_t1 ),
                "bid_t1": float(bid_t1),
                "bid_volume_t1": float(bid_volume_t1),
                "ask_t1": float(ask_t1),
                "ask_volume_t1": float(ask_volume_t1),
                "spread_depth_t_bid": float(spread_t_bid),
                "spread_depth_t_ask": float(spread_t_ask),
                "spread_depth": float(spread)
            }
        }
    ]
    myclient_tcp.write_points(depth_json, time_precision='ms')

    if float(spread_t_ask) < 0:

        if instrument_t0[-3:] == "EUR":
            instrument_t0_cross = instrument_t0[:-3] + "USD"
            instrument_t0_cross_bid = round(float(kraken_EURUSD_BID_5_t0)*float(ask_t0), 5)
            instrument_t0_cross_ask = round(float(kraken_EURUSD_ASK_5_t0)*float(bid_t0), 5)

        if instrument_t0[-3:] == "USD":
            instrument_t0_cross = instrument_t0[:-3] + "EUR"
            instrument_t0_cross_bid = round(float(bid_t0)/float(kraken_EURUSD_ASK_5_t0), 5)
            instrument_t0_cross_ask = round(float(ask_t0)/float(kraken_EURUSD_BID_5_t0), 5)

        if instrument_t1[-3:] == "EUR":
            instrument_t1_cross = instrument_t1[:-3] + "USD"
            instrument_t1_cross_bid = round(float(kraken_EURUSD_BID_5_t1)*float(ask_t1), 5)
            instrument_t1_cross_ask = round(float(kraken_EURUSD_ASK_5_t1)*float(bid_t1), 5)

        if instrument_t1[-3:] == "USD":
            instrument_t1_cross = instrument_t1[:-3] + "EUR"
            instrument_t1_cross_bid = round(float(bid_t1)/float(kraken_EURUSD_ASK_5_t1), 5)
            instrument_t1_cross_ask = round(float(ask_t1)/float(kraken_EURUSD_BID_5_t1), 5)

        print ("SNAPSHOT",instrument_t0, bid_t0, ask_t0, instrument_t0_cross, instrument_t0_cross_bid,
               instrument_t0_cross_ask, instrument_t1, bid_t1, ask_t1, instrument_t1_cross, instrument_t1_cross_bid, instrument_t1_cross_ask)
        snapshot_json = [
            {
                "measurement": 'MESSAGES',
                "tags": {
                    "MSGTYPE": "SNAPSHOT",
                    "instrument": "KR_EURUSD_DEPTH",
                    "instrument_t0": instrument_t0,
                    "instrument_t0_cross": instrument_t0_cross,
                    "instrument_t1": instrument_t1,
                    "instrument_t1_cross": instrument_t1_cross,
                },
                "fields": {
                    "kraken_EURUSD_depth_BID_5_t0": float ( kraken_EURUSD_BID_5_t0 ),
                    "kraken_EURUSD_depth_ASK_5_t0": float ( kraken_EURUSD_ASK_5_t0 ),
                    "instrument_t0": instrument_t0,
                    "bid_t0": float(bid_t0),
                    "bid_volume_t0": float(bid_volume_t0),
                    "ask_t0": float(ask_t0),
                    "ask_volume_t0": float(ask_volume_t0),
                    "instrument_t0_cross": instrument_t0_cross,
                    "bid_t0_cross" : float(instrument_t0_cross_bid),
                    "ask_t0_cross" : float(instrument_t0_cross_ask),
                    "kraken_EURUSD_depth_BID_5_t1": float ( kraken_EURUSD_BID_5_t1 ),
                    "kraken_EURUSD_depth_ASK_5_t1": float (kraken_EURUSD_ASK_5_t1 ),
                    "instrument_t1": instrument_t1,
                    "bid_t1": float(bid_t1),
                    "bid_volume_t1": float(bid_volume_t1),
                    "ask_t1": float(ask_t1),
                    "ask_volume_t1": float(ask_volume_t1),
                    "instrument_t1_cross": instrument_t1_cross,
                    "bid_t1_cross" : float(instrument_t1_cross_bid),
                    "ask_t1_cross" : float(instrument_t1_cross_ask),
                    "spread_depth_t_bid": float(spread_t_bid),
                    "spread_depth_t_ask": float(spread_t_ask),
                    "spread_depth": float(spread)
                }
            }
        ]
        myclient_tcp.write_points(snapshot_json, time_precision='ms')

        if instrument_t1[-3:] == "EUR":
            print("BASKET","EURUSD ASK:", kraken_EURUSD_ASK_5_t1, "SELL",instrument_t1, bid_t1,"BUY",
                  instrument_t1_cross, \
                  instrument_t1_cross_ask,
                  "EURUSD BID:",kraken_EURUSD_BID_5_t0,"BUY", instrument_t0, ask_t0,"SELL", float(instrument_t1_cross), float(instrument_t1_cross_bid))

            basket_json = [
                {
                    "measurement": 'MESSAGES',
                    "tags": {
                        "MSGTYPE": "BASKET",
                        "instrument": "KR_EURUSD_DEPTH",
                        "SIDE_T0": "BUY",
                        "instrument_t0": instrument_t0,
                        "SIDE_CROSS_T0": "SELL" ,
                        "instrument_t0_cross": instrument_t0_cross,
                        "SIDE_T1": "SELL",
                        "instrument_t1": instrument_t1,
                        "SIDE_CROSS_T1":"BUY",
                        "instrument_t1_cross": instrument_t1_cross,
                    },
                    "fields": {
                        "kraken_EURUSD_depth_BID_5_t0": float ( kraken_EURUSD_BID_5_t0 ),
                        "kraken_EURUSD_depth_ASK_5_t0": float ( kraken_EURUSD_ASK_5_t0 ),
                        "SIDE_T0": "BUY",
                        "instrument_t0": instrument_t0,
                        "bid_t0": float(bid_t0),
                        "bid_volume_t0": float(bid_volume_t0),
                        "ask_t0": float(ask_t0),
                        "ask_volume_t0": float(ask_volume_t0),
                        "SIDE_CROSS_T0": "SELL" ,
                        "instrument_t0_cross": instrument_t0_cross,
                        "bid_t0_cross" : float(instrument_t0_cross_bid),
                        "ask_t0_cross" : float(instrument_t0_cross_ask),
                        "kraken_EURUSD_depth_BID_5_t1": float ( kraken_EURUSD_BID_5_t1 ),
                        "kraken_EURUSD_depth_ASK_5_t1": float (kraken_EURUSD_ASK_5_t1 ),
                        "SIDE_T1": "SELL",
                        "instrument_t1": instrument_t1,
                        "bid_t1": float(bid_t1),
                        "bid_volume_t1": float(bid_volume_t1),
                        "ask_t1": float(ask_t1),
                        "ask_volume_t1": float(ask_volume_t1),
                        "SIDE_CROSS_T1":"BUY",
                        "instrument_t1_cross": instrument_t1_cross,
                        "bid_t1_cross" : float(instrument_t1_cross_bid),
                        "ask_t1_cross" : float(instrument_t1_cross_ask),
                        "spread_depth_t_bid": float(spread_t_bid),
                        "spread_depth_t_ask": float(spread_t_ask),
                        "spread_depth": float(spread)
                    }
                }
            ]
            myclient_tcp.write_points(basket_json, time_precision='ms')

        if instrument_t1[-3:] == "USD":
            print("BASKET","EURUSD ASK:", kraken_EURUSD_ASK_5_t1, "BUY",instrument_t1, ask_t1,"SELL",
                  instrument_t1_cross, instrument_t1_cross_bid, "EURUSD BID:", kraken_EURUSD_BID_5_t0, "SELL", instrument_t0, bid_t0,"BUY", instrument_t0_cross, instrument_t0_cross_ask  )
            basket_json = [
                {
                    "measurement": 'MESSAGES',
                    "tags": {
                        "MSGTYPE": "BASKET",
                        "instrument": "KR_EURUSD_DEPTH",
                        "SIDE_T0": "SELL",
                        "instrument_t0": instrument_t0,
                        "SIDE_CROSS_T0": "BUY" ,
                        "instrument_t0_cross": instrument_t0_cross,
                        "SIDE_T1": "BUY",
                        "instrument_t1": instrument_t1,
                        "SIDE_CROSS_T1":"SELL",
                        "instrument_t1_cross": instrument_t1_cross,
                    },
                    "fields": {
                        "kraken_EURUSD_depth_BID_5_t0": float ( kraken_EURUSD_BID_5_t0 ),
                        "kraken_EURUSD_depth_ASK_5_t0": float ( kraken_EURUSD_ASK_5_t0 ),
                        "SIDE_T0": "SELL",
                        "instrument_t0": instrument_t0,
                        "bid_t0": float(bid_t0),
                        "bid_volume_t0": float(bid_volume_t0),
                        "ask_t0": float(ask_t0),
                        "ask_volume_t0": float(ask_volume_t0),
                        "SIDE_CROSS_T0": "BUY" ,
                        "instrument_t0_cross": instrument_t0_cross,
                        "bid_t0_cross" : float(instrument_t0_cross_bid),
                        "ask_t0_cross" : float(instrument_t0_cross_ask),
                        "kraken_EURUSD_depth_BID_5_t1": float ( kraken_EURUSD_BID_5_t1 ),
                        "kraken_EURUSD_depth_ASK_5_t1": float (kraken_EURUSD_ASK_5_t1 ),
                        "SIDE_T1": "BUY",
                        "instrument_t1": instrument_t1,
                        "bid_t1": float(bid_t1),
                        "bid_volume_t1": float(bid_volume_t1),
                        "ask_t1": float(ask_t1),
                        "ask_volume_t1": float(ask_volume_t1),
                        "SIDE_CROSS_T1":"SELL",
                        "instrument_t1_cross": instrument_t1_cross,
                        "bid_t1_cross" : float(instrument_t1_cross_bid),
                        "ask_t1_cross" : float(instrument_t1_cross_ask),


                        "spread_depth_t_bid": float(spread_t_bid),
                        "spread_depth_t_ask": float(spread_t_ask),
                        "spread_depth": float(spread)
                    }
                }
            ]
            myclient_tcp.write_points(basket_json, time_precision='ms')

    if float(spread_t_bid) < 0:

            if instrument_t0[-3:] == "EUR":
                instrument_t0_cross = instrument_t0[:-3] + "USD"
                instrument_t0_cross_bid = round(float(kraken_EURUSD_BID_5_t0)*float(ask_t0), 5)
                instrument_t0_cross_ask = round(float(kraken_EURUSD_ASK_5_t0)*float(bid_t0), 5)

            if instrument_t0[-3:] == "USD":
                instrument_t0_cross = instrument_t0[:-3] + "EUR"
                instrument_t0_cross_bid = round(float(bid_t0)/float(kraken_EURUSD_ASK_5_t0), 5)
                instrument_t0_cross_ask = round(float(ask_t0)/float(kraken_EURUSD_BID_5_t0), 5)

            if instrument_t1[-3:] == "EUR":
                instrument_t1_cross = instrument_t1[:-3] + "USD"
                instrument_t1_cross_bid = round(float(kraken_EURUSD_BID_5_t1)*float(ask_t1), 5)
                instrument_t1_cross_ask = round(float(kraken_EURUSD_ASK_5_t1)*float(bid_t1), 5)

            if instrument_t1[-3:] == "USD":
                instrument_t1_cross = instrument_t1[:-3] + "EUR"
                instrument_t1_cross_bid = round(float(bid_t1)/float(kraken_EURUSD_ASK_5_t1), 5)
                instrument_t1_cross_ask = round(float(ask_t1)/float(kraken_EURUSD_BID_5_t1), 5)

            print ("SNAPSHOT",instrument_t0, bid_t0, ask_t0, instrument_t0_cross, instrument_t0_cross_bid,
                   instrument_t0_cross_ask, instrument_t1, bid_t1, ask_t1, instrument_t1_cross, instrument_t1_cross_bid, instrument_t1_cross_ask)

            tick_json = [
                {
                    "measurement": 'MESSAGES',
                    "tags": {
                        "MSGTYPE": "SNAPSHOT",
                        "instrument": "KR_EURUSD_DEPTH",
                        "instrument_t0": instrument_t0,
                        "instrument_t0_cross": instrument_t0_cross,
                        "instrument_t1": instrument_t1,
                        "instrument_t1_cross": instrument_t1_cross,
                    },
                    "fields": {
                        "kraken_EURUSD_depth_BID_5_t0": float ( kraken_EURUSD_BID_5_t0 ),
                        "kraken_EURUSD_depth_ASK_5_t0": float ( kraken_EURUSD_ASK_5_t0 ),
                        "instrument_t0": instrument_t0,
                        "bid_t0": float(bid_t0),
                        "bid_volume_t0": float(bid_volume_t0),
                        "ask_t0": float(ask_t0),
                        "ask_volume_t0": float(ask_volume_t0),
                        "instrument_t0_cross": instrument_t0_cross,
                        "bid_t0_cross" : float(instrument_t0_cross_bid),
                        "ask_t0_cross" : float(instrument_t0_cross_ask),
                        "kraken_EURUSD_depth_BID_5_t1": float ( kraken_EURUSD_BID_5_t1 ),
                        "kraken_EURUSD_depth_ASK_5_t1": float (kraken_EURUSD_ASK_5_t1 ),
                        "instrument_t1": instrument_t1,
                        "bid_t1": float(bid_t1),
                        "bid_volume_t1": float(bid_volume_t1),
                        "ask_t1": float(ask_t1),
                        "ask_volume_t1": float(ask_volume_t1),
                        "instrument_t1_cross": instrument_t1_cross,
                        "bid_t1_cross" : float(instrument_t1_cross_bid),
                        "ask_t1_cross" : float(instrument_t1_cross_ask),
                        "spread_depth_t_bid": float(spread_t_bid),
                        "spread_depth_t_ask": float(spread_t_ask),
                        "spread_depth": float(spread)
                    }
                }
            ]
            myclient_tcp.write_points(tick_json, time_precision='ms')
            if instrument_t1[-3:] == "EUR":
                print("BASKET","EURUSD ASK:", kraken_EURUSD_ASK_5_t0, "SELL",instrument_t0, bid_t0,"BUY", instrument_t0_cross, instrument_t0_cross_ask, "EURUSD BID:",kraken_EURUSD_BID_5_t1,"BUY", instrument_t1, ask_t1,"SELL", float(instrument_t1_cross), float(instrument_t1_cross_bid))
            basket_json = [
                {
                    "measurement": 'MESSAGES',
                    "tags": {
                        "MSGTYPE": "BASKET",
                        "instrument": "KR_EURUSD_DEPTH",
                        "SIDE_T0": "SELL",
                        "instrument_t0": instrument_t0,
                        "SIDE_CROSS_T0": "BUY" ,
                        "instrument_t0_cross": instrument_t0_cross,
                        "SIDE_T1": "BUY",
                        "instrument_t1": instrument_t1,
                        "SIDE_CROSS_T1":"SELL",
                        "instrument_t1_cross": instrument_t1_cross,
                    },
                    "fields": {
                        "kraken_EURUSD_depth_BID_5_t0": float ( kraken_EURUSD_BID_5_t0 ),
                        "kraken_EURUSD_depth_ASK_5_t0": float ( kraken_EURUSD_ASK_5_t0 ),
                        "SIDE_T0": "SELL",
                        "instrument_t0": instrument_t0,
                        "bid_t0": float(bid_t0),
                        "bid_volume_t0": float(bid_volume_t0),
                        "ask_t0": float(ask_t0),
                        "ask_volume_t0": float(ask_volume_t0),
                        "SIDE_CROSS_T0": "BUY" ,
                        "instrument_t0_cross": instrument_t0_cross,
                        "bid_t0_cross" : float(instrument_t0_cross_bid),
                        "ask_t0_cross" : float(instrument_t0_cross_ask),
                        "kraken_EURUSD_depth_BID_5_t1": float ( kraken_EURUSD_BID_5_t1 ),
                        "kraken_EURUSD_depth_ASK_5_t1": float (kraken_EURUSD_ASK_5_t1 ),
                        "SIDE_T1": "BUY",
                        "instrument_t1": instrument_t1,
                        "bid_t1": float(bid_t1),
                        "bid_volume_t1": float(bid_volume_t1),
                        "ask_t1": float(ask_t1),
                        "ask_volume_t1": float(ask_volume_t1),
                        "SIDE_CROSS_T1":"SELL",
                        "instrument_t1_cross": instrument_t1_cross,
                        "bid_t1_cross" : float(instrument_t1_cross_bid),
                        "ask_t1_cross" : float(instrument_t1_cross_ask),
                        "spread_depth_t_bid": float(spread_t_bid),
                        "spread_depth_t_ask": float(spread_t_ask),
                        "spread_depth": float(spread)
                    }
                }
            ]
            myclient_tcp.write_points(basket_json, time_precision='ms')
            if instrument_t1[-3:] == "USD":
                print("BASKET","EURUSD ASK:", kraken_EURUSD_ASK_5_t0, "BUY",instrument_t0, ask_t0,"SELL", instrument_t0_cross, instrument_t0_cross_bid, "EURUSD BID:", kraken_EURUSD_BID_5_t1, "SELL",  instrument_t1, bid_t1,"BUY", instrument_t1_cross, instrument_t1_cross_ask)

            basket_json = [
                {
                    "measurement": 'MESSAGES',
                    "tags": {
                        "MSGTYPE": "BASKET",
                        "instrument": "KR_EURUSD_DEPTH",
                        "SIDE_T0": "BUY",
                        "instrument_t0": instrument_t0,
                        "SIDE_CROSS_T0": "SELL" ,
                        "instrument_t0_cross": instrument_t0_cross,
                        "SIDE_T1": "SELL",
                        "instrument_t1": instrument_t1,
                        "SIDE_CROSS_T1":"BUY",
                        "instrument_t1_cross": instrument_t1_cross,
                    },
                    "fields": {
                        "kraken_EURUSD_depth_BID_5_t0": float ( kraken_EURUSD_BID_5_t0 ),
                        "kraken_EURUSD_depth_ASK_5_t0": float ( kraken_EURUSD_ASK_5_t0 ),
                        "SIDE_T0": "BUY",
                        "instrument_t0": instrument_t0,
                        "bid_t0": float(bid_t0),
                        "bid_volume_t0": float(bid_volume_t0),
                        "ask_t0": float(ask_t0),
                        "ask_volume_t0": float(ask_volume_t0),
                        "SIDE_CROSS_T0": "SELL" ,
                        "instrument_t0_cross": instrument_t0_cross,
                        "bid_t0_cross" : float(instrument_t0_cross_bid),
                        "ask_t0_cross" : float(instrument_t0_cross_ask),
                        "kraken_EURUSD_depth_BID_5_t1": float ( kraken_EURUSD_BID_5_t1 ),
                        "kraken_EURUSD_depth_ASK_5_t1": float (kraken_EURUSD_ASK_5_t1 ),
                        "SIDE_T1": "SELL",
                        "instrument_t1": instrument_t1,
                        "bid_t1": float(bid_t1),
                        "bid_volume_t1": float(bid_volume_t1),
                        "ask_t1": float(ask_t1),
                        "ask_volume_t1": float(ask_volume_t1),
                        "SIDE_CROSS_T1":"BUY",
                        "instrument_t1_cross": instrument_t1_cross,
                        "bid_t1_cross" : float(instrument_t1_cross_bid),
                        "ask_t1_cross" : float(instrument_t1_cross_ask),
                        "spread_depth_t_bid": float(spread_t_bid),
                        "spread_depth_t_ask": float(spread_t_ask),
                        "spread_depth": float(spread)
                    }
                }
            ]
            myclient_tcp.write_points(basket_json, time_precision='ms')
# line = 'synthetic,instrument=KR_EURUSD,instrument_t0=' + instrument_t0 + ',instrument_t1=' + instrument + ' kraken_EURUSD_BID_5_t0=' + kraken_EURUSD_BID_5_t0 + ',kraken_EURUSD_ASK_5_t0=' + kraken_EURUSD_ASK_5_t0 + ',kraken_EURUSD_BID_5_t1=' + kraken_EURUSD_BID_5_t1 + ',kraken_EURUSD_ASK_5_t1=' + kraken_EURUSD_ASK_5_t1 + ',spread_t_bid=' + spread_t_bid + ',spread_t_ask=' + spread_t_ask + ',spread=' + spread
    # print(tick_json)
    # myclient_udp.send_packet ( line , protocol='line')
    # myclient_tcp.write_points( line , protocol='line')
    # myclient_udp._write_points ( line , protocol='line')
    # print ( instrument_t0 , kraken_EURUSD_BID_5_t0 , kraken_EURUSD_ASK_5_t0 , instrument , kraken_EURUSD_BID_5_t1 ,
    # kraken_EURUSD_ASK_5_t1 , spread , spread_t_bid , spread_t_ask)