#!/usr/bin/python
import subprocess
from time import gmtime, strftime
def pred():
    while True:
        p = subprocess.Popen(["/home/sdreep/nabla/eurusdcount1"], stdout=subprocess.PIPE)
        ln = p.stdout.readline()

        print strftime("%H:%M:%S", gmtime()) + " received " + ln

pred()