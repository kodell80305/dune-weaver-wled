# dw_wled_server
Code to implement a lightweight wled server to control led strip in the dune_weaver project.  It's in pretty rough shape right now, but I've tested on/off, brightness and color change.   It's intended to take wled json requests and control the leds using the raspberry pi gpio (pin 18)

There are four files that are used:  

startup.py  - starts the low level interface thread and then the flask/web server thread.

wled_rpi.py - the low level interface to control the leds.   Needs to run at root level

wled_web_server.py - web interface.  You probably don't want this to run at root.   I think flask drops levels(?) - need to verify this.    The intent is that this maintains the status/information on the leds and the low level interface just implements it.   The control is done by a message queue between flask/low level interface where the low level function pointer and all the arguments are passed in on the message queue. 

config.py - global values

run sudo python startup.py

The only things tested are the curl scripts in test.sh.  Run ./test.sh 127.0.0.1   (or use the IP address of a real WLED server.

The json parsing is minimal and a I haven't implemented any info/effects yet.   I want to work out how to change the brightness while doing effects/how to cancel effects without using yet another thread spawned from the low level interface.

Added the ability for effects/setting brightness with stopping effects (does cause restart right now ... not sure if this bothers me enough to fix it)  Only tested in simulation mode on windows, until I can test on pi.


