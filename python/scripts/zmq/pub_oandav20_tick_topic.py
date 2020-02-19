

#
# Last value cache
# Uses XPUB subscription messages to re-send data
#

import zmq

def main():
    ctx = zmq.Context.instance()
    frontend = ctx.socket(zmq.SUB)
    frontend.connect("tcp://192.168.0.13:5556")
    backend = ctx.socket(zmq.XPUB)
    backend.bind("tcp://*:5562")

    # Subscribe to every single topic from publisher
    frontend.setsockopt_string(zmq.SUBSCRIBE, 'oanda_tick')

    # Store last instance of each topic in a cache
    cache = {}

    # main poll loop
    # We route topic updates from frontend to backend, and
    # we handle subscriptions by sending whatever we cached,
    # if anything:
    poller = zmq.Poller()
    poller.register(frontend, zmq.POLLIN)
    poller.register(backend, zmq.POLLIN)
    while True:
        try:
            events = dict(poller.poll(1000))
        except KeyboardInterrupt:
            print("interrupted")
            break

        # Any new topic data we cache and then forward
        if frontend in events:
            # print (frontend.recv_multipart())
            # msg = frontend.recv_multipart()
            msg = frontend.recv_string().split()
            topic, current = msg
            instrument, timestamp, bid, ask = current.split('\x01')

            # print (instrument, timestamp, bid, ask)

            cache[instrument] = timestamp, bid, ask
            # print (cache)
            last_tick = timestamp + "\x01" + bid + "\x01" +  ask
            backend.send_string( "%s %s" % (instrument , last_tick) )
            # print (instrument, last_tick)
        # handle subscriptions
        # When we get a new subscription we pull data from the cache:
        if backend in events:
            event = backend.recv()
            print (event[0])
            # Event is one byte 0=unsub or 1=sub, followed by topic
            if event[0] == b'\x01':
                instrument = event[1:]
                if instrument in cache:
                    print ("Sending cached topic %s" % instrument)
                    backend.send_string(instrument, cache[instrument])

if __name__ == '__main__':
    main()
