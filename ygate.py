#!/usr/bin/python
import re
import serial
import telnetlib
import time

HOST = "noam.aprs2.net"     # north america tier2 servers round robin
USER = "KM6LYW-1"
PASS = "22452"

try:
  tn = telnetlib.Telnet(HOST, 14580)
except Exception, e:
  print "Telnet session failed.\n"
  sys.exit(-1)
time.sleep(2)
tn.write("user " + USER + " pass " +  PASS + " vers aprsd 0.99\n" )

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

