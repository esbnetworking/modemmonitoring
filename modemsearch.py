#!/usr/bin/python
import os
import subprocess
import re
import sys
import argparse
import time
import fileinput
from itertools import cycle, islice
#from subprocess import Popen, PIPE

searchmodem = open("/var/log/messages", "r")
seen = []
storedline = "temp"
for line in searchmodem:
    if "GSM" in line: 
	templine = (line.partition('attached to')[2])
	if templine.find('tty') != -1:
		if templine.strip() not in seen:
			seen.append(templine.strip())
	if not seen:
		seen = ["ttyUSB0","ttyUSB1","ttyUSB2","ttyUSB3"]
searchmodem.close()
stopprocess = 0
waitingprocess = 0

def syslogfollow():
	syslogfile = open("/var/log/syslog", "r")
	syslogfile.seek(0,2) # Go to the end of the file
    	while True:
        	line = syslogfile.readline()
        	if not line:
            		time.sleep(0.1) # Sleep briefly
            		continue
        	yield line
sysloglines = syslogfollow()
for lines1 in sysloglines:
	if ("gammu-smsd" in lines1 and "Error opening device" in lines1) or ("gammu-smsd" in lines1 and "Error getting SMS" in lines1) or ("gammu-smsd" in lines1 and "Error at init connection" in lines1): # look for gammu events in syslog
		if not stopprocess: # If gammu is not stopped
			if not waitingprocess: If I havent stopped and waiting I'm waiting for the process to stop
				waitingprocess = 1	
				proc = subprocess.Popen(["sudo", "/usr/sbin/service", "gammu-smsd", "stop"], stdout=subprocess.PIPE) # stop gammu
				proc.wait()
				stopprocess = 1
	if ("Stopped SMS daemon for Gammu" in lines1):
		searchconfig = fileinput.input("/etc/gammu-smsdrc", inplace=1)
		for configline in searchconfig:
			if "dev" in configline:
				templine2 = (configline.partition('dev/')[2])
				templine2 =  templine2.strip()
				proc = subprocess.Popen(["sudo", "/usr/bin/minicom", "-D", "/dev/"+templine2, "-S", "/home/pi/domoticz/scripts/reset_modem.minicom"], stdout=subprocess.PIPE) # turn off and on modem
				proc.wait()
				stemp = list(islice(cycle(seen),seen.index(templine2)+1,seen.index(templine2)+1+len(seen)))
				for s in stemp:
					if (s != templine2 or (s != storedline and s != "temp") and templine2 != storedline): 
						configline = configline.replace(templine2,s)
						storedline = templine2
			sys.stdout.write(configline)
		searchconfig.close()
		proc = subprocess.Popen(["sudo", "/usr/sbin/service", "gammu-smsd", "start"], stdout=subprocess.PIPE) # start gammu
		proc.wait()
		stopprocess = 0	
		waitingprocess = 0


