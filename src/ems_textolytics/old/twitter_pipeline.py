#-----------------------------------------------------------------------
# twitter-stream-format:
#  - ultra-real-time stream of twitter's public timeline.
#    does some fancy output formatting.
#-----------------------------------------------------------------------
import twitter
from twitter import *

import re

search_term = "euro,dollar"
#-----------------------------------------------------------------------
# import a load of external features, for text display and date handling
# you will need the termcolor module:
# pip install termcolor
#-----------------------------------------------------------------------
from time import strftime
from textwrap import fill
from termcolor import colored
from email.utils import parsedate
import psycopg2
import psycopg2.extras
import psycopg2.extensions
# import tweepy

import simplejson as json
# from influxdb import InfluxDBClient
# from influxdb.client import InfluxDBClientError
# from influxdb import SeriesHelper
import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import names
from nltk.classify import PositiveNaiveBayesClassifier
# from twitter.api import Twitter

#-----------------------------------------------------------------------
# InfluxDB connections settings
#-----------------------------------------------------------------------
# host = '192.168.0.104'
# port = 8086
# user = 'twitter'
# password = 'twitter'
# dbname = 'twitter'
# myclient = InfluxDBClient(host, port, user, password, dbname, use_udp=False)

#-----------------------------------------------------------------------
# load our API credentials
#-----------------------------------------------------------------------
# config = {}
# execfile("config.py", config)

# # Account textolytics@gmail.com
# consumer_key = 'YnH734IEAE0gxCa2hupX70KJQ'
# consumer_secret = 'ohMDIJO8BwuFLV1d1NdHnWnmKWT8zXzg0QL9BHS07o5D5dtylq'
# access_key = '769882262208974848-EEPdY1hzDvNJ5CQbJgwoVhGI5MIJqDF'
# access_secret = 'IpYvXUXcNDwkOmhvqGWktn7EtTGTdvMG1dLCWUDdGimbl'


# Account sdreep@gmail.com
consumer_key = 'IOMUiT1LbcTyHkV0qYyg7A870'
consumer_secret = '09o6IVEaQIs5gtZrrrp2BGHGlGygPrJwhRmHDKrMrNR7qWxq6f'
access_key = '223681612-c97g9eyQXHq8gBZwN0VqqNul7LpBvyzJQOMjaxPL'
access_secret = 'kzPXjEW1RtXrB2CH2sQ6VwbX44EraVIo4pdGDUGJCPbkP'


#-----------------------------------------------------------------------
# Sentiment Analysis
#-----------------------------------------------------------------------
def word_feats(words):
	return dict([(word, True) for word in words])

# positive_vocab = ['awesome', 'outstanding', 'fantastic', 'terrific', 'good', 'nice', 'great', ':)']
# negative_vocab = ['bad', 'terrible', 'useless', 'hate', ':(']
neutral_vocab = ['movie', 'the', 'sound', 'was', 'is', 'actors', 'did', 'know', 'words', 'not']
negative_vocab = [line.strip() for line in open("/home/sdreep/nabla/text/opinion_lexicon/negative-words.txt", 'r')]
positive_vocab = [line.strip() for line in open("/home/sdreep/nabla/text/opinion_lexicon/positive-words.txt", 'r')]
positive_features = [(word_feats(pos), 'pos') for pos in positive_vocab]
negative_features = [(word_feats(neg), 'neg') for neg in negative_vocab]
neutral_features = [(word_feats(neu), 'neu') for neu in neutral_vocab]
train_set = negative_features + positive_features + neutral_features
print (train_set)
classifier = NaiveBayesClassifier.train(train_set)
# classifier_positive = PositiveNaiveBayesClassifier.train(positive_features,neutral_features,negative_features)

def sentiment_analysis_predict(sentence):
	# Predict
	neg = 0
	pos = 0
	# sentence = "Awesome movie, I liked it"
	sentence = sentence.lower()

	words = sentence.split(' ')
	for word in words:

			classResult = classifier.classify(word_feats(word))
			if classResult == 'neg':
				neg = neg + 1
			if classResult == 'pos':
				pos = pos + 1
	# print (neg)
	if neg == len(words):
		neg = 0
	fneg = neg
	return str(float(pos) / len(words)), str(float(fneg) / len(words))
#-----------------------------------------------------------------------
# create twitter API object
#-----------------------------------------------------------------------
auth = OAuth(access_key, access_secret, consumer_key, consumer_secret)
stream = TwitterStream(auth = auth, secure = True)
#-----------------------------------------------------------------------
# iterate over tweets matching this filter text
#-----------------------------------------------------------------------
tweet_iter = stream.statuses.filter(track = search_term)
pattern = re.compile("%s" % search_term, re.IGNORECASE)

def pipelinedb_connect():
    try:
        conn=psycopg2.connect("host='192.168.0.100' port='5432' dbname='pipeline' user='twitter' password='twitter'")
        return conn
    except psycopg2.DatabaseError as e:
        print ("I am unable to connect to the database.")
        print ('Error %s' % e)
    return conn

def pipeline_record(timetext, positive_score, negative_score ,time_zone,location_name, user_name,statuses_count,followers_count, lang,text):
    conn = pipelinedb_connect()
    try:
        cur = conn.cursor()
        cur.execute('INSERT INTO twitter_tweet(timestmp, positive_score, negative_score ,time_zone,location_name, user_name,statuses_count,followers_count, lang,text)\
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s);' , (timetext, positive_score, negative_score ,time_zone,location_name, user_name,statuses_count,followers_count, lang,text))
        # print (instrument, timestamp, bid, ask)
        conn.commit()
        cur.close()
        # conn.close()
        print ("%s|%s|%s|%s|%s|@%s|%s|%s|%s|%s" % ((timetext, positive_score, negative_score ,time_zone,location_name, user_name,statuses_count,followers_count, lang,text)))
    except psycopg2.DatabaseError as e:
        print ("DB_ERROR:",'Error %s' % e)

def twitter():
    try:
        for tweet in tweet_iter:
            tweet_id = tweet["id_str"]
            location_colored = colored(tweet["user"]["location"],"red")
            location_name = tweet["user"]["location"]
            timestmp = parsedate(tweet["created_at"])
            # now format this nicely into HH:MM:SS format
            timetext = strftime("%Y%m%d%H%M%S", timestmp)
            retweet_count =  tweet["retweet_count"]
            # colour our tweet's time, user and text
            user_colored = colored(tweet["user"]["screen_name"], "green")
            user_name = tweet["user"]["screen_name"]
            followers_count = tweet["user"]["followers_count"]
            lang = colored(tweet["user"]["lang"],"blue")
            language = tweet["user"]["lang"]
            text = tweet["text"]
            # Sentiment analysis
            positive_score, negative_score = sentiment_analysis_predict(text)
            # symbols = tweet["entities"]["symbols"]
            time_zone = tweet["user"]["time_zone"]
            statuses_count = tweet["user"]["statuses_count"]
            # replace each instance of our search terms with a highlighted version
            text_colored = pattern.sub(colored(search_term.upper(), "yellow"), text)
            # add some indenting to each line and wrap the text nicely
            indent = " " * 0
            text_colored = fill(text_colored, 180, initial_indent = indent, subsequent_indent = indent)
			# tweet_json = [
			# 	{
			# 		"measurement": "tweet",
			# 		"tags": {
			# 			"lang": lang,
			# 			"time_zone": time_zone
			# 		},
			# 		"created_at": timestamp,
			# 		"fields": {
			# 			"id": tweet_id,
			# 			"followers_count": followers_count,
			# 			"retweet_count": retweet_count,
			# 			"text": text,
			# 			"location": location,
			# 			"user": user,
            # 			"statuses_count": statuses_count,
            #
            # 		}
            # 	}
            # ]
        # myclient.write_points(tweet_json,batch_size=500,time_precision='u')
        pipeline_record(timetext, positive_score, negative_score ,time_zone,location_name, user_name,statuses_count,followers_count, lang,text)
        # print ("%s|  %s %s | %s |%s| @%s |%s| [%s] %s %s" % (time_colored, positive_score, negative_score ,time_zone,location_colored, user_colored,statuses_count,followers_count, lang,text_colored))
    except Exception as e:
        print("DB_ERROR:", 'Error %s' % e)


def main():

    twitter()
if __name__ == '__main__':

    main()

