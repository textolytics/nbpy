#!/usr/bin/python2.7

#-----------------------------------------------------------------------
# twitter-stream-format:
#  - ultra-real-time stream of twitter's public timeline.
#    does some fancy output formatting.
#-----------------------------------------------------------------------

from twitter import *
import re

search_term = "bitcoin,etherium,crypto"
import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import names
from nltk.classify import PositiveNaiveBayesClassifier
#-----------------------------------------------------------------------
# import a load of external features, for text display and date handling
# you will need the termcolor module:
#
# pip install termcolor
#-----------------------------------------------------------------------
from time import strftime
from textwrap import fill
from termcolor import colored
from email.utils import parsedate
import psycopg2
import psycopg2.extras
import psycopg2.extensions
import pygeohash as pgh
#-----------------------------------------------------------------------
# load our API credentials
#-----------------------------------------------------------------------
# config = {}
# execfile("config.py", config)
# Account textolytics@gmail.com
consumer_key = 'YnH734IEAE0gxCa2hupX70KJQ'
consumer_secret = 'ohMDIJO8BwuFLV1d1NdHnWnmKWT8zXzg0QL9BHS07o5D5dtylq'
access_key = '769882262208974848-EEPdY1hzDvNJ5CQbJgwoVhGI5MIJqDF'
access_secret = 'IpYvXUXcNDwkOmhvqGWktn7EtTGTdvMG1dLCWUDdGimbl'
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

def recorder_connect():
    try:
        conn=psycopg2.connect("host='192.168.0.104' port='5432' dbname='research' user='postgres' password='postgres'")
        conn.autocommit = True
        return conn
    except psycopg2.DatabaseError as e:
        print ("I am unable to connect to the database.")
        print ('Error %s' % e)
    return conn

import simplejson as json
from datetime import datetime
from influxdb import InfluxDBClient
from influxdb.client import InfluxDBClientError
from influxdb import SeriesHelper


# InfluxDB connections settings
host = '192.168.0.15'
port = 8086
user = 'twitter'
password = 'twitter'
dbname = 'twitter'

myclient = InfluxDBClient(host, port, user, password, dbname,use_udp=False)


def news_recorder(tweet_id, time_colored, user_colored, text_colored):
    conn = recorder_connect()
    try:
        cur = conn.cursor()
        cur.execute('INSERT INTO news_twitter(text_colored, tweet_id, time_colored, user_colored)\
        VALUES(%s,%s,%s,%s);', (text_colored, tweet_id, time_colored, user))
        # print (instrument, timestamp, bid, ask)
        #conn.commit()
        #cur.close()
        #conn.close()
        print ("%s (%s) @%s %s" %  (time_colored, tweet_id, user_colored, text_colored))

    except psycopg2.DatabaseError as e:
        print ("DB_ERROR:",'Error %s' % e)


def pipelinedb_connect():
    try:
        conn=psycopg2.connect("host='192.168.0.104' port='5432' dbname='pipeline' user='twitter' password='twitter'")
        return conn
    except psycopg2.DatabaseError as e:
        print ("I am unable to connect to the database.")
        print ('Error %s' % e)
    return conn

def pipeline_record(timetext, positive_score, negative_score ,time_zone,location_colored, user_colored,statuses_count,followers_count, lang,text_colored):
    conn = pipelinedb_connect()
    try:
        cur = conn.cursor()
        cur.execute('INSERT INTO twitter_stream_tweets(timestmp, positive_score, negative_score ,time_zone,location_name, user_name,statuses_count,followers_count,tweet_language, tweet)\
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);', (timetext, positive_score, negative_score ,time_zone,location_colored, user_colored,statuses_count,followers_count, lang,text_colored))
        # print (instrument, timestamp, bid, ask)
        conn.commit()
        cur.close()
        # conn.close()
        print ("%s|%s|%s|%s|%s|@%s|%s|%s|%s|%s" % ((time_colored, positive_score, negative_score ,time_zone,location_colored, user_colored,statuses_count,followers_count, lang,text_colored)))
    except psycopg2.DatabaseError as e:
        print ("DB_ERROR:",'Error %s' % e)

def word_feats(words):
    return dict([(word, True) for word in words])

# positive_vocab = ['awesome', 'outstanding', 'fantastic', 'terrific', 'good', 'nice', 'great', ':)']
# negative_vocab = ['bad', 'terrible', 'useless', 'hate', ':(']
neutral_vocab = ['movie', 'the', 'sound', 'was', 'is', 'actors', 'did', 'know', 'words', 'not']
negative_vocab = [line.strip() for line in open("../../text/opinion_lexicon/negative-words.txt", 'r')]
positive_vocab = [line.strip() for line in open("../../text/opinion_lexicon/positive-words.txt", 'r')]
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
    # print (pos,neg)
    # for word in words:
    # 	positiveclassResult = classifier_positive.classify(word_feats(word))
    # 	if positiveclassResult == 'pos':
    # 		positive = positive + 1
    #

    # print('Positive: ' + str(float(pos) / len(words)))
    # print('Negative: ' + str(float(neg) / len(words)))
    if neg == len(words):
        neg = 0
    fneg = neg
    return str(float(pos) / len(words)), str(float(neg) / len(words))

def twitter(SeriesHelper):
    try:
        for tweet in tweet_iter:
        #	print tweet
        # turn the date string into a date object that python can handle
            tweet_id = tweet["id_str"]
            location_colored = colored(tweet["user"]["location"],"red")
            place = json.dumps(tweet['place'])
            location = tweet["user"]["location"]
            timestamp = parsedate(tweet["created_at"])
            # now format this nicely into HH:MM:SS format
            timetext = strftime("%Y%m%d%H%M%S", timestamp)
            retweet_count =  tweet["retweet_count"]
            # colour our tweet's time, user and text
            time_colored = colored(timetext, color = "white", attrs = ["bold"])
            user_colored = colored(tweet["user"]["screen_name"], "green")
            user = tweet["user"]["screen_name"]
            followers_count = tweet["user"]["followers_count"]
            lang = tweet["user"]["lang"]
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
            coordinates = json.dumps(tweet['coordinates'])
            long = 0
            lat = 0
            geohash = ''
            pgeoa = ''
            pgeob = ''
            pgeoc = ''
            pgeod = ''
            if place != 'null':
                place_keys = tweet['place'].keys()
                # print (place_keys)
                place_tag = []

                place_tag = tweet['place']['bounding_box']['coordinates']
                for fields in place_tag:
                    for i, f in enumerate(fields):
                        if i == 0:
                            pgeoalat = f[1]
                            pgeoalong = f[0]
                            print (colored(pgeoalat, "blue"), colored(pgeoalong, "blue"))
                            geohash = pgh.encode(pgeoalat, pgeoalong)
                        if i == 1:
                            pgeob = pgh.encode(f[0], f[1])
                        if i == 2:
                            pgeoc = pgh.encode(f[0], f[1])
                        if i == 3:
                            pgeod = pgh.encode(f[0], f[1])
                    print (pgeoa, pgeob, pgeoc, pgeod)

                polygon = tweet['place']['bounding_box']
                print (colored(place_tag, "blue"))
                if coordinates != 'null':
                    coordinates_keys = tweet['coordinates'].keys()
                    coordinates = str(tweet['coordinates']['coordinates'])
                    # print (coordinates_keys)
                    # print (tweet['coordinates']['coordinates'])
                    long = tweet['coordinates']['coordinates'][1]
                    lat = tweet['coordinates']['coordinates'][0]
                    geohash = pgh.encode(long, lat)
                    print (long, lat, colored(geohash, "green"))

            positive_score_colored =  colored(positive_score,"green")
            negative_score_colored = colored(negative_score,"red")
            time_zone_colored = colored(time_zone,"blue")

            # xterm = pattern.sub ( search_term.upper () , text )
            print ("%s|  %s %s | %s |%s| @%s |%s| %s [%s] %s %s" % (
                time_colored, positive_score_colored, negative_score_colored, time_zone_colored, location_colored, geohash, user_colored,
                statuses_count,
                followers_count, lang, text_colored))
            tweet_json = [
                {
                    "measurement": "crypto",
                    "tags": {
                        "lang": lang,
                        "location": location,
                        "time_zone": time_zone,
                        "user_name": user,
                        "geohash": geohash
                    },
                    "created_at": timestamp,
                    "fields": {
                        "id": tweet_id,
                        "followers_count": followers_count,
                        "retweet_count": retweet_count,
                        "text": text,
                        "user": user,
                        "geohash": geohash,
                        "pgeoa": pgeoa,
                        "pgeob": pgeob,
                        "pgeoc": pgeoc,
                        "pgeod": pgeod,
                        "statuses_count": statuses_count,
                        "coordinates": coordinates,
                        "long_coordinates": long,
                        "lat_coordinates": lat,
                        "positive_score": positive_score ,
                        "negative_score": negative_score

                    }
                }
             ]

            myclient.write_points(tweet_json)
            #pipeline_record(timetext, positive_score, negative_score, time_zone, location_colored, user_colored,statuses_count, followers_count, lang, text_colored)

    except InfluxDBClientError as e:
        print("DB_ERROR:", 'Error %s' % e)






def main():
    # global curve, data, ptr, p, lastTime, fps, x
    # usage = "usage: %prog [options]"
    # parser = OptionParser(usage)
    # parser.add_option("-b", "--displayHeartBeat", dest = "verbose", action = "store_true",
    #                   help = "Display HeartBeat in streaming data")
    # displayHeartbeat = False
    # (options, args) = parser.parse_args()
    # if len(args) > 1:
    #     parser.error("incorrect number of arguments")
    # if options.verbose:
    #     displayHeartbeat = True
    twitter(SeriesHelper)



if __name__ == '__main__':
    main()
