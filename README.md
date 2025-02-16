# dw_wled_server
Code to implement a lightweight wled server to control led strip in the dune_weaver project.  It's in pretty rough shape right now, but I've tested on/off, brightness and color change.   It's intended to take wled json requests and control the leds using the raspberry pi gpio (pin 18)

There are two files that are used:  

wled_rpi.py
wled_web_server.py

run sudo python startup.py

The only things tested are in test.sh.  Run

./test.sh 127.0.0.1 

on the pi.


