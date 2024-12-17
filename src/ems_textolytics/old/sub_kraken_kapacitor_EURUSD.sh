#!/bin/bash
for i in $(seq 0 4000)
do
#   python '/home/sdreep/python/twitter-stream-search-dollar.py'

#	for(( ; ; ))
#	do
    	python3.5  '/home/zmq/nabla/python/scripts/zmq/sub_kraken_kapacitor_EURUSD.py'
#'/home/sdreep/nabla/python/oanda_rss_pybrain_position_order.py'
#		for(( ; ; ))
#		do
#		   python '/home/sdreep/python/news_recorder-tsla.py'
#		   echo "Traceback (most recent call last):$?" >&2
#		   sleep 1
#		done
#	   echo "Traceback (most recent call last):$?" >&2
#	   sleep 1
#	done
#  python '/home/sdreep/python/news_recorder-tsla.py'
#  echo "infinite loops [ hit CTRL+C to stop]"
   echo "Traceback (most recent call last):$?" >&2
   sleep 1
done
