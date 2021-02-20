#!/usr/bin/python

#-----------------------------------------------------------------------
# twitter-stream-format:
#  - ultra-real-time stream of twitter's public timeline.
#    does some fancy output formatting.
#-----------------------------------------------------------------------

from twitter import *
import re
import twitter

search_term = "euro,dollar"

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
import simplejson as json
# from influxdb import InfluxDBClient
# from influxdb.client import InfluxDBClientError
# from influxdb import SeriesHelper

import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import names
from nltk.classify import PositiveNaiveBayesClassifier

#-----------------------------------------------------------------------
# InfluxDB connections settings
#-----------------------------------------------------------------------
host = '192.168.0.104'
port = 8086
user = 'twitter'
password = 'twitter'
dbname = 'twitter'
# myclient = InfluxDBClient(host, port, user, password, dbname, use_udp=False)

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
# Sentiment Analysis
#-----------------------------------------------------------------------
def word_feats(words):
	return dict([(word, True) for word in words])

# positive_vocab = ['awesome', 'outstanding', 'fantastic', 'terrific', 'good', 'nice', 'great', ':)']
# negative_vocab = ['bad', 'terrible', 'useless', 'hate', ':(']
neutral_vocab = ['movie', 'the', 'sound', 'was', 'is', 'actors', 'did', 'know', 'words', 'not']
negative_vocab = [line.strip() for line in open("/home/sdreep/nabla/opinion_lexicon/negative-words.txt", 'r')]
positive_vocab = [line.strip() for line in open("/home/sdreep/nabla/opinion_lexicon/positive-words.txt", 'r')]
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
	return str(float(pos) / len(words)), str(float(neg) / len(words))
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

def twitter(SeriesHelper):
	try:
		for tweet in tweet_iter:
			tweet_id = tweet["id_str"]
			location_colored = colored(tweet["user"]["location"],"red")
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
			tweet_json = [
				{
					"measurement": "tweet",
					"tags": {
						"lang": lang,
						"time_zone": time_zone
					},
					"created_at": timestamp,
					"fields": {
						"id": tweet_id,
						"followers_count": followers_count,
						"retweet_count": retweet_count,
						"text": text,
						"location": location,
						"user": user,
						"statuses_count": statuses_count,

					}
				}
			]
			# myclient.write_points(tweet_json,batch_size=500,time_precision='u')

			print ("%s|  %s %s | %s |%s| @%s |%s| [%s] %s %s" % (time_colored, positive_score, negative_score ,time_zone,location_colored, user_colored,statuses_count,followers_count, lang,text_colored))
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


#
# def twitter_old_influx(SeriesHelper):
# 	try:
# 		for tweet in tweet_iter:
# 			# turn the date string into a date object that python can handle
# 			# print (json.loads(json.dumps(tweet)))
# 			# lines = json.loads(tweet)
# 			# for line in lines:
# 			# print (tweet)
# 			tweet_id = tweet["id_str"]
# 			location_colored = colored(tweet["user"]["location"],"red")
# 			location = tweet["user"]["location"]
# 			# possibly_sensitive = tweet["possibly_sensitive"]
# 			# print (possibly_sensitive	,json.loads(json.dumps(tweet)))
#
# 			# withheld_in_countries = tweet["user"]["withheld_in_countries"]
# 			# if tweet["place"] != 'None':
# 			# 		print (tweet["place"])
# 			# 	place = json.loads(line)
# 			# 	print (place['country_code'])
# 			# place = json.dumps(tweet['place'])
# 			# print (place)
# 			timestamp = parsedate(tweet["created_at"])
# 			# now format this nicely into HH:MM:SS format
# 			timetext = strftime("%Y%m%d%H%M%S", timestamp)
# 			retweet_count =  tweet["retweet_count"]
# 			# colour our tweet's time, user and text
# 			time_colored = colored(timetext, color = "white", attrs = ["bold"])
# 			user_colored = colored(tweet["user"]["screen_name"], "green")
# 			user = tweet["user"]["screen_name"]
# 			followers_count = tweet["user"]["followers_count"]
# 			lang = tweet["user"]["lang"]
# 			text = tweet["text"]
#
# 			positive_score, negative_score = sentiment_analysis_predict(text)
#
#
# 			symbols = tweet["entities"]["symbols"]
# 			# for line in hashtags:
# 			# 	print (line)
# 			time_zone = tweet["user"]["time_zone"]
# 			statuses_count = tweet["user"]["statuses_count"]
# 			# if 'text' in tweet["entities"]["hashtags"]:
# 			# 	hashtags = tweet["entities"]["hashtags"]['text']
# 			# 	print (hashtags)
#
# 			# replace each instance of our search terms with a highlighted version
# 			text_colored = pattern.sub(colored(search_term.upper(), "yellow"), text)
#
# 			# add some indenting to each line and wrap the text nicely
# 			indent = " " * 0
# 			text_colored = fill(text_colored, 180, initial_indent = indent, subsequent_indent = indent)
# 			# myclient.write_points(json.dump(tweet,separators=","))
# 			tweet_json = [
# 				{
# 					"measurement": "tweet",
# 					"tags": {
# 						"lang": lang,
# 						"time_zone": time_zone
# 					},
# 					"created_at": timestamp,
# 					"fields": {
# 						"id": tweet_id,
# 						"followers_count": followers_count,
# 						"retweet_count": retweet_count,
# 						"text": text,
# 						"location": location,
# 						"user": user,
# 						"statuses_count": statuses_count,
#
# 					}
# 				}
# 			]
# 			# myclient.write_points(tweet_json,batch_size=500,time_precision='u')
#
# 	# tweet_record(id=tweet_id, created_at=timestamp, text=text, tweet='tweet')
#
# 			#    user = user,
# 			# now output our tweet
# 			# print (symbols)
# 			print ("%s |%s| %s |%s| @%s |%s| [%s] %s %s" % (time_colored,symbols,time_zone,location_colored, user_colored,statuses_count,followers_count, lang,text_colored))
# 	except InfluxDBClientError as e:
# 		print("DB_ERROR:", 'Error %s' % e)




#
# class tweet_record(SeriesHelper):
# 	# def __call__(self):
# 		# Meta class stores time series helper configuration.
# 	    class Meta:
# 	        # The client should be an instance of InfluxDBClient.
# 	        client = myclient
# 	        time_precision = 'ms'
# 	        # The series name must be a string. Add dependent fields/tags in curly brackets.
# 	        series_name = '{tweet}'
# 	        # Defines all the fields in this time series.
# 	        fields = ['tweet','text']
# 	        # Defines all the tags for the series.
# 	        tags = ['id', 'created_at']
# 	        # Defines the number of data points to store prior to writing on the wire.
# 	        bulk_size = 50
# 	        # autocommit must be set to True when using bulk_size
# 	        autocommit = True
# #
# #
# tweet_json = [
# 	{
# 		"measurement": "cpu_load_short",
# 		"tags": {
# 			"lang": lang,
# 			"time_zone": time_zone
# 		},
# 		"created_at": created_at,
# 		"fields": {
# 			"Float_value": 0.64,
# 			"Int_value": id,
# 			"Int_value": followers_count,
# 			"Int_value": retweet_count,
# 			"String_value": text,
# 			"String_value": location,
# 			"String_value": user,
# 		}
# 	}
# ]



# news_recorder(tweet_id, time_colored, user_colored, text_colored)
	# print "%s %s" % (time_colored, text_colored)
	# print "%s (%s) @%s %s" % (text_colored, tweet_id, time_colored, user_colored, text_colored)
# print "%s " % (text_colored)
# {"favorited": false, "contributors": null, "truncated": false, "text": "RT @voguemagazine: .@Beyonce may have just solidified two burgeoning trends. https://t.co/QYfj1bObon", "possibly_sensitive": false, "is_quote_status": false, "in_reply_to_status_id": null, "user":
#
# 	{"follow_request_sent": null, "profile_use_background_image": true, "default_profile_image": false, "id": 713358247344734208, "verified": false, "profile_image_url_https": "https://pbs.twimg.com/profile_images/820159495603154944/nQd6WZiK_normal.jpg", "profile_sidebar_fill_color": "DDEEF6", "profile_text_color": "333333", "followers_count": 784, "profile_sidebar_border_color": "C0DEED", "id_str": "713358247344734208", "profile_background_color": "F5F8FA", "listed_count": 4, "profile_background_image_url_https": "", "utc_offset": null, "statuses_count": 1341, "description": "the sidity girl faith .\ud83d\ude07 Singer \ud83c\udfa4 dancer \ud83d\udc83 actress \ud83c\udfad commercialsim\ud83c\udfac DANCING DOLL\u2764 #DD4L \u2764\ud83d\udca3", "friends_count": 295, "location": null, "profile_link_color": "1DA1F2", "profile_image_url": "http://pbs.twimg.com/profile_images/820159495603154944/nQd6WZiK_normal.jpg", "following": null, "geo_enabled": true, "profile_banner_url": "https://pbs.twimg.com/profile_banners/713358247344734208/1484276168", "profile_background_image_url": "", "name": "havealittleFAITH\ud83d\udc51", "lang": "en", "profile_background_tile": false, "favourites_count": 1359, "screen_name": "thatdoll_faith", "notifications": null, "url": "http://teamfaith.com", "created_at": "Fri Mar 25 13:33:54 +0000 2016", "contributors_enabled": false, "time_zone": null, "protected": false, "default_profile": true, "is_translator": false},
#  "filter_level": "low", "geo": null, "id": 828161987683172352, "favorite_count": 0, "lang": "en", "retweeted_status":
#
# {"contributors": null, "truncated": false, "text": ".@Beyonce may have just solidified two burgeoning trends. https://t.co/QYfj1bObon", "is_quote_status": false, "in_reply_to_status_id": null, "id": 828161577786421249, "favorite_count": 5, "source": "<a href=\"http://www.socialflow.com\" rel=\"nofollow\">SocialFlow</a>", "retweeted": false, "coordinates": null, "entities": {"user_mentions": [{"id": 31239408, "indices": [1, 9], "id_str": "31239408", "screen_name": "Beyonce", "name": "BEYONC\u00c9"}], "symbols": [], "hashtags": [], "urls": [{"url": "https://t.co/QYfj1bObon", "indices": [58, 81], "expanded_url": "http://vogue.cm/XFnImi4", "display_url": "vogue.cm/XFnImi4"}]}, "in_reply_to_screen_name": null, "id_str": "828161577786421249", "retweet_count": 5, "in_reply_to_user_id": null, "favorited": false, "user": {"follow_request_sent": null, "profile_use_background_image": false, "default_profile_image": false, "id": 136361303, "verified": true, "profile_image_url_https": "https://pbs.twimg.com/profile_images/738754778881228801/AOl9LYjz_normal.jpg", "profile_sidebar_fill_color": "EFEFEF", "profile_text_color": "333333", "followers_count": 12333334, "profile_sidebar_border_color": "FFFFFF", "id_str": "136361303", "profile_background_color": "131516", "listed_count": 21639, "profile_background_image_url_https": "https://pbs.twimg.com/profile_background_images/458099777918337025/LqbpyREg.jpeg", "utc_offset": -18000, "statuses_count": 53871, "description": "The official twitter page of Vogue Magazine.", "friends_count": 528, "location": "New York, NY", "profile_link_color": "009999", "profile_image_url": "http://pbs.twimg.com/profile_images/738754778881228801/AOl9LYjz_normal.jpg", "following": null, "geo_enabled": true, "profile_banner_url": "https://pbs.twimg.com/profile_banners/136361303/1484313044", "profile_background_image_url": "http://pbs.twimg.com/profile_background_images/458099777918337025/LqbpyREg.jpeg", "name": "Vogue Magazine", "lang": "en", "profile_background_tile": false, "favourites_count": 5879, "screen_name": "voguemagazine", "notifications": null, "url": "http://www.vogue.com", "created_at": "Fri Apr 23 18:33:32 +0000 2010", "contributors_enabled": false, "time_zone": "Quito", "protected": false, "default_profile": false, "is_translator": false}, "geo": null, "in_reply_to_user_id_str": null, "possibly_sensitive": false, "lang": "en", "created_at": "Sun Feb 05 08:41:21 +0000 2017", "filter_level": "low", "in_reply_to_status_id_str": null, "place": null}, "entities": {"user_mentions": [{"id": 136361303, "indices": [3, 17], "id_str": "136361303", "screen_name": "voguemagazine", "name": "Vogue Magazine"}, {"id": 31239408, "indices": [20, 28], "id_str": "31239408", "screen_name": "Beyonce", "name": "BEYONC\u00c9"}], "symbols": [], "hashtags": [], "urls": [{"url": "https://t.co/QYfj1bObon", "indices": [77, 100], "expanded_url": "http://vogue.cm/XFnImi4", "display_url": "vogue.cm/XFnImi4"}]}, "in_reply_to_user_id_str": null, "retweeted": false, "coordinates": null, "timestamp_ms": "1486284179026", "source": "<a href=\"https://mobile.twitter.com\" rel=\"nofollow\">Mobile Web (M5)</a>", "in_reply_to_status_id_str": null, "in_reply_to_screen_name": null, "id_str": "828161987683172352", "place": null, "retweet_count": 0, "created_at": "Sun Feb 05 08:42:59 +0000 2017", "in_reply_to_user_id": null}
