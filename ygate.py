#!/usr/bin/python  -u 
#
#
#  ygate - Yaesu igate                       General Public License v2
#
#  (C)2022 Craig Lamparter
#
#  This software and a raspberry pi will turn your Yaesu radio (FT1D, FTM-400) into 
#  a receive-only APRS igate.  All APRS packet traffic your radio hears will be
#  forwarded to the Internet (APRS-IS Servers) for further routing.
#
#  Hook your Yaesu amateur radio with APRS up to a Linux pc (raspberry pi) with a
#  USB cable. Set the radio to emit "packet" data in nmea9 format over the data
#  port. This script will login to an aprsis server, and relay the packet data
#  after reformatting the reduculous output from the radio into real APRS packet
#  strings.
#
#  Be sure to set your callsign, password and position below.
#

import re
import serial 
import time
import threading
import signal
import os
import socket

# Please fill these out accordingly
HOST = "noam.aprs2.net"     # north america tier2 servers round robin
USER = "KM6XXX-1"
PASS = "00000"
POSITION = "3899.70NR12099.15W"


def signal_handler(signal, frame): # kill mainline and thread on ctrl-c
   print("Ctrl+C, exiting.")
   ser.close
   os._exit(0)  
signal.signal(signal.SIGINT, signal_handler)


def send_my_position():     # thread that says our name and position every 10 mins (1200secs)
  threading.Timer(1200, send_my_position).start()
  position_string = USER + ">APRS,TCPIP*:!" + POSITION + "&Yaesu Ygate https://github.com/craigerl/ygate \n"
  sock.send(bytes(position_string, 'utf-8'))
  print(position_string.strip())


# Setup socket connection to APRS-IS server
try: 
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.connect((HOST, 14580))
except Exception as e:
  print("Unable to connect to APRS-IS server.\n")
  os._exit(1)
#sock_file = sock.makefile(mode='r', bufsize=0 )
sock_file = sock.makefile(mode='r' )
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # disable nagle algorithm   
sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 512)  # buffer size


time.sleep(2)

#login
#sock.send("user " + USER + " pass " +  PASS + " vers ygate.py 0.99\n" )
loginstring=bytes("user " + USER + " pass " +  PASS + " vers ygate.py 1.00\n", 'utf-8')
sock.send(loginstring)

#print the first two lines from aprsis server to see version and server name as fyi
print(sock_file.readline().strip())
print(sock_file.readline().strip())

#start position beacon thread
send_my_position()

# open first usb serial port
ser = serial.Serial('/dev/ttyUSB0', 9600)

# read nmea9 sentences from yaesu radio
# arrange them into aprs packet strings
# inject our callsign in the routing chain
# drop packets which shouldn't be forwarded to APRS-IS  
#
# Yaesu output looks like this:
#    AA6I>APOTU0,K6IXA-3,VACA,WIDE2* [06/02/18 13:47:54] <UI>:
#
#    /022047z3632.30N/11935.16Wk136/055/A=000300ENROUTE
#
# after removing a random number of yaesu-injected line feeds we rearrange into a real APRS packet like this:
#    AA6I>APOTU0,K6IXA-3,VACA,WIDE2*,qAO,KM6XXX-1:/022047z3632.30N/11935.16Wk136/055/A=000300ENROUTE
#  
while True:
  #line = ser.readline().strip('\n\r')
  line = ser.readline().strip(bytes('\n\r', 'utf-8'))
  if re.search('\[.*\] <UI.*>:', str(line)):      # Yaesu's nmea9-formatted suffix means we found a routing block
     routing = line.decode('utf-8', errors='ignore')
     routing = re.sub(' \[.*\] <UI.*>:', ',qAR,' + USER + ':', routing)  # drop nmea/yaesu gunk, append us to routing block
     payload = ser.readline().strip(bytes('\n\r', 'utf-8'))    # next non-empty line is the payload, strip random number of yaesu line feeds
     payload = payload.decode('utf-8', errors='ignore')
     packet = routing + payload
     if len(payload) == 0:
       print(">>> No payload, not gated:  " + packet)   # aprs-is servers also notice and drop empty packets, no spec for this
       continue
     if re.search(',TCP', routing):            # drop packets sourced from internet
       print(">>> Internet packet not gated:  " + packet) 
       continue
     if re.search('^}.*,TCP.*:', payload):     # drop packets sourced from internet in third party packets
       print(">>> Internet packet not gated:  " + packet) 
       continue
     if 'RFONLY' in routing:
       print(">>> RFONLY, not gated: " + packet) 
       continue
     if 'NOGATE' in routing:
       print(">>> NOGATE, not gated: " + packet) 
       continue
     print(packet)
#     sock.send(packet + '\r\n')  # spec calls for cr/lf, just lf worked in practice too
     sock.send(bytes(packet + '\r\n', 'utf-8'))  # spec calls for cr/lf, just lf worked in practice too

ser.close()
sock.shutdown(0)
sock.close()
