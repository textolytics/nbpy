import ccs
import simplejson as json
import zmq
import sys
import datetime
port = "5558"

context = zmq.Context()
socket = context.socket(zmq.PUB)
topic = 'kraken_tick'
topic_json = 'kraken_tick_json'

# Update
# socket.setsockopt(zmq.ZMQ_IMMEDIATE, 1)
socket.setsockopt(zmq.SNDBUF, 10240)
socket.setsockopt(zmq.SNDHWM, 10000)
# socket.setsockopt(zmq.SWAP, 25000000)
socket.bind("tcp://*:%s" % port)

# get Asset Pairs
response = ccs.kraken.public.getTradableAssetPairs()
instruments_msg = json.loads(response)
print (response)
instruments = instruments_msg['result']
instrument_list = ','.join ( [str(instrument ) for instrument in instruments] )



while True:
    response = ccs.kraken.public.getTickerInformation(pair=instrument_list)
    ticks_msg = json.loads(response)

    # print (ticks_msg)
    # try:
    #     socket.send_json( "%s %s" % (topic_json, ticks_msg))
    #     socket.send_string( "%s %s" % (topic, response))
    #
    # except Exception as E:
    #         print (E)

    ticks = ticks_msg['result']
    for tick in ticks:
        instrument = str(tick)
        tick = ticks[instrument]
        ask_price, ask_whole_lot_volume, ask_lot_volume = tick['a']
        bid_price, bid_whole_lot_volume, bid_lot_volume = tick['b']
        last_trade_price, last_trade_lot_volume = tick['c']
        volume_today, volume_last_24_hours = tick['v']
        vwap_today, vwap_last_24_hours = tick['p']
        number_of_trades_today,number_of_trades_last_24_hours = tick['t']
        low_today, low_last_24_hours = tick['l']
        high_today, high_last_24_hours = tick['h']
        opening_price = tick['o']
        messagedata = str(instrument) +"\x01" + str(ask_price ) + "\x01" + str(ask_whole_lot_volume ) + "\x01" + str(ask_lot_volume ) + "\x01" + str (bid_price ) + "\x01" + str(bid_whole_lot_volume ) + "\x01" + str(bid_lot_volume ) + "\x01" + str (
            last_trade_price ) + "\x01" + str(last_trade_lot_volume )+ "\x01" + str(volume_today ) + "\x01" + str(volume_last_24_hours) + "\x01" + str(vwap_today ) + "\x01" + str(vwap_last_24_hours) + "\x01" + str(number_of_trades_today ) + "\x01" + str(number_of_trades_last_24_hours) + "\x01" + str(low_today ) + "\x01" + str(low_last_24_hours) + "\x01" + str(high_today ) + "\x01" + str(high_last_24_hours) + "\x01" + str(opening_price)
        topic = 'kraken_tick'
        # messagedata_encoded = messagedata.encode('utf-8', 'strict')
        # topic_encoded = topic.encode('utf-8', 'strict')
        socket.send_string( "%s %s" % (topic , messagedata) )
        # socket.send_json("%s" "%s" % (topic_encoded , messagedata_encoded))


        # try:
        #     # socket.send_json( "%s %s" % (topic_json , tick) )
        # except Exception as e:
        #     print (e)
        print (topic, instrument,ask_price , ask_whole_lot_volume , ask_lot_volume, bid_price , bid_whole_lot_volume , bid_lot_volume,    last_trade_price , last_trade_lot_volume, volume_today, volume_last_24_hours ,vwap_today, vwap_last_24_hours ,number_of_trades_today,number_of_trades_last_24_hours ,low_today, low_last_24_hours ,high_today, high_last_24_hours ,opening_price)
    # # print(instrument,volume_today, volume_last_24_hours ,vwap_today, vwap_last_24_hours ,number_of_trades_today,number_of_trades_last_24_hours ,low_today, low_last_24_hours ,high_today, high_last_24_hours ,opening_price)
    #
