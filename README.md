# dune-weaver-wled

This code is designed to run with the amazing [Dune Weaver](https://github.com/tuanchris/dune-weaver) project.  The Dune Weaver project uses standalone WLED devices to control the lighting for the sand table.   The project uses a Raspberry Pi to control a commercial CNC board (mks dlc32 running Fluidnc).   Since the Raspberry Pi Zero 2w is an essential port of the system, I've implemented WLED compatible software to replace the additional ESP32 device.  The commercial WLED devices are probably far less hassle and provide some needed level shifting/wiring simplification as well as many more features, so using these might be your best choice.   I was interested in having one less device that needs to be on my network and simplifing the overall hardware design, so I've implemented this software.

## Installation

The web pages are all directly from the WLED project.  I've included WLED as a submodule. Note that I have not tested this software using a virtual environment or using docker.  After cloning the repo, you should be able to run 

```sudo python startService.py```.  

This is supposed do the following (supposed to - needs more fresh install testing):
* If needed, populate the WLED submodule
* If needed, install packages from requirements.txt.  Note that the "--break-system-packages" flag is used.
* If needed, dynamically build the templates and static directories used by the flask web server from the WLED sources (eliminate websocket, hide unsupported features, work in flask, etc.) 
* If needed create or modify the service file
* Start the service
The command can also be used to stop the service (or the normal systemctl commands can be used).   You should be able to change the "WLED Configuration" IP in the Dune Weaver setting menu to point to the IP address of the Pi.  For some reason it won't connect using "127.0.0.1" but I haven't investigated this.

I may need to  modify this script to blacklist the snd_bcm2835 module and disable audio, but so far it hasn't seemed necessary.   If you want, you can install this and test it without any of the wiring/hardware changes.   The software will have no idea if anything is connected to GPIO 18.

## Tests run so far
This has only been tested on the Pi Zero 2w and the Pi 4 using the latest 64 bit Bookworm OS (Version 12), freshly installed and updated.   The startService.py program (may or may not) won't work correctly on other versions/operating systems, but everything it does can be done manually.   I'm doing testing for real time, latency, memory usage.  So far everything seems very good.  Very little real time is used.  I've only tested with the 12V led strips ws2815 and the ws2811.   With 80 leds,  the The Pi Zero 2w uses about 8% of it's memory (I used the additional LEDs as a separate segment for under table lighting).   This is enough for the ws2815 on the Ombonad table or the ws2811 on with the Dune Weaver Pro version.   I'll do some additional testing with 180 leds for the ws2815 on the Dune Weaver Pro.

## Hardware configuration
I've tested only with the Raspberry Pi 4 and the Zero 2w along with the mks dlc32 boad supplying power for both the Pi and the LED strip.   Because the data signal from the Pis is marginal without level shifters it seems like good ground connections (and a good data connection).  I run a ground wire from the mks dlc32 and one from the Pi and connect them together at the LED jst header.   I'm planning on doing some additional testing with the various methods of incorporating level shifters into the data line.
Features implemented are going to be those that are used on the Dune Weaver project, but the intentions is to be as compatible as possible with the WLED functions.

## What it does
Isn't too hard to explain, since it should behave exactly like WLED in this environment (I'm not planning on re-inventing WLED ... this only incorporates needed/useful features for the Dune Weaver project.   It is (in my opinion) usable at this point, but it's not feature complete.  A short list of missing features includes:

* Configuration from the web interface - this is high on my list.  As of right now, strip type, number of leds, segment definitions, default color, etc. are all hard coded.  Power, brightness, color picking and a limited number of effects work.
* Timer not implemented.
* Can't modify or delete segments.  Segment 0 is reserved for the table, Segment 1 can be used (or not) for under table lighting.  
* Can't modify or delete presets or playlists.  I'll add support for any of these as needed.
* Some needed effects, playlists are not yet implemented.

Everything that hasn't been hidden is there  because I'm planning on implementing it.

![image](https://github.com/user-attachments/assets/4e5b012e-39f0-4214-ad64-e3564760a754)

Effects currently implemented - it's relatively simple to add more, but I won't support the entire WLED list.

![image](https://github.com/user-attachments/assets/1d8cc4c6-046f-4a80-a161-51e0ee746cd5)

## Software

This is implemented as a flask web server thread and a backend thread that runs the rpi_ws281x software.  The rpi_ws281x needs to run as root, while the flask web server doesn't/shouldn't (although it currently does ...).   Even at root the flask server has permission issues with reading/writing to /dev/mem (required by rpi_281x).  I think I've overcome these with this architecture, but this is still an area of concern as I don't fully understand some of the problems I've seen.  If you have problems it's most likely from either the wiring or some arcane permission problem that occurs on your system but not mine.  Please let me know so I can work through them.

## Docker, virtual environment

I haven't really investigage running in these conditions.   Docker can be somewhat strange when it comes with interfacing with hardware and supporting this is probably never going to be a priority for me.  requirements.txt can probably be trimmed down considerable ... it contains:
```
lask==2.2.2
numpy==1.24.2
openpyxl==3.1.5
paho_mqtt==2.1.0
pandas==2.2.3
platformio==6.1.18
plotly==6.0.0
Requests==2.32.3
rpi_ws281x==5.0.0
```
at the moment I'm a little confused about where some of these dependancies came from.  I'll need to start with a clean environment and regenerate this file.

## Uninstall

The startSerice.py program will also uninstall the service.
```
Usage: python startService.py <start|stop|uninstall>
```

This one is minimally tested.   Any python packages installed will remain, so it doesn't completely restore your system to it's original state.  If you're using the Pi Zero 2w to store your bitcoin or other really important information you might want to rethink some of your life choices ...


