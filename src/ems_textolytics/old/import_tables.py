
from sqlalchemy import create_engine
import pandas as pds
from sqlalchemy import text
import psycopg2
import psycopg2.extras
import psycopg2.extensions


def pd_connect_ttrss():
	try:
		engine_ttrss = create_engine('postgresql://pipeline:pipeline@192.168.0.105:5432/pipeline')
		return engine_ttrss
	except create_engine as e:
		print("I am unable to connect to the database.")
		print('Error %s' % e)

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
