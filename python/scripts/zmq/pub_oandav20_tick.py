#!/usr/bin/python3.5
import argparse
import common.config
import common.view

import requests
# import httplib as http_client
from optparse import OptionParser
import simplejson as json
from datetime import datetime
import zmq
import random
import sys
import time

port = "5556"
context = zmq.Context()
socket = context.socket(zmq.PUB)

# Update
# socket.setsockopt(zmq.ZMQ_IMMEDIATE, 1)
socket.setsockopt(zmq.SNDBUF, 10240)
socket.setsockopt(zmq.SNDHWM, 10000)
socket.bind("tcp://*:%s" % port)


def price_to_string(price):

    return "{} ({}) {}/{}".format(
        price.instrument,
        price.time,
        price.bids[0].price,
        price.asks[0].price
    )

def heartbeat_to_string(heartbeat):
    return "HEARTBEAT ({})".format(
        heartbeat.time
    )

def instruments_list():
    """
    Create an API context, and use it to fetch and display the tradeable
    instruments for and Account.

    The configuration for the context and Account to fetch is parsed from the
    config file provided as an argument.
    """

    parser = argparse.ArgumentParser()

    #
    # The config object is initialized by the argument parser, and contains
    # the REST APID host, port, accountID, etc.
    #
    common.config.add_argument(parser)

    args = parser.parse_args()

    account_id = args.config.active_account

    #
    # The v20 config object creates the v20.Context for us based on the
    # contents of the config file.
    #
    api = args.config.create_context()

    #
    # Fetch the tradeable instruments for the Account found in the config file
    #
    response = api.account.instruments(account_id)

    #
    # Extract the list of Instruments from the response.
    #
    instruments = response.get("instruments", "200")
    instruments.sort(key=lambda i: i.name)
    def marginFmt(instrument):
        return "{:.0f}:1 ({})".format(
            1.0 / float(instrument.marginRate),
            instrument.marginRate
        )

    def pipFmt(instrument):
        location = float(10 ** instrument.pipLocation)
        return "{:.4f}".format (location)

    #
    # Print the details of the Account's tradeable instruments
    #
    common.view.print_collection(
        "{} Instruments".format(len(instruments)),
        instruments,
        [
            ("Name", lambda i: i.name),
            ("Type", lambda i: i.type),
            ("Pip", pipFmt),
            ("Margin Rate", marginFmt),
        ]
    )
    instrument_list = ""
    # instrument_list +="\""
    for entity in instruments:
        instrument_list += entity.name + ","
    instrument_list= instrument_list[:-1]
    # instrument_list +="\""
    print (instrument_list)
    # [
    #     # ("Name", lambda i: i.name),
    #     # ("Type", lambda i: i.type),
    #     # ("Pip", pipFmt),
    #     # ("Margin Rate", marginFmt),
    # ]
    return instrument_list

def streaming_v20():
    """
    Stream the prices for a list of Instruments for the active Account.
    """

    parser = argparse.ArgumentParser()

    common.config.add_argument(parser)
    print (instruments_list())

    # parser.add_argument(
    #     '--instrument', "-i",
    #     type=common.args.instrument,
    #     required=True,
    #     action="append",
    #     help="Instrument to get prices for"
    # )

    parser.add_argument(
        '--snapshot',
        action="store_true",
        default=True,
        help="Request an initial snapshot"
    )

    parser.add_argument(
        '--no-snapshot',
        dest="snapshot",
        action="store_false",
        help="Do not request an initial snapshot"
    )

    parser.add_argument(
        '--show-heartbeats', "-s",
        action='store_true',
        default=False,
        help="display heartbeats"
    )

    args = parser.parse_args()
    account_id = args.config.active_account

    api = args.config.create_streaming_context()

    # api.set_convert_decimal_number_to_native(False)

    # api.set_stream_timeout(3)

    #
    # Subscribe to the pricing stream
    #
    response = api.pricing.stream(
        account_id,
        snapshot=args.snapshot,
        instruments=instruments_list(),
    )

    #
    # Print out each price as it is received to topc             topic = 'oanda_tick'
    #
    topic_oanda_tick = 'oanda_tick'
    topic_oanda_heartbeat = 'oanda_heartbeat'

    for msg_type, msg in response.parts():
        if msg_type == "pricing.Heartbeat" and args.show_heartbeats:
            heartbeat = msg
            heartbit_ts = str(heartbeat.time)
            now_ts = datetime.strptime(datetime.utcnow().isoformat(sep='T'), '%Y-%m-%dT%H:%M:%S.%f')
            lag = now_ts - heartbit_ts
            messagedata = heartbit_ts + "\x01" + now_ts+ "\x01" + lag
            socket.send_string("%s %s" % (topic_oanda_heartbeat, messagedata))
            # print(messagedata)
        elif msg_type == "pricing.Price":
            price = msg
            messagedata = str(price.instrument) + "\x01" + str(price.time) + "\x01" + str(price.bids[0].price) + "\x01" + str(price.asks[0].price)
            # print(messagedata)
            socket.send_string("%s %s" % (topic_oanda_tick, messagedata))
            topic_instrument = str(price.instrument)
            messagedata = str(price.time) + "\x01" + str(price.bids[0].price) + "\x01" + str(price.asks[0].price)
            socket.send_string("%s %s" % (topic_instrument, messagedata))
            # print(topic_instrument,messagedata)
            # print(price.instrument, price.time, price.bids[0].price, price.asks[0].price)
            # print(price_to_string(msg))
            # print (price.instrument,
            # price.time,
            # price.bids[0].price,
            # price.asks[0].price)

if __name__ == "__main__":
    streaming_v20()