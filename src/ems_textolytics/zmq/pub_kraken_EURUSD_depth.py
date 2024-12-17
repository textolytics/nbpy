import sys
import zmq
import simplejson as json

# sub-socket client
sub_port = "5560"
sub_context = zmq.Context()
sub_socket = sub_context.socket(zmq.SUB)
sub_topicfilter = "kr_depth"
sub_socket.setsockopt_string(zmq.SUBSCRIBE, sub_topicfilter)
sub_socket.setsockopt_string(zmq.SUBSCRIBE, "1")
print ("PORT: " +sub_port+ ". SUB TOPIC: " + sub_topicfilter)
sub_socket.connect("tcp://localhost:%s" % sub_port)

# pub-socket server
pub_port = "5561"
pub_context = zmq.Context()
pub_socket = pub_context.socket(zmq.PUB)
pub_topic = "kr_eurusd_depth"

# Update
pub_socket.setsockopt(zmq.SNDBUF, 10240)
pub_socket.setsockopt(zmq.SNDHWM, 10000)
print ("PORT: " +pub_port+ ". PUB TOPIC: "+pub_topic)
pub_socket.bind("tcp://*:%s" % pub_port)
kraken_EURUSD_BID = 0.11111
kraken_EURUSD_ASK = 100000.11111
BCHUSD_bid_price= 0.0000001
DASHUSD_bid_price= 0.0000001
USDTZUSD_bid_price= 0.0000001
XETCZUSD_bid_price= 0.0000001
XETHZUSD_bid_price= 0.0000001
XETHZUSD_d_bid_price= 0.0000001
XLTCZUSD_bid_price= 0.0000001
XXBTZUSD_bid_price= 0.0000001
XXBTZUSD_d_bid_price= 0.0000001
XXMRZUSD_bid_price= 0.0000001
XXRPZUSD_bid_price= 0.0000001
XZECZUSD_bid_price= 0.0000001
BCHEUR_bid_price= 0.0000001
DASHEUR_bid_price= 0.0000001
XETCZEUR_bid_price= 0.0000001
XETHZEUR_bid_price= 0.0000001
XETHZEUR_d_bid_price= 0.0000001
XLTCZEUR_bid_price= 0.0000001
XREPZEUR_bid_price= 0.0000001
XXBTZEUR_bid_price= 0.0000001
XXBTZEUR_d_bid_price= 0.0000001
XXMRZEUR_bid_price= 0.0000001
XXRPZEUR_bid_price= 0.0000001
XZECZEUR_bid_price= 0.0000001
BCHUSD_ask_price= 1000000
DASHUSD_ask_price= 1000000
USDTZUSD_ask_price= 1000000
XETCZUSD_ask_price= 1000000
XETHZUSD_ask_price= 1000000
XETHZUSD_d_ask_price= 1000000
XLTCZUSD_ask_price= 1000000
XXBTZUSD_ask_price= 1000000
XXBTZUSD_d_ask_price= 1000000
XXMRZUSD_ask_price= 1000000
XXRPZUSD_ask_price= 1000000
XZECZUSD_ask_price= 1000000
BCHEUR_ask_price= 1000000
DASHEUR_ask_price= 1000000
XETCZEUR_ask_price= 1000000
XETHZEUR_ask_price= 1000000
XETHZEUR_d_ask_price= 1000000
XLTCZEUR_ask_price= 1000000
XREPZEUR_ask_price= 1000000
XXBTZEUR_ask_price= 1000000
XXBTZEUR_d_ask_price= 1000000
XXMRZEUR_ask_price= 1000000
XXRPZEUR_ask_price= 1000000
XZECZEUR_ask_price= 1000000

kraken_EURUSD_ASK = 1.2
kraken_EURUSD_BID = 1.1
kraken_EURUSD_ASK_5_t1 = 1.2
kraken_EURUSD_BID_5_t1 = 1.1

bid_hedge = ""
ask_hedge = ""
instrument_t0=""

bid_t1 = 0.0001
bid_volume_t1 = 0.0001
ask_t1 = 0.0001
ask_volume_t1 = 0.0001



while True:
    topic, response = sub_socket.recv_string().split()
    msg = json.loads(response)
    ticks = msg['result']
    # print (response)
    for tick in ticks:
        instrument = str(tick)
        tick = ticks[instrument]
        for index, item in enumerate(tick['bids']):
            tier_id = str(index)
            top_bid = str(item[0])
            top_bid_volume = str(item[1])
            timestamp = str(item[2])
            # ms_timestamp = datetime.fromtimestamp ( timestamp ).strftime ( '%Y-%m-%dT%H:%M:%S.%f' )
#            line = 'depth,instrument=' + instrument + ' tier_id=' + tier_id + ',top_bid=' + top_bid + ',top_bid_volume=' + top_bid_volume
#            myclient.write_points(line, protocol='line',time_precision='ms')
#            print(line)
        for index, item in enumerate(tick['asks']):
            tier_id = str(index)
            top_ask = str(item[0])
            top_ask_volume = str(item[1])
            timestamp = str(item[2])
    str(instrument)
    bid_price=top_bid
    ask_price=top_ask
    if ('EUR' in instrument or 'USD' in instrument) and (instrument != 'USDTZUSD'):
        if instrument == 'BCHUSD':
            BCHUSD_ask_price = float ( ask_price )
            BCHUSD_bid_price = float ( bid_price )
            kraken_BCH_EURUSD_ASK = BCHUSD_ask_price / BCHEUR_bid_price
            kraken_BCH_EURUSD_BID = BCHUSD_bid_price / BCHEUR_ask_price
    #        if kraken_BCH_EURUSD_ASK <= kraken_EURUSD_ASK:
            ask_hedge = instrument
            kraken_EURUSD_ASK = kraken_BCH_EURUSD_ASK
    #        if kraken_BCH_EURUSD_BID >= kraken_EURUSD_BID:
            bid_hedge = instrument
            kraken_EURUSD_BID = kraken_BCH_EURUSD_BID
        if instrument == 'DASHUSD':
            DASHUSD_ask_price = float ( ask_price )
            DASHUSD_bid_price = float ( bid_price )
            kraken_DASH_EURUSD_ASK = DASHUSD_ask_price / DASHEUR_bid_price
            kraken_DASH_EURUSD_BID = DASHUSD_bid_price / DASHEUR_ask_price
    #        if kraken_DASH_EURUSD_ASK <= kraken_EURUSD_ASK:
            ask_hedge = instrument
            kraken_EURUSD_ASK = kraken_DASH_EURUSD_ASK
    #        if kraken_DASH_EURUSD_BID >= kraken_EURUSD_BID:
            bid_hedge = instrument
            kraken_EURUSD_BID = kraken_DASH_EURUSD_BID
        # if instrument == 'USDTZUSD':
        #     USDTZUSD_ask_price = float ( ask_price )
        #     USDTZUSD_bid_price = float ( bid_price )
        #     kraken_TZ_EURUSD_ASK = USDTZUSD_ask_price / XETCZEUR_bid_price
        #     kraken_TZ_EURUSD_BID = USDTZUSD_bid_price / XETCZEUR_ask_price
        #     if kraken_TZ_EURUSD_ASK <= kraken_EURUSD_ASK:
        #         ask_hedge = instrument
        #         kraken_EURUSD_ASK = kraken_TZ_EURUSD_ASK
        #     if kraken_TZ_EURUSD_BID >= kraken_EURUSD_BID:
        #         bid_hedge = instrument
        #         kraken_EURUSD_BID = kraken_TZ_EURUSD_BID
        if instrument == 'XETCZUSD':
            XETCZUSD_ask_price = float ( ask_price )
            XETCZUSD_bid_price = float ( bid_price )
            kraken_XETCZ_EURUSD_ASK = XETCZUSD_ask_price / XETHZEUR_bid_price
            kraken_XETCZ_EURUSD_BID = XETCZUSD_bid_price / XETHZEUR_ask_price
    #        if kraken_XETCZ_EURUSD_ASK <= kraken_EURUSD_ASK:
            ask_hedge = instrument
            kraken_EURUSD_ASK = kraken_XETCZ_EURUSD_ASK
    #        if kraken_XETCZ_EURUSD_BID >= kraken_EURUSD_BID:
            bid_hedge = instrument
            kraken_EURUSD_BID = kraken_XETCZ_EURUSD_BID
        if instrument == 'XETHZUSD':
            XETHZUSD_ask_price = float ( ask_price )
            XETHZUSD_bid_price = float ( bid_price )
            kraken_XETHZ_EURUSD_ASK = XETHZUSD_ask_price / XETHZEUR_d_bid_price
            kraken_XETHZ_EURUSD_BID = XETHZUSD_bid_price / XETHZEUR_d_ask_price
    #        if kraken_XETHZ_EURUSD_ASK <= kraken_EURUSD_ASK:
            ask_hedge = instrument
            kraken_EURUSD_ASK = kraken_XETHZ_EURUSD_ASK
    #        if kraken_XETHZ_EURUSD_BID >= kraken_EURUSD_BID:
            bid_hedge = instrument
            kraken_EURUSD_BID = kraken_XETHZ_EURUSD_BID
        if instrument == 'XETHZUSD.d':
            XETHZUSD_d_ask_price = float ( ask_price )
            XETHZUSD_d_bid_price = float ( bid_price )
            kraken_XETHZ_d_EURUSD_ASK = XETHZUSD_d_ask_price / XLTCZEUR_bid_price
            kraken_XETHZ_d_EURUSD_BID = XETHZUSD_d_bid_price / XLTCZEUR_ask_price
    #        if kraken_XETHZ_d_EURUSD_ASK <= kraken_EURUSD_ASK:
            ask_hedge = instrument
            kraken_EURUSD_ASK = kraken_XETHZ_d_EURUSD_ASK
    #        if kraken_XETHZ_d_EURUSD_BID >= kraken_EURUSD_BID:
            bid_hedge = instrument
            kraken_EURUSD_BID = kraken_XETHZ_d_EURUSD_BID
        if instrument == 'XLTCZUSD':
            XLTCZUSD_ask_price = float ( ask_price )
            XLTCZUSD_bid_price = float ( bid_price )
            kraken_XLTCZ_EURUSD_ASK = XLTCZUSD_ask_price / XREPZEUR_bid_price
            kraken_XLTCZ_EURUSD_BID = XLTCZUSD_bid_price / XREPZEUR_ask_price
    #        if kraken_XLTCZ_EURUSD_ASK <= kraken_EURUSD_ASK:
            ask_hedge = instrument
            kraken_EURUSD_ASK = kraken_XLTCZ_EURUSD_ASK
    #        if kraken_XLTCZ_EURUSD_BID >= kraken_EURUSD_BID:
            bid_hedge = instrument
            kraken_EURUSD_BID = kraken_XLTCZ_EURUSD_BID
        if instrument == 'XXBTZUSD':
            XXBTZUSD_ask_price = float ( ask_price )
            XXBTZUSD_bid_price = float ( bid_price )
            kraken_XXBTZ_EURUSD_ASK = XXBTZUSD_ask_price / XXBTZEUR_bid_price
            kraken_XXBTZ_EURUSD_BID = XXBTZUSD_bid_price / XXBTZEUR_ask_price
    #        if kraken_XXBTZ_EURUSD_ASK <= kraken_EURUSD_ASK:
            ask_hedge = instrument
            kraken_EURUSD_ASK = kraken_XXBTZ_EURUSD_ASK
    #        if kraken_XXBTZ_EURUSD_BID >= kraken_EURUSD_BID:
            bid_hedge = instrument
            kraken_EURUSD_BID = kraken_XXBTZ_EURUSD_BID
        if instrument == 'XXBTZUSD.d':
            XXBTZUSD_d_ask_price = float ( ask_price )
            XXBTZUSD_d_bid_price = float ( bid_price )
            kraken_XXBTZ_d_EURUSD_ASK = XXBTZUSD_d_ask_price / XXBTZEUR_d_bid_price
            kraken_XXBTZ_d_EURUSD_BID = XXBTZUSD_d_bid_price / XXBTZEUR_d_ask_price
    #        if kraken_XXBTZ_d_EURUSD_ASK <= kraken_EURUSD_ASK:
            ask_hedge = instrument
            kraken_EURUSD_ASK = kraken_XXBTZ_d_EURUSD_ASK
    #        if kraken_XXBTZ_d_EURUSD_BID >= kraken_EURUSD_BID:
            bid_hedge = instrument
            kraken_EURUSD_BID = kraken_XXBTZ_d_EURUSD_BID
        if instrument == 'XXMRZUSD':
            XXMRZUSD_ask_price = float ( ask_price )
            XXMRZUSD_bid_price = float ( bid_price )
            kraken_XXMRZ_EURUSD_ASK = XXMRZUSD_ask_price / XXMRZEUR_bid_price
            kraken_XXMRZ_EURUSD_BID = XXMRZUSD_bid_price / XXMRZEUR_ask_price
    #        if kraken_XXMRZ_EURUSD_ASK <= kraken_EURUSD_ASK:
            ask_hedge = instrument
            kraken_EURUSD_ASK = kraken_XXMRZ_EURUSD_ASK
    #        if kraken_XXMRZ_EURUSD_BID >= kraken_EURUSD_BID:
            bid_hedge = instrument
            kraken_EURUSD_BID = kraken_XXMRZ_EURUSD_BID
        if instrument == 'XXRPZUSD':
            XXRPZUSD_ask_price = float ( ask_price )
            XXRPZUSD_bid_price = float ( bid_price )
            kraken_XXRPZ_EURUSD_ASK = XXRPZUSD_ask_price / XXRPZEUR_bid_price
            kraken_XXRPZ_EURUSD_BID = XXRPZUSD_bid_price / XXRPZEUR_ask_price
    #        if kraken_XXRPZ_EURUSD_ASK <= kraken_EURUSD_ASK:
            ask_hedge = instrument
            kraken_EURUSD_ASK = kraken_XXRPZ_EURUSD_ASK
    #        if kraken_XXRPZ_EURUSD_BID >= kraken_EURUSD_BID:
            bid_hedge = instrument
            kraken_EURUSD_BID = kraken_XXRPZ_EURUSD_BID
        if instrument == 'XZECZUSD':
            XZECZUSD_ask_price = float ( ask_price )
            XZECZUSD_bid_price = float ( bid_price )
            kraken_XZECZ_EURUSD_ASK = XZECZUSD_ask_price / XZECZEUR_bid_price
            kraken_XZECZ_EURUSD_BID = XZECZUSD_bid_price / XZECZEUR_ask_price
    #        if kraken_XZECZ_EURUSD_ASK <= kraken_EURUSD_ASK:
            ask_hedge = instrument
            kraken_EURUSD_ASK = kraken_XZECZ_EURUSD_ASK
    #        if kraken_XZECZ_EURUSD_BID >= kraken_EURUSD_BID:
            bid_hedge = instrument
            kraken_EURUSD_BID = kraken_XZECZ_EURUSD_BID
        if instrument == 'BCHEUR':
            BCHEUR_ask_price = float ( ask_price )
            BCHEUR_bid_price = float ( bid_price )
            kraken_BCH_EURUSD_BID = BCHUSD_bid_price / BCHEUR_ask_price
            kraken_BCH_EURUSD_ASK = BCHUSD_ask_price / BCHEUR_bid_price
    #        if kraken_BCH_EURUSD_BID >= kraken_EURUSD_BID:
            bid_hedge = instrument
            kraken_EURUSD_BID = kraken_BCH_EURUSD_BID
    #        if kraken_BCH_EURUSD_ASK <= kraken_EURUSD_ASK:
            ask_hedge = instrument
            kraken_EURUSD_ASK = kraken_BCH_EURUSD_ASK
        if instrument == 'DASHEUR':
            DASHEUR_ask_price = float ( ask_price )
            DASHEUR_bid_price = float ( bid_price )
            kraken_DASH_EURUSD_BID = DASHUSD_bid_price / DASHEUR_ask_price
            kraken_DASH_EURUSD_ASK = DASHUSD_ask_price / DASHEUR_bid_price
    #        if kraken_DASH_EURUSD_BID >= kraken_EURUSD_BID:
            bid_hedge = instrument
            kraken_EURUSD_BID = kraken_DASH_EURUSD_BID
    #        if kraken_DASH_EURUSD_ASK <= kraken_EURUSD_ASK:
            ask_hedge = instrument
            kraken_EURUSD_ASK = kraken_DASH_EURUSD_ASK
        # if instrument == 'XETCZEUR':
        #     XETCZEUR_ask_price = float ( ask_price )
        #     XETCZEUR_bid_price = float ( bid_price )
        #     kraken_TZ_EURUSD_BID = XETCZUSD_bid_price / XETCZEUR_ask_price
        #     kraken_TZ_EURUSD_ASK = XETCZUSD_ask_price / XETCZEUR_bid_price
        #     if kraken_TZ_EURUSD_BID >= kraken_EURUSD_BID:
        #         bid_hedge = instrument
        #         kraken_EURUSD_BID = kraken_TZ_EURUSD_BID
        #     if kraken_TZ_EURUSD_ASK <= kraken_EURUSD_ASK:
        #         ask_hedge = instrument
        #         kraken_EURUSD_ASK = kraken_TZ_EURUSD_ASK
        if instrument == 'XETHZEUR':
            XETHZEUR_ask_price = float ( ask_price )
            XETHZEUR_bid_price = float ( bid_price )
            kraken_XETCZ_EURUSD_BID = XETHZUSD_bid_price / XETHZEUR_ask_price
            kraken_XETCZ_EURUSD_ASK = XETHZUSD_ask_price / XETHZEUR_bid_price
    #        if kraken_XETCZ_EURUSD_BID >= kraken_EURUSD_BID:
            bid_hedge = instrument
            kraken_EURUSD_BID = kraken_XETCZ_EURUSD_BID
    #        if kraken_XETCZ_EURUSD_ASK <= kraken_EURUSD_ASK:
            ask_hedge = instrument
            kraken_EURUSD_ASK = kraken_XETCZ_EURUSD_ASK
        if instrument == 'XETHZEUR.d':
            XETHZEUR_d_ask_price = float ( ask_price )
            XETHZEUR_d_bid_price = float ( bid_price )
            kraken_XETHZ_EURUSD_BID = XETHZUSD_bid_price / XETHZEUR_d_ask_price
            kraken_XETHZ_EURUSD_ASK = XETHZUSD_ask_price / XETHZEUR_d_bid_price
    #        if kraken_XETHZ_EURUSD_BID >= kraken_EURUSD_BID:
            bid_hedge = instrument
            kraken_EURUSD_BID = kraken_XETHZ_EURUSD_BID
    #        if kraken_XETHZ_EURUSD_ASK <= kraken_EURUSD_ASK:
            ask_hedge = instrument
            kraken_EURUSD_ASK = kraken_XETHZ_EURUSD_ASK
        if instrument == 'XLTCZEUR':
            XLTCZEUR_ask_price = float ( ask_price )
            XLTCZEUR_bid_price = float ( bid_price )
            kraken_XETHZ_d_EURUSD_BID = XETHZUSD_d_bid_price / XLTCZEUR_ask_price
            kraken_XETHZ_d_EURUSD_ASK = XETHZUSD_d_ask_price / XLTCZEUR_bid_price
    #        if kraken_XETHZ_d_EURUSD_BID >= kraken_EURUSD_BID:
            bid_hedge = instrument
            kraken_EURUSD_BID = kraken_XETHZ_d_EURUSD_BID
    #        if kraken_XETHZ_d_EURUSD_ASK <= kraken_EURUSD_ASK:
            ask_hedge = instrument
            kraken_EURUSD_ASK = kraken_XETHZ_d_EURUSD_ASK
        if instrument == 'XREPZEUR':
            XREPZEUR_ask_price = float ( ask_price )
            XREPZEUR_bid_price = float ( bid_price )
            kraken_XLTCZ_EURUSD_BID = XLTCZUSD_bid_price / XREPZEUR_ask_price
            kraken_XLTCZ_EURUSD_ASK = XLTCZUSD_ask_price / XREPZEUR_bid_price
    #        if kraken_XLTCZ_EURUSD_BID >= kraken_EURUSD_BID:
            bid_hedge = instrument
            kraken_EURUSD_BID = kraken_XLTCZ_EURUSD_BID
    #        if kraken_XLTCZ_EURUSD_ASK <= kraken_EURUSD_ASK:
            ask_hedge = instrument
            kraken_EURUSD_ASK = kraken_XLTCZ_EURUSD_ASK
        if instrument == 'XXBTZEUR':
            XXBTZEUR_ask_price = float ( ask_price )
            XXBTZEUR_bid_price = float ( bid_price )
            kraken_XXBTZ_EURUSD_BID = XXBTZUSD_bid_price / XXBTZEUR_ask_price
            kraken_XXBTZ_EURUSD_ASK = XXBTZUSD_ask_price / XXBTZEUR_bid_price
    #        if kraken_XXBTZ_EURUSD_BID >= kraken_EURUSD_BID:
            bid_hedge = instrument
            kraken_EURUSD_BID = kraken_XXBTZ_EURUSD_BID
    #        if kraken_XXBTZ_EURUSD_ASK <= kraken_EURUSD_ASK:
            ask_hedge = instrument
            kraken_EURUSD_ASK = kraken_XXBTZ_EURUSD_ASK
        if instrument == 'XXBTZEUR.d':
            XXBTZEUR_d_ask_price = float ( ask_price )
            XXBTZEUR_d_bid_price = float ( bid_price )
            kraken_XXBTZ_d_EURUSD_BID = XXBTZUSD_d_bid_price / XXBTZEUR_d_ask_price
            kraken_XXBTZ_d_EURUSD_ASK = XXBTZUSD_d_ask_price / XXBTZEUR_d_bid_price
    #        if kraken_XXBTZ_d_EURUSD_BID >= kraken_EURUSD_BID:
            bid_hedge = instrument
            kraken_EURUSD_BID = kraken_XXBTZ_d_EURUSD_BID
    #        if kraken_XXBTZ_d_EURUSD_ASK <= kraken_EURUSD_ASK:
            ask_hedge = instrument
            kraken_EURUSD_ASK = kraken_XXBTZ_d_EURUSD_ASK
        if instrument == 'XXMRZEUR':
            XXMRZEUR_ask_price = float ( ask_price )
            XXMRZEUR_bid_price = float ( bid_price )
            kraken_XXMRZ_EURUSD_BID = XXMRZUSD_bid_price / XXMRZEUR_ask_price
            kraken_XXMRZ_EURUSD_ASK = XXMRZUSD_ask_price / XXMRZEUR_bid_price
    #        if kraken_XXMRZ_EURUSD_BID >= kraken_EURUSD_BID:
            bid_hedge = instrument
            kraken_EURUSD_BID = kraken_XXMRZ_EURUSD_BID
    #        if kraken_XXMRZ_EURUSD_ASK <= kraken_EURUSD_ASK:
            ask_hedge = instrument
            kraken_EURUSD_ASK = kraken_XXMRZ_EURUSD_ASK
        if instrument == 'XXRPZEUR':
            XXRPZEUR_ask_price = float ( ask_price )
            XXRPZEUR_bid_price = float ( bid_price )
            kraken_XXRPZ_EURUSD_BID = XXRPZUSD_bid_price / XXRPZEUR_ask_price
            kraken_XXRPZ_EURUSD_ASK = XXRPZUSD_ask_price / XXRPZEUR_bid_price
    #        if kraken_XXRPZ_EURUSD_BID >= kraken_EURUSD_BID:
            bid_hedge = instrument
            kraken_EURUSD_BID = kraken_XXRPZ_EURUSD_BID
    #        if kraken_XXRPZ_EURUSD_ASK <= kraken_EURUSD_ASK:
            ask_hedge = instrument
            kraken_EURUSD_ASK = kraken_XXRPZ_EURUSD_ASK
        if instrument == 'XZECZEUR':
            XZECZEUR_ask_price = float ( ask_price )
            XZECZEUR_bid_price = float ( bid_price )
            kraken_XZECZ_EURUSD_BID = XZECZUSD_bid_price / XZECZEUR_ask_price
            kraken_XZECZ_EURUSD_ASK = XZECZUSD_ask_price / XZECZEUR_bid_price
    #        if kraken_XZECZ_EURUSD_BID >= kraken_EURUSD_BID:
            bid_hedge = instrument
            kraken_EURUSD_BID = kraken_XZECZ_EURUSD_BID
    #        if kraken_XZECZ_EURUSD_ASK <= kraken_EURUSD_ASK:
            ask_hedge = instrument
            kraken_EURUSD_ASK = kraken_XZECZ_EURUSD_ASK

        if 1 <= float(kraken_EURUSD_BID) <= 3:
            if 1 <= float(kraken_EURUSD_ASK)<=3:
                bid_t0 = float(bid_t1)
                bid_volume_t0 = float(bid_volume_t1)
                ask_t0 = float(ask_t1)
                ask_volume_t0 = float(ask_volume_t1)

                bid_t1 = float(top_bid)
                bid_volume_t1 = float(top_bid_volume)
                ask_t1 = float(top_ask)
                ask_volume_t1 = float(top_ask_volume)

                kraken_EURUSD_BID_5_t0 = kraken_EURUSD_BID_5_t1
                kraken_EURUSD_ASK_5_t0 = kraken_EURUSD_ASK_5_t1
                kraken_EURUSD_BID_5_t1 = round(kraken_EURUSD_BID,5)
                kraken_EURUSD_ASK_5_t1 = round (kraken_EURUSD_ASK, 5)
                spread = (float(kraken_EURUSD_ASK_5_t1 ) - float ( kraken_EURUSD_BID_5_t1 ))
                spread_t_ask = kraken_EURUSD_ASK_5_t1 - kraken_EURUSD_BID_5_t0
                spread_t_bid = kraken_EURUSD_ASK_5_t0 - kraken_EURUSD_BID_5_t1
                messagedata = str (instrument_t0 ) + "\x01" + str (kraken_EURUSD_BID_5_t0) + "\x01" + str (kraken_EURUSD_ASK_5_t0) +"\x01" + str(round(bid_t0,5)) + "\x01" + str(round(bid_volume_t0,5)) + "\x01"  + str(round(ask_t0,5)) +"\x01" +  str(round(ask_volume_t0,5)) + "\x01" + str (instrument) + "\x01" + str ( float(kraken_EURUSD_BID_5_t1) ) + "\x01" + str ( float(kraken_EURUSD_ASK_5_t1) ) +  "\x01" +  str(round(bid_t1,5)) + "\x01" + str(round(bid_volume_t1,5)) + "\x01" + str(round(ask_t1,5)) +  "\x01" + str(round(ask_volume_t1,5)) + "\x01" + str(round(spread, 5)) + "\x01" + str(round(spread_t_bid, 5)) + "\x01" + str(round(spread_t_ask,5))
                pub_socket.send_string("%s %s" % (pub_topic, messagedata))
                print(messagedata)
                instrument_t0 = instrument


