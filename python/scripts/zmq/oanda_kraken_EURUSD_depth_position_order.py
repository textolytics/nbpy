

import simplejson as json
import zmq
from influxdb import InfluxDBClient

# InfluxDB connections settings
host = '192.168.0.33'
port = 8086
user = 'zmq'
password = 'zmq'
dbname = 'tick'
myclient = InfluxDBClient(host, port, user, password, dbname, use_udp=False)

# ZeroMQ connections settings
port = "5560"
context = zmq.Context()
socket = context.socket(zmq.SUB)
topicfilter = "kr_depth"
socket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)
socket.setsockopt_string(zmq.SUBSCRIBE, "1")
print("SUB :"+topicfilter+" >>> INFLUXDB." +dbname+" [ORDERS]...")
socket.connect("tcp://localhost:%s" % port)

while True:
    topic, response = socket.recv_string().split()
    msg = json.loads(response)
    ticks = msg['result']
    # print (ticks)
    for tick in ticks:
        instrument = str(tick)
        if instrument[0] == 'X' and instrument[-4] == 'Z':
            base_ccy = instrument[1:4]
            term_ccy = instrument[-3:]
            # print (base_ccy,term_ccy)
        elif len(instrument) == 6 and instrument[-4] != '_':
            base_ccy = instrument[0:3]
            term_ccy = instrument[3:6]
            # print (base_ccy,term_ccy)
        tick = ticks[instrument]
        for index, item in enumerate(tick['bids']):
            tier_id = str(index)
            top_bid = str(item[0])
            top_bid_volume = str(item[1])
            timestamp = str(item[2])
            # ms_timestamp = datetime.fromtimestamp ( timestamp ).strftime ( '%Y-%m-%dT%H:%M:%S.%f' )
            line = 'depth,instrument=' + instrument + ',base_ccy=' + base_ccy + ',term_ccy=' + term_ccy + ' tier_id=' + tier_id + ',top_bid=' + top_bid + ',top_bid_volume=' + top_bid_volume
            myclient.write_points(line, protocol='line',  time_precision='ms')
            # print(line)

        for index, item in enumerate(tick['asks']):
            tier_id = str(index)
            top_ask = str(item[0])
            top_ask_volume = str(item[1])
            timestamp = (item[2])
            # ms_timestamp = datetime.fromtimestamp ( timestamp ).strftime ( '%Y-%m-%dT%H:%M:%S.%f' )
            line = 'depth,instrument=' + instrument + ',base_ccy=' + base_ccy + ',term_ccy=' + term_ccy + ' tier_id=' + tier_id + ',top_ask=' + top_ask + ',top_ask_volume=' + top_ask_volume
            myclient.write_points(line, protocol='line',  time_precision='ms')
        # print (line)

        position_open(instrument, closeoutBid, closeoutAsk)

    response = socket.recv_string()
    topic, messagedata = response.split(' ')
    instrument_t0, kraken_EURUSD_BID_5_t0, kraken_EURUSD_ASK_5_t0, bid_t0, bid_volume_t0, ask_t0, ask_volume_t0, instrument_t1, kraken_EURUSD_BID_5_t1, kraken_EURUSD_ASK_5_t1, bid_t1, bid_volume_t1, ask_t1, ask_volume_t1, spread, spread_t_bid, spread_t_ask = messagedata.split('\x01')


def newOrder(instrument, p,bid,ask):
    units = 1000
    if instrument == 'XAG_USD':
        units = 1
    if instrument == 'XAU_USD':
        units = 1
    if instrument == 'BCO_USD':
        units = 1
    if p > ask:
        side = 'buy'
        if pip == 0.001:
            price = round(((ask - bid) / 2 + bid), 3)
            takeProfit = round((ask + 0.007*ask),3)
            stopLoss = round((bid - 0.002*ask),3)
            trailingStop = round((bid - 0.002*ask),3)
        if pip == 0.00001:
            # price = round(((ask - bid) / 2 + bid), 5)
            # takeProfit = round((ask + 0.0013*ask),5)
            # stopLoss = round((bid - 0.0007*ask),5)
            # trailingStop = round((bid - 0.0007*ask),5)

            price = round(((ask - bid) / 2 + bid), 5)
            takeProfit = round((ask + 0.00013*ask),5)
            stopLoss = round((bid - 0.00007*ask),5)
            trailingStop = round((bid - 0.00007*ask),5)

    if p < bid:
        side = 'sell'
        if pip == 0.001:

            price = round(((ask - bid) / 2 + bid), 3)
            takeProfit = round((bid - 0.0013*bid),3)
            stopLoss = round((ask + 0.0007*bid),3)
            trailingStop = round((ask + 0.0007*bid),3)

        if pip == 0.00001:
            # price = round(((ask - bid) / 2 + bid), 5)
            # takeProfit = round((bid - 0.007 * bid), 5)
            # stopLoss = round((ask + 0.001*bid), 5)
            # trailingStop = round((ask + 0.002*bid), 5)

            price = round(((ask - bid) / 2 + bid), 5)
            takeProfit = round((bid - 0.0013 * bid), 6)
            stopLoss = round((ask + 0.0007*bid), 6)
            trailingStop = round((ask + 0.0007*bid), 5)




    print (stopLoss,takeProfit)
    test_order = Order(
        instrument=instrument,
        units=units,
        side=side,
        type="market",
        stopLoss=stopLoss,
        trailingStop=5,
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
    print (instrument, takeProfit , stopLoss)
    return test_order

def position_open(instrument, bid, ask):
    try:
        # instrument, bid, ask = connect_v20(access_token, accountID, instruments)
        # print(instrument, bid, ask)
        # term1, term2, pip = search_terms(instrument)
        # print(term1, term2, pip)
        # print(pip)

        try:
            position = client.get_position(instrument)
            print(position)

        except Exception as e:
            if str(e) == "OCode-404: Position not found":
                # aggregate_quotes_ohlc_train, aggregate_quotes_ohlc_validate, aggregate_quotes, aggregate_ttrss, aggregate_quotes_last_hour, aggregate_ttrss_last_hour = select(
                #     instrument, term1, term2)
                # train(aggregate_quotes, aggregate_quotes,aggregate_ttrss)
                # p=float(predict(aggregate_quotes_last_hour,aggregate_ttrss))
                # if abs((p - float(bid))/float(bid)) > 0.01:
                prediction = round(p,5)

                print (instrument, prediction,  float(bid), float(ask))
                test_order = newOrder(instrument, float(prediction), float(bid), float(ask))
                print (str(newOrder(instrument, float(prediction), float(bid), float(ask))))
                order = client.create_order(order=test_order)

            print(str(e))
    except Exception as e:
        print(str(e))


while True:
    response = socket.recv_string()
    topic, messagedata = response.split(' ')
    instrument_t0, kraken_EURUSD_BID_5_t0, kraken_EURUSD_ASK_5_t0, bid_t0, bid_volume_t0, ask_t0, ask_volume_t0, instrument_t1, kraken_EURUSD_BID_5_t1, kraken_EURUSD_ASK_5_t1, bid_t1, bid_volume_t1, ask_t1, ask_volume_t1, spread, spread_t_bid, spread_t_ask = messagedata.split('\x01')
    print("KR_EURUSD DEPTH:", messagedata)
    spread_t_bid_f = float(spread_t_bid)
    if spread_t_bid_f < - 0.0005:
        instrument, closeoutBid, closeoutAsk = connect_v20(access_token, accountID, instruments)
        p = 1.21234
        position_open(instruments, p, closeoutBid, closeoutAsk)
    spread_t_ask_f = float(spread_t_ask)
    if spread_t_ask_f < - 0.0005:
        instrument, closeoutBid, closeoutAsk = connect_v20(access_token, accountID, instruments)
        p = 1.12123
        position_open(instruments, p, closeoutBid, closeoutAsk)
