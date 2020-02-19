
#-----------------------------------------------------------------------
# twitter-stream-format:
#  - ultra-real-time stream of twitter's public timeline.
#    does some fancy output formatting.
#-----------------------------------------------------------------------

import twitter
from twitter import *

import re
# from requests_oauthlib import OAuth1 as OAuth
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
		conn=psycopg2.connect("host='192.168.0.105' port='5432' dbname='research' user='postgres' password='postgres'")
		conn.autocommit = True
		return conn
	except psycopg2.DatabaseError as e:
		print ("I am unable to connect to the database.")
		print ('Error %s' % e)
	return conn



def news_recorder(tweet_id, time_colored, user_colored, text_colored):
	conn = recorder_connect()
	try:
		cur = conn.cursor()
		cur.execute('INSERT INTO news_twitter(text_colored, tweet_id, time_colored, user_colored)\
        VALUES(%s,%s,%s,%s);', (text_colored, tweet_id, timetext, user))
		# print (instrument, timestamp, bid, ask)
		#conn.commit()
		#cur.close()
		#conn.close()
		print ("%s (%s) @%s %s" %  (time_colored, tweet_id, user_colored, text_colored))

	except psycopg2.DatabaseError as e:
		print ("DB_ERROR:",'Error %s' % e)

for tweet in tweet_iter:
#	print tweet
	# turn the date string into a date object that python can handle
	tweet_id = tweet["id"]
	timestamp = parsedate(tweet["created_at"])

	# now format this nicely into HH:MM:SS format
	timetext = strftime("%Y%m%d%H%M%S", timestamp)

	# colour our tweet's time, user and text
	time_colored = colored(timetext, color = "white", attrs = [ "bold" ])
	user_colored = colored(tweet["user"]["screen_name"], "green")
	user = tweet["user"]["screen_name"]
	text_colored = tweet["text"]
	location = tweet["user"]["location"]  # replace each instance of our search terms with a highlighted version
	text_colored = pattern.sub(colored(search_term.upper(), "yellow"), text_colored)

	# add some indenting to each line and wrap the text nicely
	indent = " " * 0
	text_colored = fill(text_colored, 180, initial_indent = indent, subsequent_indent = indent)

	# now output our tweet
	# print "%s %s %s %s" % (tweet_id, time_colored, user_colored, text_colored)
	news_recorder(tweet_id, time_colored, user_colored, text_colored)
	# print "%s %s" % (time_colored, text_colored)

	# print "%s (%s) @%s %s" % (text_colored, tweet_id, time_colored, user_colored, text_colored)
# print "%s " % (text_colored)
