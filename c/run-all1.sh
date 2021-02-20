#!/bin/sh
for i in $(echo $(python /home/sdreep/nabla/oanda_daemon13.py) | tr " " ,"\n")
    do
      # process
      echo i
      ./eurusdcount
    done
