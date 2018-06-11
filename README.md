
ygate - Yaesu igate

(C)2018 Craig Lamparter

This software and a raspberry pi will turn your Yaesu radio (FT1D, FTM-400) into
a receive-only APRS igate.  All APRS packet traffic your radio hears will be
forwarded to the Internet (APRS-IS Servers) for further routing.

Hook your Yaesu amateur radio with APRS up to a Linux pc (raspberry pi) with a
USB cable. Set the radio to emit "packet" data in nmea9 format over the data
port. This script will login to an aprsis server, and relay the packet data
after reformatting the reduculous output from the radio into real APRS packet
strings.

Be sure to set your callsign, password and position below.



todo:
- [ ] invalid callsign detection, currently filtered by aprs-is servers
- [X] convert telnet sandbox to socket(s)
- [ ] lower latency  
- [ ] duplicate detection and suppression with timer


