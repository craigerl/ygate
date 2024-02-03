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
PORT = 14580
USER = "KM6XXX-1"
PASS = "00000"
LAT  = "3347.42N"
LONG = "11153.77W"
ICON = "&"
OVERLAY = "R"
POSITION = LAT + OVERLAY + LONG
TO_CALL = "APZYG2"  # Software version used as TOCALL
MESSAGE = "Yaesu ygate https://github.com/craigerl/ygate"
SERIAL_PORT = 'COM9'
#SERIAL_PORT = '/dev/ttyUSB0'

# kill mainline and thread on ctrl-c
def signal_handler(signal, frame):
   print("Ctrl+C detected, exiting.")
   ser.close
   sock.shutdown(0)
   sock.close()
   time.sleep(2)
   os._exit(0)
# register the signal handler
signal.signal(signal.SIGINT, signal_handler)

# thread that says our name and position every 30 mins (1800secs)
def send_my_position():
  threading.Timer(1800, send_my_position).start()
  position_string = USER + ">" + TO_CALL + ",TCPIP*:!" + POSITION + ICON + MESSAGE + "\r\n"
  sock.send(bytes(position_string, 'utf-8'))
  print(position_string.strip())

# Setup socket connection to APRS-IS server
try:
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.connect((HOST, PORT))
except Exception as e:
  print("Unable to connect to APRS-IS server.\n")
  os._exit(1)
#sock_file = sock.makefile(mode='r', bufsize=0 )
sock_file = sock.makefile(mode='r' )
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # disable nagle algorithm
sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 512)  # buffer size

time.sleep(2)

# login to APRS-IS server
loginstring=bytes("user " + USER + " pass " +  PASS + " vers ygate.py 1.00\n", 'utf-8')
sock.send(loginstring)

# Print the first two lines from aprsis server to see version and server name as fyi
print(sock_file.readline().strip())
print(sock_file.readline().strip())

# Start position beacon thread
send_my_position()

# open the specified serial port
ser = serial.Serial(SERIAL_PORT, 9600)

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
  line = ser.readline()
  line = line.decode('utf-8', errors='ignore')
  line = line.strip('\n\r')
  if re.search('\[.*\] <UI.*>:', str(line)):      # Yaesu's nmea9-formatted suffix means we found a routing block
     routing = line
     routing = re.sub(' \[.*\] <UI.*>:', ',qAO,' + USER + ':', routing)  # drop nmea/yaesu gunk, append us to routing block
     payload = ser.readline()                     # next non-empty line is the payload, strip random number of yaesu line feeds
     payload = payload.decode('utf-8', errors='ignore')
     payload = payload.strip('\n\r')
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
     sock.send(bytes(packet + '\r\n', 'utf-8'))  # spec calls for cr/lf, just lf worked in practice too

# We never get here, but these things happen in the ctrl-c handler
ser.close()
sock.shutdown(0)
sock.close()
