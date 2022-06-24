
## ygate - Yaesu igate

(C)2022 Craig Lamparter         \ \ \ \ \ \          General Public License v2

This software and a raspberry pi will turn your Yaesu radio (FTM-100,FTM-400)
into a receive-only APRS igate.  All APRS packet traffic your radio hears will

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
- [ ] duplicate detection and suppression with timer
- [ ] binary inspection, handle all encodings, utf-8 errors ignored for now
- [ ] reconnect socket after server disconnets 


Testing/QA:
- [x] Yaesu FTM-400
- [x] Yaesu FTM-100
- [ ] Yaesu FTM-300
- [ ] Yaesu FT1DR  (not possible, aprs data on com port incomplete)
- [ ] Yaesu FT2DR   "
- [ ] Yaesu FT3DR   "
- [ ] Yaesu FT5DR   "


## Example


$ ./ygate.py  

\# aprsc 2.1.10-gd72a17c
\# logresp KM6LYW-4 verified, server T2PR
KM6LYW-4>APRS,TCPIP*:!3854.70NR12056.15W&Yaesu Ygate https://github.com/craigerl/ygate
W4YS-1>SYQYXQ,K6FGA-1*,WIDE2-1,qAR,KM6LYW-4:`0?5pzmv/"F?}
W4YS-1>SYQYXQ,K6FGA-1,KM6ZTH-4*,qAR,KM6LYW-4:`0?5pzmv/"F?}
W4YS-1>SYQYXQ,K6FGA-1,ACARC-1,WIDE2*,qAR,KM6LYW-4:`0?5pzmv/"F?}
GAPGTE>APDW15,K6FGA-1*,WIDE2,qAR,KM6LYW-4:!3845.26NT12058.60W&PHG7290GAPGTE Rescue RX/TX igate KI6PPU
K6FGA-1>APN382,WIDE2-2,qAR,KM6LYW-4:!3914.74NS12057.91W#PHG4520/Wn,NCAn/Banner Mt/CDFVIP/A=003940
W4YS-1>SYQYWX,K6FGA-1,KM6ZTH-4*,qAR,KM6LYW-4:`0?$q+$v/"F<}
NC6J-1>APBPQ1,K6FGA-1*,WIDE2-1,qAR,KM6LYW-4:<IGATE,MSG_CNT=269,LOC_CNT=122
NC6J-1>APBPQ1,K6FGA-1,ACARC-1,WIDE2*,qAR,KM6LYW-4:<IGATE,MSG_CNT=269,LOC_CNT=122
AF6JP-9>3W5QWV,SUMMIT,ACARC-1,WIDE2*,qAR,KM6LYW-4:`1,kr>)>/`"3o}145.390MHz T136 -060_%
NC6J-1>APBPQ1,K6CDF-8,ACARC-1,WIDE2*,qAR,KM6LYW-4:!3833.48NI12114.09W&BPQ Node/WL2K and APRS IGate Sacramento
W4YS-1>SYQYUQ,K6FGA-1*,WIDE2-1,qAR,KM6LYW-4:`0>5p]@v/"FS}TT3, SmrtBcn
W4YS-1>SYQYUQ,K6FGA-1,ACARC-1,WIDE2*,qAR,KM6LYW-4:`0>5p]@v/"FS}TT3, SmrtBcn
W6SCR>APMI06,W6SCR-4*,qAR,KM6LYW-4:@241522z3942.75N/12147.10W/Butte SAR Headquarters 14.0volts
KS4FUN-12>3X0PRU,KM6ZTH-4*,WIDE2-1,qAR,KM6LYW-4:`2^=l!U+/'"4>}|(?%r'l|!wkO!|3
KB6EC-9>APDR10,K6CDF-8,ACARC-1,WIDE2*,qAR,KM6LYW-4:!3942.16N\12131.36WWKB6EC Location
>>> Internet packet not gated:  NC6J-1>APBPQ1,K6FGA-1,KM6ZTH-4*,qAR,KM6LYW-4:}W6TKD-9>SX3XUT,TCPIP,NC6J-1*:`1`/",^j/]"4x}=
>>> Internet packet not gated:  NC6J-1>APBPQ1,K6FGA-1,ACARC-1,WIDE2*,qAR,KM6LYW-4:}W6TKD-9>SX3XUT,TCPIP,NC6J-1*:`1`/",^j/]"4x}=
PLKPIN>APOT30,ALDER,ACARC-1,WIDE2*,qAR,KM6LYW-4:!3845.70N/12034.70W# 12.6V N6YBH Pollock Pines DIGI
KJ6DZB-3>APAVT5,ALDER,ACARC-1,WIDE2*,qAR,KM6LYW-4:=3849.70N/12002.21W>025/000/A=007453144.390MHz 4.12V  70.7F|S!).9%Q#N|
WA6MAT-1>APT310,W6SCR-5,ACARC-1,WIDE2*,qAR,KM6LYW-4:!4032.25N\12219.49WO174/000/A=000475/Matthew's Truck

