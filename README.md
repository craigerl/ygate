
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
- [x] convert telnet sandbox to socket(s)
- [ ] lower latency
- [ ] duplicate detection and suppression with timer
- [ ] binary inspection, handle all encodings, utf-8 errors ignored for now
- [x] reconnect socket after server disconnets 


Testing/QA:
- [x] Yaesu FTM-500
- [x] Yaesu FTM-400
- [x] Yaesu FTM-100
- [ ] Yaesu FTM-300
- [ ] Yaesu FT1DR  (not possible, aprs data on com port incomplete)
- [ ] Yaesu FT2DR   "
- [ ] Yaesu FT3DR   "
- [ ] Yaesu FT5DR   "

## Install

Download [ygate.py](https://raw.githubusercontent.com/craigerl/ygate/master/ygate.py) to your system, Raspberry Pi OS Buster, or any Linux system with Python3.

    wget https://raw.githubusercontent.com/craigerl/ygate/master/ygate.py

Make the file executable, run the command:

    chmod 755 ygate.py

Edit the top of the file (**nano ygate.py**), and modify these variables to match your station:

        USER = "KM6XXX-1"
        PASS = "00000"
        LAT  = "3819.70N"
        LONG = "12019.15W"
        SERIAL_PORT = 'COM9'
        

Your APRS password may be generated here:  https://apps.magicbug.co.uk/passcode/

The latitude/longitude fields have their decimal point shifted two places to the right.

For example:

        38 degrees and 22.56 minutes North
        120 degrees and 19.15 minutes West

becomes:

        LAT  = "3822.56N"
        LONG = "12019.15W"

If you see errors like missing modules, or "not defined", you might need additional python libraries.
For example, if you see serial errors, make sure pyserial is installed.
        "sudo pip3 install pyserial"

## Configure Radio 

Hold down the **[DISP/Setup]** button, and change the following values:

**APRS Menu**

    Modem:     On
  
**Data menu**

    Speed:     1200
    Output:    Packet
    WP Format: NMEA9
  
Connect the USB cable Yaesu provided in the box  (USB to serial cable) to your computer/Pi.  For a Pi, a USB adapter cable will be needed to fit the micro USB port.

## Run ygate

    ./ygate.py

## Example output

    # aprsc 2.1.10-gd72a17c
    # logresp KM6LYW-4 verified, server T2PR
    W6SCR>APMI06,W6SCR-4*,qAR,KM6LYW-4:@241522z3942.75N/12147.10W/Butte SAR Headquarters 14.0volts
    KS4FUN-12>3X0PRU,KM6ZTH-4*,WIDE2-1,qAR,KM6LYW-4:`2^=l!U+/'"4>}|(?%r'l|!wkO!|3
    KB6EC-9>APDR10,K6CDF-8,ACARC-1,WIDE2*,qAR,KM6LYW-4:!3942.16N\12131.36WWKB6EC Location
    >>> Internet packet not gated:  NC6J-1>APBPQ1,K6FGA-1,KM6ZTH-4*,qAR,KM6LYW-4:}W6TKD-9>SX3XUT,TCPIP,NC6J-1*:`1`/",^j/]"4x}=
    >>> Internet packet not gated:  NC6J-1>APBPQ1,K6FGA-1,ACARC-1,WIDE2*,qAR,KM6LYW-4:}W6TKD-9>SX3XUT,TCPIP,NC6J-1*:`1`/",^j/]"4x}=
    PLKPIN>APOT30,ALDER,ACARC-1,WIDE2*,qAR,KM6LYW-4:!3845.70N/12034.70W# 12.6V N6YBH Pollock Pines DIGI
    KJ6DZB-3>APAVT5,ALDER,ACARC-1,WIDE2*,qAR,KM6LYW-4:=3849.70N/12002.21W>025/000/A=007453144.390MHz 4.12V  70.7F|S!).9%Q#N|
    WA6MAT-1>APT310,W6SCR-5,ACARC-1,WIDE2*,qAR,KM6LYW-4:!4032.25N\12219.49WO174/000/A=000475/Matthew's Truck

## Direwatch integration (tft display)
https://github.com/craigerl/direwatch

    ./ygate.py  > /tmp/output.txt &
    ./direwatch.py -o -l /tmp/out/put.txt
