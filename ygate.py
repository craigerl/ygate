#!/usr/bin/python  -u 
#
#
#  ygate - Yaesu igate                       General Public License v2
#
#  (C)2022-2024 Craig Lamparter
#
#  This software and a raspberry pi will turn your Yaesu radio (FT1D, FTM-400) into 
#  a receive-only APRS igate.  All APRS packet traffic your radio hears will be
#  forwarded to the Internet (APRS-IS Servers) for further routing.
#
#  Hook your Yaesu amateur radio with APRS up to a Linux pc (raspberry pi) with the
#  Yaesu USB cable. Set the radio to emit "packet" data in nmea9 format over the data
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
from enum import Enum

# User specific constants (please fill these out accordingly)
USER = "W2xxx-1"
PASS = "12345"
LAT  = "4068.92N"
LONG = "7404.44W"
#SERIAL_PORT = 'COM9' # Windows
SERIAL_PORT = '/dev/ttyUSB0' # Linux

# APRS-IS specific constants
HOST = "noam.aprs2.net"  # north america tier2 servers round robin
PORT = 14580
ICON = "&"
OVERLAY = "R"
BUFFER_SIZE = 512

# My position string constants
POSITION = LAT + OVERLAY + LONG
TO_CALL = ">APZYG2"  # Software version used as TOCALL
MESSAGE = "Yaesu ygate https://github.com/craigerl/ygate"
MY_POSITION_STRING = USER + TO_CALL + ",TCPIP*:!" + POSITION + ICON + MESSAGE + "\r\n"
MY_LOGIN_STRING = "user " + USER + " pass " +  PASS + " vers ygate.py 2.00\n"
BEACON_INTERVAL_S = 1800

# State Machine definitions
class AprsIsState(Enum):
  NOCONNECT = 1
  CONNECTED = 2
  LOGGED_IN = 3

# Ctrl-c handler
def signal_handler(signal, frame):
  print(">>> Ctrl+C detected, exiting...")
  sock.shutdown(0)
  sock.close()
  ser.close
  time.sleep(2)
  os._exit(0)

# Setup a socket for connection to APRS-IS server
def setup_socket(buffer_size):
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock_file = sock.makefile(mode='r')
  sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # disable nagle algorithm
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, buffer_size)
  return sock, sock_file

# Shutdown/close socket
def reset_socket():
  try:
    sock.shutdown(0)
    sock.close()
  except Exception as e:
    print(">>> FAILED to close socket\n")
    print(e)

# Try to connect to aprs-is
def connect_to_server():
  success = False
  try:
    sock.connect((HOST, PORT))
    success = True
  except Exception as e:
    print(">>> FAILED connect to " + HOST + "\n")
    print(e)
  finally:
    return success

# Try to send to aprs-is
def send_to_server(packet_string):
  success = False
  try:
    sock.send(bytes(packet_string, 'utf-8'))
    success = True
  except Exception as e:
    print(">>> FAILED send " + packet_string)
    print(e)
  finally:
    return success


# Register the ctrl-c signal handler
signal.signal(signal.SIGINT, signal_handler)

# Open the specified serial port
try:
  ser = serial.Serial(SERIAL_PORT, 9600)
except Exception as e:
  print(">>> FAILED to open " + SERIAL_PORT + "\n")
  print(e)
  os._exit(1)  # If we can't do this, we're done!

run_state = AprsIsState.NOCONNECT

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

# Force sending my position first time around
last_beacon_time = time.time() - BEACON_INTERVAL_S

while True:

  match run_state:

    case AprsIsState.NOCONNECT:
        sock, sock_file = setup_socket(BUFFER_SIZE)
        if (connect_to_server() == True):
          run_state = AprsIsState.CONNECTED
        else:
          reset_socket()
          time.sleep(5)

    case AprsIsState.CONNECTED:
        if (send_to_server(MY_LOGIN_STRING) == True):
          version = sock_file.readline().strip()
          print(version)
          login_response = sock_file.readline().strip()
          print(login_response)
          if ("verified" in login_response):
            print("Login SUCCESS\n")
            run_state = AprsIsState.LOGGED_IN
          else:
            print("Login FAILURE\n")
            sock.shutdown(0)
            sock.close()
            ser.close()
            os._exit(1)  # If we can't do this, we're done!

    case AprsIsState.LOGGED_IN:
      line = ser.readline()
      line = line.decode('utf-8', errors='ignore')
      line = line.strip('\n\r')
      if (re.search('\[.*\] <UI.*>:', str(line))):     # Yaesu's nmea9-formatted suffix means we found a routing block
        routing = line
        routing = re.sub(' \[.*\] <UI.*>:', ',qAO,' + USER + ':', routing)  # drop nmea/yaesu gunk, append us to routing block
        payload = ser.readline()                     # next non-empty line is the payload, strip random number of yaesu line feeds
        payload = payload.decode('utf-8', errors='ignore')
        payload = payload.strip('\n\r')
        packet = routing + payload

        # Drop those packets we shouldn't send to APRS-IS
        if (len(payload) == 0):
          print(">>> No payload, not igated:  " + packet)   # aprs-is servers also notice and drop empty packets, no spec for this
          continue
        if (re.search(',TCP', routing)):            # drop packets sourced from internet
          print(">>> Internet packet not igated:  " + packet)
          continue
        if (re.search('^}.*,TCP.*:', payload)):     # drop packets sourced from internet in third party packets
          print(">>> Internet packet not igated:  " + packet)
          continue
        if ('RFONLY' in routing):
          print(">>> RFONLY, not igated: " + packet)
          continue
        if ('NOGATE' in routing):
          print(">>> NOGATE, not igated: " + packet)
          continue

        # Send the packet to APRS-IS
        print("[0.0] " + packet)
        if (send_to_server(packet + "\r\n") == False):
          reset_socket()
          time.sleep(5)
          run_state = AprsIsState.NOCONNECT

        # Check to see if its time to beacon
        current_time = time.time()
        if (current_time - last_beacon_time > BEACON_INTERVAL_S):
          if (send_to_server(MY_POSITION_STRING) == False):
            reset_socket()
            time.sleep(5)
            run_state = AprsIsState.NOCONNECT
          else:
            print(MY_POSITION_STRING.strip())
            last_beacon_time = current_time

# We never get here, but these things happen in the ctrl-c handler
ser.close()
sock.shutdown(0)
sock.close()
