#!/bin/sh
#!/bin/bash
#log_file=""/home/sdreep/nabla/logs/oanda_out_log.txt-`date +'%Y-%m-%d_%H-%M-%S'`""
#| tee -a "$log_file"

quotes=$(python /home/sdreep/nabla/oanda_daemon13.py)
result='quotes'
exco $(quotes)
