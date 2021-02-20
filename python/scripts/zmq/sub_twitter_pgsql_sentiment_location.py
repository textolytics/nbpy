#!/usr/bin/python3.5
#-----------------------------------------------------------------------
# twitter-stream-format:
#  - ultra-real-time stream of twitter's public timeline.
#    does some fancy output formatting.
#  new-service.sh "sub_twitter_influx_sentiment_location" "sub_twitter_influx_sentiment_location" "/usr/bin/python3.5 /home/zmq/nabla/python/scripts/zmq/sub_twitter_influx_sentiment_location.py" "zmq"
#-----------------------------------------------------------------------

from twitter import *
import re
import simplejson as json
import datetime
search_term = "euro,dollar"
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
# consumer_key = 'YnH734IEAE0gxCa2hupX70KJQ'
# consumer_secret = 'ohMDIJO8BwuFLV1d1NdHnWnmKWT8zXzg0QL9BHS07o5D5dtylq'
# access_key = '769882262208974848-EEPdY1hzDvNJ5CQbJgwoVhGI5MIJqDF'
# access_secret = 'IpYvXUXcNDwkOmhvqGWktn7EtTGTdvMG1dLCWUDdGimbl'

# Account yakub@europe.com
consumer_key = 'ToYgyzFSZdkTLYHDaGpfkoyLH'
consumer_secret = 'lLwXeUPvzgma9C80tbHwpTZGJgB1EXJjCfjKsc6Swu9WDdnt0T'
access_key ='223681612-bVGDwvUo3z5RibI0hsQ2MOTrO8ZBTC0QnOYNP9hB'
access_secret ='Z7TJXH27m3aBknbHIQ8Y12oXKaSPqVXGcimXIXGlcot5Y'

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
        conn=psycopg2.connect("host='192.168.0.120' port='5432' dbname='twitter' user='twitter' password='twitter'")
        return conn
    except psycopg2.DatabaseError as e:
        print ("I am unable to connect to the database.")
        print ('Error %s' % e)
    return conn

def pipeline_record(tweet_id_int, time_num , time_timestamp, pos_score_rnd, neg_score_rnd, time_zone, location, geohash,
            user,
            statuses_count,
            followers_count, lang, text):
    conn = pipelinedb_connect()
    try:
        cur = conn.cursor()

        # CREATE
        # TABLE
        # twitter_tweets(tweet_id_num
        # numeric, time_num
        # numeric, tweet_id_str
        # text, time_str
        # text, pos_score_rnd
        # float, neg_score_rnd
        # float, time_zone
        # text, location
        # text, geohash
        # text, user_name
        # text, statuses_count
        # integer, followers_count
        # integer, lang
        # text, tweet_text
        # text);
        #


        cur.execute('INSERT INTO twitter_tweets(tweet_id_num, time_num, time_timestamp, pos_score_rnd, neg_score_rnd, time_zone, location, geohash, user_name, statuses_count, followers_count, lang, tweet_text)\
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);', (tweet_id_int, time_num, time_timestamp, pos_score_rnd, neg_score_rnd, time_zone, location, geohash,
            user,
            statuses_count,
            followers_count, lang, text))
        # print (instrument, timestamp, bid, ask)
        conn.commit()
        # cur.close()
        # conn.close()
        # print("%s|%s|%s|%s|%s|%s|%s|@%s|%s|%s[%s]%s[%s]" % (tweet_id_int, time_num, time_timestamp, pos_score_rnd, neg_score_rnd, time_zone, location, geohash,
        #     user,
        #     statuses_count,
        #     followers_count, lang, text))
    except psycopg2.DatabaseError as e:
        print ("DB_ERROR:",'Error %s' % e)

def word_feats(words):
    return dict([(word, True) for word in words])

# positive_vocab = ['awesome', 'outstanding', 'fantastic', 'terrific', 'good', 'nice', 'great', ':)']
# negative_vocab = ['bad', 'terrible', 'useless', 'hate', ':(']
neutral_vocab = ['movie', 'the', 'sound', 'was', 'is', 'actors', 'did', 'know', 'words', 'not']
# negative_vocab = [line.strip() for line in open("../zmq/text/opinion_lexicon/negative-words.txt", 'r')]
# positive_vocab = [line.strip() for line in open("../zmq/text/opinion_lexicon/positive-words.txt", 'r')]

negative_vocab = [line.strip() for line in open("/home/zmq/nabla/python/scripts/zmq/text/opinion_lexicon/negative-words.txt", 'r')]
positive_vocab = [line.strip() for line in open("/home/zmq/nabla/python/scripts/zmq/text/opinion_lexicon/positive-words.txt", 'r')]

positive_features = [(word_feats(pos), 'pos') for pos in positive_vocab]
negative_features = [(word_feats(neg), 'neg') for neg in negative_vocab]
neutral_features = [(word_feats(neu), 'neu') for neu in neutral_vocab]
train_set = negative_features + positive_features + neutral_features
# print (train_set)
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
    #     positiveclassResult = classifier_positive.classify(word_feats(word))
    #     if positiveclassResult == 'pos':
    #         positive = positive + 1
    #

    # print('Positive: ' + str(float(pos) / len(words)))
    # print('Negative: ' + str(float(neg) / len(words)))
    if neg == len(words):
        neg = 0
    fneg = neg
    return str(float(pos) / len(words)), str(float(neg) / len(words))
geohash = ''
def twitter():
    try:
        for tweet in tweet_iter:
            coordinates = json.dumps(tweet['coordinates'])
            if coordinates != 'null':
                coordinates_keys = tweet[ 'coordinates' ].keys ()
                coordinates = str ( tweet[ 'coordinates' ][ 'coordinates' ] )
                # print (coordinates_keys)
                # print (tweet['coordinates']['coordinates'])
                long = tweet[ 'coordinates' ][ 'coordinates' ][ 1 ]
                lat = tweet[ 'coordinates' ][ 'coordinates' ][ 0 ]
                geohash = pgh.encode ( long , lat )
                # print ( long , lat , colored ( geohash , "green" ) )

            # print (tweet)
        # turn the date string into a date object that python can handle
            tweet_id = tweet["id_str"]
            tweet_id_str = str(tweet_id)
            tweet_id_int = int(tweet_id)

            location_colored = colored(tweet["user"]["location"],"red")
            place = json.dumps(tweet['place'])
            location = tweet["user"]["location"]
            timestamp = parsedate(tweet["created_at"])
            # now format this nicely into HH:MM:SS format
            time_str = str(strftime("%Y%m%d%H%M%S", timestamp))
            time_timestamp = str(strftime("%Y-%m-%dT%H:%M:%S", timestamp))
            time_num = int(time_str)
            retweet_count =  tweet["retweet_count"]
            # colour our tweet's time, user and text
            time_colored = colored(time_str, color = "white", attrs = ["bold"])
            user_colored = colored(tweet["user"]["screen_name"], "green")
            user = tweet["user"]["screen_name"]
            followers_count = tweet["user"]["followers_count"]
            lang = tweet["user"]["lang"]
            text = tweet["text"]
            # Sentiment analysis
            positive_score, negative_score = sentiment_analysis_predict(text)
            pos_score = float(positive_score)
            neg_score = float(negative_score)
            neg_score_rnd = round(neg_score,2)
            pos_score_rnd = round(pos_score,2)
            time_zone = tweet["user"]["time_zone"]
            statuses_count = tweet["user"]["statuses_count"]
            # replace each instance of our search terms with a highlighted version
            text_colored = pattern.sub(colored(search_term.lower(), "yellow"), text)
            # add some indenting to each line and wrap the text nicely
            indent = " " * 0
            text_colored = fill(text_colored, 180, initial_indent = indent, subsequent_indent = indent)
            long = 0
            lat = 0
            geohash = 'None'
            pgeoa = ''
            pgeob = ''
            pgeoc = ''
            pgeod = ''
            polygon = ''
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
                            # print (colored(pgeoalat, "blue"), colored(pgeoalong, "blue"))
                            geohash = pgh.encode(pgeoalat, pgeoalong)
                        if i == 1:
                            pgeob = pgh.encode(f[0], f[1])
                        if i == 2:
                            pgeoc = pgh.encode(f[0], f[1])
                        if i == 3:
                            pgeod = pgh.encode(f[0], f[1])
                    # print (pgeoa, pgeob, pgeoc, pgeod)

                polygon = tweet['place']['bounding_box']
                # print (colored(place_tag, "blue"))

            positive_score_colored = colored(pos_score_rnd,"green")
            negative_score_colored = colored(neg_score_rnd,"red")
            time_zone_colored = colored(time_zone,"blue")

            xterm = pattern.sub ( search_term.upper () , text )
            # print ("%s|%s|%s%s|%s|%s|@%s|%s|%s[%s]%s[%s]" % (tweet_id,
            #                                                  time_num, time_timestamp, positive_score_colored, negative_score_colored, time_zone_colored, location_colored, geohash, user_colored,
            #     statuses_count,
            #     followers_count, lang, text_colored))

            pipeline_record(tweet_id_int, time_num, time_timestamp, pos_score_rnd, neg_score_rnd, time_zone, location, geohash,
            user,
            statuses_count,
            followers_count, lang, text)
    except Exception as e:
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
    twitter()

if __name__ == '__main__':
    main()
