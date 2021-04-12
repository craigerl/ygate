
ygate - Yaesu igate

(C)2021 Craig Lamparter    KM6LYW       \ \ \ \ \ \          General Public License v2

This software and a raspberry pi will turn your Yaesu radio (FTM-100, FTM-400) into
a receive-only APRS igate.  All APRS packet traffic your radio hears will be
forwarded to the Internet (APRS-IS Servers) for further routing.

Connect your Yaesu amateur radio with APRS to a Raspberry Pi (or PC) with
the Yaesu-supplied USB cable. Set the radio to output "packet" data in "nmea9"
format at "9600" bps over the com/serial port. This script will login to an
aprsis server, and relay the packet data after reformatting the reduculous
output from the radio into real APRS packet strings.

Be sure to set your callsign, password and position at the top of the script.


To do list:
- [x] translate yaesu output into aprs packets, upload to aprs-is servers
- [ ] invalid callsign detection, currently filtered by aprs-is servers
- [X] convert telnet sandbox to socket(s)
- [ ] lower latency  


Testing/QA:
- [x] Yaesu FTM-400
- [ ] Yaesu FT1DR  (not possible, aprs data on com port incomplete)
- [ ] Yaesu FT2DR   "
- [ ] Yaesu FT3DR   "
- [x] Yaesu FTM-100


