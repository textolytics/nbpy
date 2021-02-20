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
import curl
from optparse import OptionParser
import psycopg2
import psycopg2.extras
import psycopg2.extensions
import simplejson as json
from datetime import datetime
from influxdb import InfluxDBClient
from influxdb.client import InfluxDBClientError
from influxdb import SeriesHelper

# InfluxDB connections settings
host = '192.168.0.104'
port = 8086
user = 'oanda'
password = 'oanda'
dbname = 'tick'

myclient = InfluxDBClient(host, port, user, password, dbname,use_udp=False)

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
        # print (security_list)
        if security_list.status_code!=200:
            print (security_list.text)
        list = json.loads(security_list.text)
        n=0
        instrument_list = ""
        for item in list['instruments']:
            n+=1
            # print (n, item['instrument'],item['displayName'],item['pip'],item['maxTradeUnits'])
            instrument_list += item['instrument']+","
            # print (list)
            # instrument(instruments= 'instruments', instrument=item['instrument'], displayName=item['displayName'], pip=item['pip'],maxTradeUnits=item['maxTradeUnits'])

        print (instrument_list[:-1])
        return instrument_list[:-1]
    except Exception as e:
        print ("Caught exception when getting instrument list\n" + str(e))

def connect_to_stream():
    # instruments = get_instruments()
    instruments = instruments_string
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
#
# def recorder_connect():
#     try:
#         conn=psycopg2.connect("host='192.168.0.105' port='5432' dbname='oanda' user='oanda' password='oanda'")
#         conn.autocommit = True
#         return conn
#     except psycopg2.DatabaseError as e:
#         print ("I am unable to connect to the database.")
#         print ('Error %s' % e)
#     return conn
#
# def quote_recorder(instrument, timestamp, bid, ask):
#     conn = recorder_connect()
#     try:
#         cur = conn.cursor()
#         cur.execute('INSERT INTO quotes(instrument, timestmp, bid, ask)\
#         VALUES(%s,%s,%s,%s);', (instrument, timestamp, bid, ask))
#         # print (instrument, timestamp, bid, ask)
#         # conn.commit()
#         # cur.close()
#         # conn.close()
#         print (instrument, timestamp, bid, ask)
#
#     except psycopg2.DatabaseError as e:
#         print ("DB_ERROR:",'Error %s' % e)

# def influx_connect():
#     try:
#         influx_client = InfluxDBClient('192.168.0.104', 8086, 'oanda', 'oanda', 'quotes_tick_oanda')
#         return influx_client
#     except InfluxDBClient as e:
#         print("I am unable to connect to the database.")
#         print('Error %s' % e)

# def influx_HTTP(instrument,bid,ask):
#     domain = 'localhost:8086'
#     try:
#         s = requests.Session()
#         url = "http://" + domain + "/write?db=tick' --data-binary 'tick,"
#         headers = {'Authorization' : 'oanda' + 'oanda',
#         #            # 'X-Accept-Datetime-Format' : 'unix'
#                   }
#         params = { '--data-binary '+"'tick, instrument=" + instrument+ "bid="+str(bid)+ "ask=" +str(ask)+"'"}
#         req = requests.Request('POST', url, headers, params = params)
#         pre = req.prepare()
#         # resp = s.send(req, stream = True, verify = False)
#         resp = s.send(pre)
#
#         print (resp)
#         return resp
#     except Exception as e:
#         s.close()
#         print ("Caught exception when connecting to influx_HTTP stream\n" + str(e))

# def influx_record(msg,line,response):
#     try:
#         influx_client = influx_connect()
#         # retention_policy = 'awesome_policy'
#         # influx_client.create_retention_policy(retention_policy, '3d', 3, default=True)
#         influx_client.switch_database('tick')
#         measurement = 'quotes_tick_oanda'
#         # print (msg['key'])
#         response = influx_client.write_points(msg['tick'], msg['tick']['instrument'],msg['tick']['bid'], msg['tick']['ask'], time_precision = 'ms',protocol='line')
#         # influx_client._write_points(line)
#         # influx_client.write_points(msg['tick'], protocol='line')
#         # influx_client.send_packet(msg['tick'],  protocol='line')
#         # influx_client.write(msg['tick'],  protocol='line')
#         # ('INSERT INTO quotes(instrument, timestmp, bid, ask)\
#         #         VALUES(%s,%s,%s,%s);', (instrument, timestamp, bid, ask))
#         # result = client.query('select * from bid;')
#         print ("Result: {0}".format(result),response)
#     except Exception as e:
#         print("I am unable to record to the database.")
#         print('Error %s' % e)


# Uncomment the following code if the database is not yet created
# myclient.create_database(dbname)
# myclient.create_retention_policy('awesome_policy', '3d', 3, default=True)


# class MySeriesHelper(SeriesHelper):
#     # Meta class stores time series helper configuration.
#     class Meta:
#         # The client should be an instance of InfluxDBClient.
#         client = myclient
#         # The series name must be a string. Add dependent fields/tags in curly brackets.
#         series_name = 'events.stats.{server_name}'
#         # Defines all the fields in this time series.
#         fields = ['some_stat', 'other_stat']
#         # Defines all the tags for the series.
#         tags = ['server_name']
#         # Defines the number of data points to store prior to writing on the wire.
#         bulk_size = 5
#         # autocommit must be set to True when using bulk_size
#     autocommit = True

class tick(SeriesHelper):
    # Meta class stores time series helper configuration.
    class Meta:
        # The client should be an instance of InfluxDBClient.
        client = myclient
        # The series name must be a string. Add dependent fields/tags in curly brackets.
        series_name = '{tick}'
        # Defines all the fields in this time series.
        fields = ['bid','ask']
        # Defines all the tags for the series.
        tags = ['instrument']
        # Defines the number of data points to store prior to writing on the wire.
        bulk_size = 50
        # autocommit must be set to True when using bulk_size
        autocommit = True
#
# class instrument(SeriesHelper):
#     # Meta class stores time series helper configuration.
#     class Meta:
#         # The client should be an instance of InfluxDBClient.
#         client = myclient
#         # The series name must be a string. Add dependent fields/tags in curly brackets.
#         series_name = '{instruments}'
#         # Defines all the fields in this time series.
#         fields = ['pip','instrument', 'maxTradeUnits', 'displayName']
#         # Defines all the tags for the series.
#         tags = ['instruments']
#         # Defines the number of data points to store prior to writing on the wire.
#         bulk_size = 50
#         # autocommit must be set to True when using bulk_size
#         autocommit = True

# The following will create *five* (immutable) data points.
# Since bulk_size is set to 5, upon the fifth construction call, *all* data
# points will be written on the wire via MySeriesHelper.Meta.client.
# MySeriesHelper(server_name='us.east-1', some_stat=159, other_stat=10)
#
# # To manually submit data points which are not yet written, call commit:
# MySeriesHelper.commit()
#
# # To inspect the JSON which will be written, call _json_body_():
# MySeriesHelper._json_body_()

def oanda(displayHeartbeat):
    global instrument, timestamp, bid, ask
    # tick(SeriesHelper)
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
                    # time = msg['tick']['time'][:-1]
                    time = msg['tick']['time']
                    ask = float(msg['tick']['ask'])
                    bid = float(msg['tick']['bid'])
                    # print (msg)
                    # influx_msg = json.loads(line)
                    # tick.commit()
                    # tick._json_body_()
                    # print (tick)
                    # influx_record(msg,line,response)
                    # influx_HTTP(instrument,bid,ask)
                    print (instrument, time, bid, ask)
                    tick_json = [
                        {
                            "measurement": "oanda_tick",
                            "tags": {
                                "instrument": instrument,
                            },
                            "timestamp": time,
                            "fields": {
                                "bid": bid,
                                "ask": ask,

                            }
                        }
                    ]
                    myclient.write_points(tick_json,batch_size=500,time_precision='u')

                # if 'heartbeat' in msg:
                #     heartbit_ts = datetime.strptime(msg['heartbeat']['time'][:-1],'%Y-%m-%dT%H:%M:%S.%f')
                #     now_ts = datetime.strptime(datetime.utcnow().isoformat(sep='T'), '%Y-%m-%dT%H:%M:%S.%f')
                #     lag = now_ts - heartbit_ts
                #     print ('HEARTBEAT',heartbit_ts, now_ts, lag)
                    # quote_recorder(instrument, timestamp, bid, ask)

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
