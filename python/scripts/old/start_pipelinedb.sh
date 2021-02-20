#!/bin/bash
#!/usr/lib/pipelinedb/bin/
for (( ; ; ))
do

   pipeline-ctl -D '/home/pipeline/db/' -l '/home/pipeline/pipelinedb.log' start 
   echo "Traceback (most recent call last):$?" >&2
   sleep 1
done
