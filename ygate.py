#!/usr/bin/python 
import re
import serial 
import telnetlib
import time
import threading

# Please fill these out accordingly
HOST = "noam.aprs2.net"     # north america tier2 servers round robin
USER = "KM6XXX-1"
PASS = "00000"
POSITION = "3899.70NR12099.15W"


def send_my_position():     # tell aprsis our name and position every 10 mins (1200secs)
  threading.Timer(1200, send_my_position).start()
  position_string = USER + ">APRS,TCPIP*:!" + POSITION + "&Yaesu Ygate https://github.com/craigerl/ygate \n"
  tn.write(position_string)
  print position_string.strip()


#connect to aprs server using telnet
try:
  tn = telnetlib.Telnet(HOST, 14580)
except Exception, e:
  print "Telnet session failed.\n"
  sys.exit(-1)
time.sleep(2)

#login
tn.write("user " + USER + " pass " +  PASS + " vers ygate.py 0.99\n" )

#read a line from the aprsis server
tnline=""
for char in tn.read_until("\n",100):
  tnline = tnline + char
tnline = tnline.replace('\n', '')
print tnline

#start position send thread
send_my_position()

ser = serial.Serial('/dev/ttyUSB0', 9600)

while True:
  line = ser.readline().strip()
  if "] <UI" in line:
     routing = line.strip()
     routing = re.sub(' \[.*\] <UI.*>:', ':', routing)  # drop nmea/yaesu gunk
     payload = ser.readline().strip() 
     packet = routing + payload
     if len(payload) == 0:
       print ">>> No payload, not gated:  " + packet 
       continue
     if ',TCP' in routing:
       print ">>> Packet from internet not gated: " + packet 
       continue
     print  packet
     tn.write(packet + '\n')

ser.close
