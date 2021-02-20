# from __future__ import print_function
"""
To show heartbeat, replace [options] by -b or --displayHeartBeat
    Environment           <Domain>
    fxTrade               stream-fxtrade.oanda.com
    fxTrade Practice      stream-fxpractice.oanda.com
    sandbox               stream-sandbox.oanda.com

 sudo /home/sdreep/Downloads/spark-2.0.0-bin-hadoop2.7/bin/spark-submit  --master spark://192.168.0.101:7077 --executor-memory 512M --driver-memory 1024M  --verbose --py-file: /home/sdreep/Downloads/spark-2.0.0-bin-hadoop2.7/python/lib/py4j-0.10.1-src.zip --jars /home/sdreep/Downloads/spark-2.0.0-bin-hadoop2.7/jars/py4j-0.10.1.jar --executor-cores 1 file:/home/sdreep/nabla/oanda/oanda_daemon12.py 1000

sudo /home/sdreep/Downloads/spark-2.0.0-bin-hadoop2.7/bin/spark-submit  spark.driver.extraJavaOptions=-XX:+UseG1GC -XX:NewRatio=3  ---master spark://192.168.0.101:7077 --executor-memory 512M --driver-memory 1024M  --py-files /home/sdreep/Downloads/spark-2.0.0-bin-hadoop2.7/python/lib/py4j-0.10.1-src.zip --jars /home/sdreep/Downloads/spark-2.0.0-bin-hadoop2.7/jars/py4j-0.10.1.jar --executor-cores 1 file:/home/sdreep/nabla/oanda/oanda_daemon12.py 1000
"""
from __future__ import print_function
stream_domain = 'stream-fxpractice.oanda.com'
api_domain = 'api-fxpractice.oanda.com'
access_token = '5b2e1521432ad31ef69270b682394010-4df302be03bbefb18ad70e457f3db869'
account_id = '3914094'
instruments_string = "EUR_USD,USD_JPY,GBP_USD,USD_CAD,USD_CHF,AUD_USD,CAD_JPY,EU50_EUR,SPX500_USD,HK33_HKD,SG30_SGD,XAU_EUR,XAG_EUR,DE10YB_EUR,BCO_USD,WHEAT_USD,CORN_USD"
granularity = "S5"
candles = []
import requests
# import httplib as http_client
from optparse import OptionParser
import psycopg2
import psycopg2.extras
import psycopg2.extensions
import simplejson as json
from datetime import datetime
def connect_to_api():
    try:
        s = requests.Session()
        ilist_Url = "https://" + api_domain + "/v1/instruments"
        headers = {'Authorization' : 'Bearer ' + access_token
                   # 'X-Accept-Datetime-Format' : 'unix'
                   }
        instparams = {'accountId':account_id}
        ilist_Req = requests.Request('GET', ilist_Url, headers = headers, params = instparams)
        ilist_pre = ilist_Req.prepare()
        ilist = s.send(ilist_pre, stream = True, verify = False)
        # print (ilist.text)
        return ilist
    except Exception as e:
        s.close()
        print ("Caught exception when connecting to stream\n" + str(e))

def get_instruments():
    try:
        security_list = connect_to_api()
        if security_list.status_code!=200:
            print (security_list.text)
        list = json.loads(security_list.text)
        n=0
        instrument_list = ""
        for item in list['instruments']:
            n+=1
            print (n, item['instrument'],item['displayName'],item['pip'],item['maxTradeUnits'])
            instrument_list += item['instrument']+","
        print (instrument_list[:-1])
        return instrument_list[:-1]
    except Exception as e:
        print ("Caught exception when getting instrument list\n" + str(e))

def connect_to_stream():
    instruments = get_instruments()
    try:
        s = requests.Session()
        url = "https://" + stream_domain + "/v1/prices"
        headers = {'Authorization' : 'Bearer ' + access_token
                   # 'X-Accept-Datetime-Format' : 'unix'
                   }
        params = {'instruments' : instruments, 'accountId':account_id}
        # instparams = {'accountId':account_id}
        req = requests.Request('GET', url, headers = headers, params = params)
        pre = req.prepare()
        resp = s.send(pre, stream = True, verify = False)
        # ilist_Req = requests.Request('GET', ilist_Url, headers = headers, params = instparams)
        # ilist_pre = ilist_Req.prepare()
        # ilist = s.send(ilist_pre, stream = True, verify = False)
        # print (ilist.text)

        return resp
    except Exception as e:
        s.close()
        print ("Caught exception when connecting to stream\n" + str(e))

"""
CREATE STREAM twitter_tweet (timetext, positive_score, negative_score ,time_zone,location, user,statuses_count,followers_count, lang,text);

CREATE CONTINUOUS VIEW oanda_tick_view
AS SELECT timestmp,instrument,bid,ask
FROM oanda_tick;

SELECT DISTINCT(instrument),timestmp,bid,ask FROM oanda_tick_view;

DROP STREAM oanda_tick;

CREATE USER oanda

DROP CONTINUOUS VIEW oanda_last_tick_view;

GRANT SELECT, INSERT, UPDATE, DELETE
ON ALL TABLES IN SCHEMA public
TO oanda;

CREATE CONTINUOUS VIEW oanda_last_tick_transform AS
SELECT DISTINCT instrument, MAX(timestmp), bid, ask
FROM oanda_tick
GROUP BY instrument, bid, ask;

SELECT * FROM oanda_last_tick_view;
"""


def recorder_connect():
    try:
        conn=psycopg2.connect("host='192.168.0.100' port='5432' dbname='pipeline' user='oanda' password='oanda'")
        conn.autocommit = True
        return conn
    except psycopg2.DatabaseError as e:
        print ("I am unable to connect to the database.")
        print ('Error %s' % e)
    return conn

def quote_recorder(instrument, timestamp, bid, ask):
    conn = recorder_connect()
    try:
        cur = conn.cursor()
        cur.execute('INSERT INTO oanda_tick (timestmp, instrument,  bid, ask)\
        VALUES (%s,%s,%s,%s);', (instrument, timestamp, bid, ask))
        # print (instrument, timestamp, bid, ask)
        # conn.commit()
        # cur.close()
        # conn.close()
        print (instrument, timestamp, bid, ask)

    except psycopg2.DatabaseError as e:
        print ("DB_ERROR:",'Error %s' % e)

def oanda(displayHeartbeat):
    global instrument, timestamp, bid, ask

    response = connect_to_stream()
    if response.status_code!=200:
        print (response.text)
    try:
        for line in response.iter_lines(1):
            if line:
                msg =json.loads(line)
                # print (msg)
                if 'tick' in msg:
                    instrument = msg['tick']['instrument']
                    timestamp = msg['tick']['time']
                    # timestamp = msg['tick']['time'][:-1]

                    ask = msg['tick']['ask']
                    bid = msg['tick']['bid']
                    # print (instrument, timestamp, bid, ask)
                    quote_recorder(timestamp,instrument, bid, ask)

                if 'heartbeat' in msg:
                    heartbit_ts = datetime.strptime(msg['heartbeat']['time'][:-1],'%Y-%m-%dT%H:%M:%S.%f')
                    now_ts = datetime.strptime(datetime.utcnow().isoformat(sep='T'), '%Y-%m-%dT%H:%M:%S.%f')
                    lag = now_ts - heartbit_ts
                    print ('HEARTBEAT',heartbit_ts, now_ts, lag)

    except Exception as e:
        print ("Caught exception :\n" + str(e))
        return str(e)
def main():
    global curve, data, ptr, p, lastTime, fps, x
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("-b", "--displayHeartBeat", dest = "verbose", action = "store_true",
                      help = "Display HeartBeat in streaming data")
    displayHeartbeat = False
    (options, args) = parser.parse_args()
    if len(args) > 1:
        parser.error("incorrect number of arguments")
    if options.verbose:
        displayHeartbeat = True
    oanda(displayHeartbeat)

if __name__ == '__main__':

    main()
