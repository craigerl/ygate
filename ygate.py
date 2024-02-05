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

# User specific constants (please fill these out accordingly)
USER = "W9EN-10"
PASS = "24981"
LAT  = "3347.42N"
LONG = "11153.77W"
SERIAL_PORT = 'COM9'

# APRS-IS specific constants
HOST = "noam.aprs2.net"  # north america tier2 servers round robin
PORT = 14580
ICON = "&"
OVERLAY = "R"

# My position string constants
POSITION = LAT + OVERLAY + LONG
TO_CALL = ">APZYG2"  # Software version used as TOCALL
MESSAGE = "Yaesu ygate https://github.com/craigerl/ygate"
MY_POSITION_STRING = USER + TO_CALL + ",TCPIP*:!" + POSITION + ICON + MESSAGE + "\r\n"
MY_LOGIN_STRING = "user " + USER + " pass " +  PASS + " vers ygate.py 1.00\n"


# Ctrl-c handler
def signal_handler(signal, frame):
   print("Ctrl+C detected, exiting.")
   ser.close
   sock.shutdown(0)
   sock.close()
   time.sleep(2)
   os._exit(0)  

# Spawn a thread that sends my position every 1800 seconds
def send_my_position():
  threading.Timer(1800, send_my_position).start()
  send_to_aprsis(MY_POSITION_STRING)
  print(MY_POSITION_STRING.strip())

# Try to connect to aprs-is
def connect_to_aprsis():
  try: 
    sock.connect((HOST, PORT))
    time.sleep(1)
    sock.send(bytes(MY_LOGIN_STRING, 'utf-8'))
    # Print the first two lines from aprsis server to see version and server name
    print(sock_file.readline().strip())
    print(sock_file.readline().strip())
  except:
    print("Unable to connect to APRS-IS server, retrying...\n")
    try:
      sock.connect((HOST, PORT))
      time.sleep(1)
      sock.send(bytes(MY_LOGIN_STRING, 'utf-8'))
      # Print the first two lines from aprsis server to see version and server name
      print(sock_file.readline().strip())
      print(sock_file.readline().strip())
    except Exception as e:
      # time to bail
      print(e + "\n")
      os._exit(1)

# Try to send to aprs-is
def send_to_aprsis(packet_string):
  try:
    sock.send(bytes(packet_string, 'utf-8'))
  except ConnectionResetError:
    connect_to_aprsis()
    time.sleep(1)
    try:
      sock.send(bytes(packet_string, 'utf-8'))
    except Exception as e:
      # send retry failed, time to bail
      print("Unable to send " + packet_string)
      print(e + "\n")
      os._exit(1)
  except Exception as e:
    # something bad happenned, time to bail
    print("Unable to send " + packet_string)
    print(e + "\n")
    os._exit(1)


# Register the ctrl-c signal handler
signal.signal(signal.SIGINT, signal_handler)

# Setup a socket for connection to APRS-IS server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_file = sock.makefile(mode='r')
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # disable nagle algorithm   
sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 512)  # buffer size

# Connect to the server
connect_to_aprsis()

# Start the position beacon thread
send_my_position()

# Now open the specified serial port
try:
  ser = serial.Serial(SERIAL_PORT, 9600)
except Exception as e:
  print("Unable to open " + SERIAL_PORT + "\n")
  print(e + "\n")
  os._exit(1)

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
     send_to_aprsis(packet + "\r\n")

# We never get here, but these things happen in the ctrl-c handler
ser.close()
sock.shutdown(0)
sock.close()
