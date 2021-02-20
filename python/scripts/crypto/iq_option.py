import urllib3
import time
from iqoptionapi.api import IQOptionAPI
from websocket import create_connection
import json
ws = create_connection("wss://iqoption.com/echo/{randomnumber}/{randomnumber}/websocket")
print "Sending 'Cookie'..."
ws.send("{'msg': 'MY COOKIE ID', 'name': 'ssid'}")
print "Sent"
print "Reeiving..."
result = ws.recv()
print "Received '%s'" % result
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
api = IQOptionAPI("iqoption.com", "samaranight@gmail.com", "y61327061")
api.connect()
time.sleep(2)
balance = api.profile.balance
time.sleep(2)
print balance
api.setactives([73, 2])
time.sleep(2)
api.getcandles(1,1)
time.sleep(2)
data = api.candles.candles_data
print api.candles.candles_data

