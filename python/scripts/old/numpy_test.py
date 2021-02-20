import numpy as np
import pickle as pickle
from pybrain.tools.shortcuts import buildNetwork
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.structure import *
from pybrain.tools.neuralnets import NNregression

from math import sqrt
from pybrain.datasets.supervised import SupervisedDataSet as SDS
from sklearn.metrics import mean_squared_error as MSE
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import pandas as pds
from sqlalchemy import text

import datetime
from pyoanda import Client, PRACTICE, Order

import requests
import simplejson as json

from oandapyV20 import API
from oandapyV20.exceptions import V20Error
from oandapyV20.endpoints.pricing import PricingStream

# stream_domain = 'stream-fxpractice.oanda.com'
# api_domain = 'api-fxpractice.oanda.com'
# access_token = '2b557bdd4fa3dee56c8a159ece012a48-5f5a29d25cb2e7ea1aaeba98f4bbca40'
# account_id = '9276489'
# instruments_string = "EUR_USD,USD_JPY,GBP_USD,USD_CAD,USD_CHF,AUD_USD,CAD_JPY,EU50_EUR,SPX500_USD,HK33_HKD,SG30_SGD,XAU_EUR,XAG_EUR,DE10YB_EUR,BCO_USD,WHEAT_USD,CORN_USD"

# instrument_string = 'EUR_USD,USD_JPY,GBP_USD,USD_CAD,USD_CHF,AUD_USD,CAD_JPY,BCO_USD,XAU_USD,XAG_USD'
# term1 = 'dollar'
# term2 = 'yen'

# accountID = "101-004-3748257-001"
# access_token="2b557bdd4fa3dee56c8a159ece012a48-5f5a29d25cb2e7ea1aaeba98f4bbca40"
# instruments = "EUR_USD,USD_JPY,GBP_USD,USD_CAD,USD_CHF,AUD_USD,CAD_JPY,BCO_USD,XAU_USD,XAG_USD"

accountID = "101-004-3748257-001"
access_token="2b557bdd4fa3dee56c8a159ece012a48-5f5a29d25cb2e7ea1aaeba98f4bbca40"
instruments = "EUR_USD,USD_JPY,GBP_USD,USD_CAD,USD_CHF,AUD_USD,CAD_JPY,BCO_USD,XAU_USD,XAG_USD"

client = Client(
    environment=PRACTICE,
    account_id='9276489',
    access_token='2b557bdd4fa3dee56c8a159ece012a48-5f5a29d25cb2e7ea1aaeba98f4bbca40'
)





def connect_v20(access_token,accountID,instruments):

    api = API(access_token=access_token, environment="practice")
    s = PricingStream(accountID=accountID, params={"instruments":instruments})
    response = api.request(s)

    try:
        n = 0
        for R in api.request(s):
            # print (msg['type'])
            if R['type'] == 'HEARTBIT':
                print(json.dumps(R['type'], indent=2),json.dumps(R['type']['time'], indent=2))
            if R['type'] == 'PRICE':
                instrument = json.loads(json.dumps(R['instrument'], indent=2))
                status = json.loads(json.dumps(R['status'], indent=2))
                timestamp = json.loads(json.dumps(R['time'], indent=2))
                closeoutBid = json.loads(json.dumps(R['closeoutBid'], indent=2))
                closeoutAsk = json.loads(json.dumps(R['closeoutAsk'], indent=2))
                askBook = json.loads(json.dumps(R['asks'], indent=2))
                # influx_record(R['type'])
                print(instrument, timestamp, closeoutBid, closeoutAsk)
                position_open(instrument, closeoutBid, closeoutAsk)
                # for line in askBook:
                #     price = json.loads(json.dumps(line["price"], indent=2))
                #     liquidity = json.loads(json.dumps(line["liquidity"], indent=2))
                #     print (price,liquidity)
                # return instrument,closeoutBid, closeoutAsk
            # n += 1
            # if n > 125:
            #     s.terminate("maxrecs received: {}".format(MAXREC))
    except V20Error as e:
        print("Error: {}".format(e))

def search_terms(instrument):
    if instrument == 'EUR_USD':
        term1 = 'euro'
        term2 = 'dollar'
        pip = 0.00001

    if instrument == 'USD_JPY':
        term1 = 'dollar'
        term2 = 'yen'
        pip = 0.001

    if instrument == 'GBP_USD':
        term1 = 'pound'
        term2 = 'dollar'
        pip = 0.00001
    if instrument == 'CAD_JPY':
        term1 = 'canad'
        term2 = 'yen'
        pip = 0.001

    if instrument == 'AUD_USD':
        term1 = 'austral'
        term2 = 'dollar'
        pip = 0.00001
    if instrument == 'USD_CHF':
        term1 = 'dollar'
        term2 = 'franc'
        pip = 0.00001

    if instrument == 'BCO_USD':
        term1 = 'oil'
        term2 = 'dollar'
        pip = 0.001

    if instrument == 'XAU_USD':
        term1 = 'gold'
        term2 = 'dollar'
        pip = 0.001

    if instrument == 'XAG_USD':
        term1 = 'silver'
        term2 = 'dollar'
        pip = 0.001

    return term1, term2, pip




# def connect_to_api():
#     try:
#         s = requests.Session()
#         ilist_Url = "https://" + api_domain + "/v1/instruments"
#         headers = {'Authorization' : 'Bearer ' + access_token
#                    # 'X-Accept-Datetime-Format' : 'unix'
#                    }
#         instparams = {'accountId':account_id}
#         ilist_Req = requests.Request('GET', ilist_Url, headers = headers, params = instparams)
#         ilist_pre = ilist_Req.prepare()
#         ilist = s.send(ilist_pre, stream = True, verify = False)
#         # print (ilist.text)
#         return ilist
#     except Exception as e:
#         s.close()
#         print ("Caught exception when connecting to stream\n" + str(e))

# def get_instruments():
#     try:
#         security_list = connect_to_api()
#         # print (security_list)
#         if security_list.status_code!=200:
#             print (security_list.text)
#         list = json.loads(security_list.text)
#         n=0
#         instrument_list = ""
#         for item in list['instruments']:
#             n+=1
#             print (n, item['instrument'],item['displayName'],item['pip'],item['maxTradeUnits'])
#             instrument_list += item['instrument']+","
#             # print (list)
#             # instrument(instruments= 'instruments', instrument=item['instrument'], displayName=item['displayName'], pip=item['pip'],maxTradeUnits=item['maxTradeUnits'])
#
#         print (instrument_list[:-1],item['pip'])
#         return instrument_list[:-1],item['pip']
#     except Exception as e:
#         print ("Caught exception when getting instrument list\n" + str(e))
def select(instrument,term1,term2):


    aggregate_quotes_ohlc_train = """SELECT hours, open, close
            from eur_usd_ohlc_h
            order by hours
            asc
            ;"""

    aggregate_quotes_ohlc_validate = """SELECT hours, open, close
            from eur_usd_ohlc_h
            order by hours
            desc
            limit 400
            ;"""

    aggregate_quotes = """SELECT
            CAST (left(replace(replace(timestmp, '-',''), 'T',''), 10) as integer) as hours,
            (array_agg(bid ORDER BY timestmp ASC))[1] op,
            (array_agg(bid ORDER BY timestmp DESC))[1] cl
            FROM public.quotes
            where instrument like '"""+instrument+"""'
            GROUP BY hours
            ORDER BY hours
            asc
            ;"""

    aggregate_ttrss = """SELECT count_"""+term2+""".hours,count_"""+term1+""",count_"""+term2+"""  from
                (SELECT
                    cast (to_char(date_updated,'yyyyMMddHH24') as integer) as hours,
                    count(content) as count_"""+term1+""",
                    string_agg((lower(replace(content, '&#039;',''))), ' ') as content
                FROM
                    public.ttrss_entries ttrss_entries
                where content like '%"""+term1+"""%'
                GROUP BY hours
                order by hours
                asc
                    ) count_"""+term1+"""
            INNER JOIN
                (SELECT
                    CAST (to_char(date_updated,'yyyyMMddHH24') as integer) as hours,
                    count(content) as count_"""+term2+""",
                    string_agg((lower(replace(content, '&#039;',''))), ' ') as content
                FROM
                    public.ttrss_entries ttrss_entries
                where content like '%"""+term2+"""%'
                GROUP BY hours
                order by hours
                asc
                ) count_"""+term2+""" ON count_"""+term1+""".hours=count_"""+term2+""".hours
            ;"""

    aggregate_quotes_last_hour = """SELECT
            CAST (left(replace(replace(timestmp, '-',''), 'T',''), 10) as integer) as hours,
            (array_agg(bid ORDER BY timestmp ASC))[1] op,
            (array_agg(bid ORDER BY timestmp DESC))[1] cl
            FROM quotes
            where instrument like '"""+instrument+"""'
            GROUP BY hours
            ORDER BY hours
            desc
            LIMIT 1;"""

    aggregate_ttrss_last_hour = """SELECT count_"""+term2+""".hours,count_"""+term1+""",count_"""+term2+"""  from
                (SELECT
                    cast (to_char(date_updated,'yyyyMMddHH24') as integer) as hours,
                    count(content) as count_"""+term1+""",
                    string_agg((lower(replace(content, '&#039;',''))), ' ') as titles
                FROM
                    ttrss_entries ttrss_entries
                where content like '%"""+term1+"""%'
                GROUP BY hours
                order by hours
                desc
                    ) count_"""+term1+"""
            INNER JOIN
                (SELECT
                    CAST (to_char(date_updated,'yyyyMMddHH24') as integer) as hours,
                    count(content) as count_"""+term2+""",
                    string_agg((lower(replace(content, '&#039;',''))), ' ') as titles
                FROM
                    ttrss_entries ttrss_entries
                where content like '%"""+term2+"""%'
                GROUP BY hours
                order by hours
                desc
                ) count_"""+term2+""" ON count_"""+term1+""".hours=count_"""+term2+""".hours
            ;"""

    return (aggregate_quotes_ohlc_train,aggregate_quotes_ohlc_validate,aggregate_quotes,aggregate_ttrss,aggregate_quotes_last_hour,aggregate_ttrss_last_hour)
def pd_connect_oanda():
	try:
		engine_oanda = create_engine('postgresql://postgres:postgres@192.168.0.105:5432/oanda')
		return engine_oanda
	except create_engine as e:
		print("I am unable to connect to the database.")
		print('Error %s' % e)
	return engine_oanda
def pd_aggegate_quotes(select):
	engine_oanda = pd_connect_oanda()
	ohlc_df = pds.read_sql_query(select, engine_oanda)
	return ohlc_df
def pd_connect_ttrss():
	try:
		engine_ttrss = create_engine('postgresql://ttrss:ttrss@192.168.0.105:5432/ttrss')
		return engine_ttrss
	except create_engine as e:
		print("I am unable to connect to the database.")
		print('Error %s' % e)
def pd_aggegate_ttrss(aggregate_ttrss):
	engine_ttrss = pd_connect_ttrss()


	ttrss_df = pds.read_sql_query(text(aggregate_ttrss),engine_ttrss)
	return ttrss_df
def pd_join(select,aggregate_ttrss):
	ohlc_df = pd_aggegate_quotes(select)
	ttrss_df = pd_aggegate_ttrss(aggregate_ttrss)
	pd_join_df = pds.merge(ttrss_df, ohlc_df, on='hours', how='inner')
	print (pd_join_df)
	return pd_join_df
def pd_to_numpy(select,aggregate_ttrss):
	pd_frame = pd_join(select,aggregate_ttrss)
	# numpyMatrix = np.empty((0,7))
	numpyMatrix = pd_frame.as_matrix()
	return numpyMatrix
def train(train_select, validate_select,aggregate_ttrss):
	train = pd_to_numpy(train_select,aggregate_ttrss)
	validation = pd_to_numpy(validate_select,aggregate_ttrss)
	output_model_file = 'model.pkl'

	hidden_size = 20
	epochs = 10

	train = np.vstack((train, validation))
	x_train = train[:, 0:-1]
	y_train = train[:, -1]
	y_train = y_train.reshape(-1, 1)

	y_train = y_train.reshape(-1, 1)
	print (x_train,y_train)
	input_size = x_train.shape[1]
	target_size = y_train.shape[1]
	# print (input_size, target_size)

	# prepare dataset

	ds = SDS(input_size, target_size)
	ds.setField('input', x_train)
	ds.setField('target', y_train)

	# init and train
	# fnn = FeedForwardNetwork()

	net = buildNetwork(input_size, hidden_size, target_size, bias=True, )
	# net = NNregression(ds)
	trainer = BackpropTrainer(net,ds,verbose=True, weightdecay=0.01)

	print("training for {} epochs...".format(epochs))
	print(input_size, target_size, x_train, y_train)

	plt.axis([0, epochs, 0, 0.03])
	plt.xlabel('epoch')
	plt.ylabel('error')
	plt.ion()

	for i in range(epochs):
		mse = trainer.train()
		rmse = sqrt( mse )
		plt.scatter(i, rmse, s=5)
		plt.pause(0.00001)

		print("training RMSE, epoch {}: {}".format(i + 1, rmse))
	pickle.dump(net, open(output_model_file, 'wb'))
	return net
def validate(train_select,validate_select):

	train  = pd_to_numpy(train_select)
	validation = pd_to_numpy(validate_select)
	output_model_file = 'model_val.pkl'

	hidden_size = 100
	epochs = train.shape[0]
	continue_epochs = 100
	validation_proportion = 0.15

	# load data, join train and validation files

	# train = np.loadtxt( train_file, delimiter = ',' )
	# validation = np.loadtxt( validation_file, delimiter = ',' )
	train = np.vstack(( train, validation ))

	x_train = train[:,0:-1]
	y_train = train[:,-1]
	y_train = y_train.reshape( -1, 1 )

	input_size = x_train.shape[1]
	target_size = y_train.shape[1]

	# prepare dataset

	ds = SDS( input_size, target_size )
	ds.setField('input', x_train )
	ds.setField('target', y_train )

	# init and train

	net = buildNetwork( input_size, hidden_size, target_size, bias= True )
	trainer = BackpropTrainer(net,ds)

	train_mse, validation_mse = trainer.trainUntilConvergence( verbose = True, validationProportion = validation_proportion,
		maxEpochs = epochs, continueEpochs = continue_epochs)

	pickle.dump(net, open(output_model_file, 'wb'))
def predict(aggregate_quotes,aggregate_ttrss):
	# test_file = 'data/test.csv'
	model_file = 'model.pkl'
	output_predictions_file = 'predictions.txt'

	# load model
	net = pickle.load(open(model_file, 'rb'))

	# load data
	test = pd_to_numpy(aggregate_quotes,aggregate_ttrss)
	x_test = test[:, 0:-1]
	y_test = test[:, -1]
	y_test = y_test.reshape(-1, 1)

	# # you'll need labels. In case you don't have them...
	# y_test_dummy = np.zeros( y_test.shape )
	# y_test_dummy = np.zeros(y_test.shape)
	print (x_test, y_test)
	input_size = x_test.shape[1]
	target_size = y_test.shape[1]

	print (net.indim, net.outdim, input_size, target_size)
	assert (net.indim == input_size)
	assert (net.outdim == target_size)

	# prepare dataset

	ds = SDS(input_size, target_size)
	ds.setField('input', x_test)
	ds.setField('target', y_test)

	# predict

	p = net.activateOnDataset(ds)
	mse = MSE(y_test, p)
	rmse = sqrt(mse)

	print ("testing RMSE:", rmse, p)
	np.savetxt(output_predictions_file, p, fmt='%.6f')
	return p
def newOrder(instrument, p,pip,bid,ask):
    units = 1000
    if instrument == 'XAG_USD':
        units = 1
    if instrument == 'XAU_USD':
        units = 1
    if instrument == 'BCO_USD':
        units = 1
    if p > bid:
        side = 'buy'
        if pip == 0.001:
            price = round(((ask - bid) / 2 + bid), 3)
            takeProfit = round((ask + 0.007*ask),3)
            stopLoss = round((bid - 0.002*ask),3)
        if pip == 0.00001:
            price = round(((ask - bid) / 2 + bid), 5)
            takeProfit = round((ask + 0.007*ask),5)
            stopLoss = round((bid - 0.002*ask),5)
    if p < ask:
        side = 'sell'
        if pip == 0.001:
            price = round(((ask - bid) / 2 + bid), 3)
            takeProfit = round((bid - 0.007*bid),3)
            stopLoss = round((ask + 0.002*bid),3)

        if pip == 0.00001:
            price = round(((ask - bid) / 2 + bid), 5)
            takeProfit = round((bid - 0.007 * bid), 5)
            stopLoss = round((ask + 0.002 * bid), 5)
    test_order = Order(
        instrument=instrument,
        units=units,
        side=side,
        type="market",
        stopLoss=stopLoss,
        takeProfit=takeProfit,
        # price=price,
        # now = datetime.datetime.now()
        # expire = now + datetime.timedelta(days=1)
        # expiry="GTC"
        expiry=(datetime.datetime.now() + datetime.timedelta(days=50)).isoformat('T') + "Z"

        # expiry=(datetime.datetime.now() + datetime.timedelta(days=1))
        # expiry=datetime.datetime.now()

    )
    return test_order

def position_open(instrument, bid, ask):
    try:
        # instrument, bid, ask = connect_v20(access_token, accountID, instruments)
        print(instrument, bid, ask)
        term1, term2, pip = search_terms(instrument)
        print(term1, term2, float(pip))

        try:

            position = client.get_position(instrument)
            print(position)

        except Exception as e:
            if str(e) == "OCode-404: Position not found":
                aggregate_quotes_ohlc_train, aggregate_quotes_ohlc_validate, aggregate_quotes, aggregate_ttrss, aggregate_quotes_last_hour, aggregate_ttrss_last_hour = select(
                    instrument, term1, term2)
                train(aggregate_quotes, aggregate_quotes,aggregate_ttrss)
                p=float(predict(aggregate_quotes_last_hour,aggregate_ttrss))
                # if abs((p - float(bid))/float(bid)) > 0.01:
                test_order = newOrder(instrument, p, pip, float(bid), float(ask))
                order = client.create_order(order=test_order)

            print(str(e))
    except Exception as e:
        print(str(e))




def main():
    connect_v20(access_token, accountID, instruments)





main()

