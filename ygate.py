#!/usr/bin/python 
import re
import serial 
import telnetlib
import time
import threading

HOST = "noam.aprs2.net"     # north america tier2 servers round robin
USER = "KM6XXX-1"
PASS = "00000"

try:
  tn = telnetlib.Telnet(HOST, 14580)
except Exception, e:
  print "Telnet session failed.\n"
  sys.exit(-1)
time.sleep(2)
#login
tn.write("user " + USER + " pass " +  PASS + " vers ygate.py 0.99\n" )
#send position, please edit and make your own
tn.write("KM6XXX-1>SXUTWP,WIDE1-1:`0Z%l\"W-\`\"9g}Yaesu Ygate https://github.com/craigerl/ygate \n")

tnline=""
for char in tn.read_until("\n",100):
  tnline = tnline + char
tnline = tnline.replace('\n', '')
print tnline

ser = serial.Serial('/dev/ttyUSB0', 9600)

while True:
  line = ser.readline().strip()
  if "] <UI" in line:
     routing = line.strip()
     payload = ser.readline().strip() 
     packet = routing + payload
     packet = re.sub(' \[.*\] <UI.*>:', ':', packet)
     print  packet
     tn.write(packet + '\n')

ser.close
