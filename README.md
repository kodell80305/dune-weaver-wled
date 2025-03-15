# dune-weaver-wled

## The really short introduction

For those with short attention spans who just want to try this software, copy and paste the following into your Raspberry Pi terminal session:
```
git clone  https://github.com/kodell80305/dune-weaver-wled.git
cd dune-weaver-wled
sudo python install_scripts/startService.py start
```
That's it, you're done as far as the software is concerned.  Wait until the service has started and open a browser with the address of your Raspberry Pi.

If you want to actually see the LEDs you'll need to hook up the data from the LED to GPIO 18.

## If you're still here

This code is designed to run with the amazing [Dune Weaver](https://github.com/tuanchris/dune-weaver) project.  The Dune Weaver project uses standalone WLED devices to control the lighting for the sand table.   The project uses a Raspberry Pi to control a CNC board (mks dlc32 running Fluidnc).   Since the Raspberry Pi Zero 2w is an essential part of the system, I've implemented WLED compatible software to replace the additional ESP32 device.  The commercial WLED devices are probably far less hassle and provide some needed level shifting/wiring simplification as well as many more features, so using these might be your best choice.   I was interested in having one less device that needs to be on my network and simplifing the overall hardware design, so I've implemented this software.

The image below shows this software integrated into the Dune Weaver interface.  It looks almost exactly like the WLED interface (most of the web code is theirs, so it's not surprising).  

![Screenshot 2025-03-13 164145](https://github.com/user-attachments/assets/1a2445e7-8293-41fc-a84b-e79efbb004a6)


## Installation

The web pages are all directly from the WLED project.  I've included WLED as a submodule. Note that I have not tested this software using a virtual environment or using docker.  After cloning the repo, you should be able to run 

```
sudo python install_scripts/startService.py start
```


This is supposed do the following (supposed to - needs more fresh install testing):

* If needed, install packages from requirements.txt.  Note that the "--break-system-packages" flag is used.
* If needed, dynamically build the templates and static directories used by the flask web server from the WLED sources (eliminate websocket, hide unsupported features, work in flask, etc.)
* If needed, populate the WLED submodule
* If needed create or modify the service file
* Start the service
  
The command can also be used to stop the service (or the normal systemctl commands can be used).   You should be able to change the "WLED Configuration" IP in the Dune Weaver setting menu to point to the IP address of the Pi.  For some reason it won't connect using "127.0.0.1" but I haven't investigated this.

I may need to  modify this script to blacklist the snd_bcm2835 module and disable audio, but so far it hasn't seemed necessary.   If you want, you can install this and test it without any of the wiring/hardware changes.   The software will have no idea if anything is connected to GPIO 18.

At any time
```
git pull
sudo python install_scripts/startService.py start
```
will update the software to the latest version.


## Tests run so far
This has only been tested on the Pi Zero 2w and the Pi 4 using the latest 64 bit Bookworm OS (Version 12), freshly installed and updated.   The startService.py program (may or may not) won't work correctly on other versions/operating systems, but everything it does can be done manually.   I'm doing testing for real time, latency, memory usage.  So far everything seems very good.  Very little real time is used.  I've only tested with the 12V led strips ws2815 and the ws2811.   With 80 leds,  the The Pi Zero 2w uses about 8% of it's memory (I used the additional LEDs as a separate segment for under table lighting).   This is enough for the ws2815 on the Ombonad table or the ws2811 on with the Dune Weaver Pro version.   I'll do some additional testing with 180 leds for the ws2815 on the Dune Weaver Pro.

## Hardware configuration

I've tested only with the Raspberry Pi 4 and the Zero 2w along with the mks dlc32 boad supplying power for both the Pi and the LED strip.   Because the data signal from the Pis is marginal without level shifters it seems like good ground connections (and a good data connection) are essential.  I run a ground wire from the mks dlc32 and one from the Pi and connect them together at the LED JST connector.   I'm planning on doing some additional testing with the various methods of incorporating level shifters into the data line.

Running with patterns and 200 LEDs consumes 8% of the memory and less than 2% of the CPU on the Pi Zero 2W.   There seems to be no issue with real time, memory or latency that I've been able to detect.

Features implemented are going to be those that are used on the Dune Weaver project, mimicking the WLED web interface and JSON api.

## What it does
Isn't too hard to explain, since it should behave exactly like WLED in this environment (I'm not planning on re-inventing WLED ... this only incorporates needed/useful features for the Dune Weaver project).   It is (in my opinion) usable at this point, but it's not feature complete.  A short list of missing features includes:

* Configuration from the web interface - this is high on my list.  As of right now, strip type, number of leds, segment definitions, default color, etc. are all hard coded.  Power, brightness, color picking and a limited number of effects work.
* Timer not implemented.
* Can't modify or delete segments.  Segment 0 is reserved for the table, Segment 1 can be used (or not) for under table lighting.  
* Can't modify or delete presets or playlists.  I'll add support for any of these as needed.
* Some needed effects, playlists are not yet implemented.
* I'm not sure if the behavior matches WLED in all cases - I need to do some direct comparisions
* Parameters for effects (transition time, color, speed, etc.) are not yet implemented
* There is a lot of cleanup needed, both in the repository and I the actual code.

Everything that hasn't been hidden is there  because I'm planning on implementing it.  I don't see any difficulty or major time needed for any of these.

![Screenshot 2025-03-13 153459](https://github.com/user-attachments/assets/d07e8e04-9c14-45f4-9f9e-44ea58be0062)


Effects currently implemented - it's relatively simple to add more, but I won't support the entire WLED list.

![Screenshot 2025-03-13 153736](https://github.com/user-attachments/assets/a71a28f3-fded-46dc-bcdf-b3394b0f462a)

## Software

This is implemented as a flask web server thread and a backend thread that runs the rpi_ws281x software.  The rpi_ws281x needs to run as root, while the flask web server doesn't/shouldn't (although it currently does ...).   Even at root the flask server has permission issues with reading/writing to /dev/mem (required by rpi_281x).  I think I've overcome these with this architecture, but this is still an area of concern as I don't fully understand some of the problems I've seen.  If you have problems it's most likely from either the wiring or some arcane permission problem that occurs on your system but not mine.  Please let me know so I can work through them (the best contact would be kodell8003052gmail.com)

### Adding additional effects

Effects IDs need to match those in the official WLED documentation https://kno.wled.ge/features/effects/.   The file new_effects.js (used for the web ui patch) and the data in effects_list in wled_rpi.py need to have the effect name and id updated in them to show/work correctly.   Other than that any effect needs to call checkCancel() on a periodic basis.  I would like to keep this to the current two threads (flask/rpi_ws281x interface) so all timing/scheduling will need to be done from the rpi_ws281x thread

### Patching WEB UI

The patch process is a little tricky at times.   I've needed modify the HTML, javascript/web socket code.  For the most part I've tried to hide elements or stub them out(websocket class) rather than delete them (since deleting may cause other issues with missing resources).   When the build_web.py script is run it makes a copy of the old templates and static directory and places them in the backup_web directory (if it exists).  There is a tool compare_backups.py that looks for the differences between the files ... it's useful because you may not always notice when something went wrong when changing these pages.

## Docker, virtual environment

I haven't really investigaged running in these conditions.   Docker can be somewhat strange when it comes with interfacing with hardware and supporting this is probably never going to be a priority for me.  There should be no reason that virtual environments will be an issue, but this is untested.  The service itself currently runs at root level due to the access of /dev/mem.  

## Testing procedure and installation

Run on standard Ombonad Dune Weaver table.   Fresh install latest 64 bit Bookworm 88following the https://github.com/tuanchris/dune-weaver/wiki/Deploying-backend-code instructions.   Software version <??>
```
git clone  https://github.com/kodell80305/dune-weaver-wled.git
cd dune-weaver-wled
sudo python install_scripts/startService.py start
```

## Uninstall

The startSerice.py program will also uninstall or restart the service.
```
Usage: python install_scripts/startService.py <start|stop|restart|uninstall>
```

This one is minimally tested.   Any python packages installed will remain, so it doesn't completely restore your system to it's original state.  If you're using the Pi Zero 2w with prototype software to store your bitcoin or other really important information you might want to rethink some of your life choices ...

## API needing to be tested/supported

The WEB UI is mostly complete, with the exception of configuration.   I'm not able to use the settings_led.htm 
page. so I'll need to code that from scratch to get configuration for number of leds, led strip type
### Setting brightness, power

Should already work

### Specific Effects

Only effect id 0 (solid) and 47 (Loading) are used.  I can implement something appropriate for 47, it may not match WLED exactly.   I can add the parameters fairly easily.

Effect id 47 is Loading 
Loading	Moves a sawtooth pattern along the strip
	⋮	🎨 Fx, Bg	Speed, Fade

# Preset 1, 2

Are used.   These I'm planning on having some default, plausible action but you won't be able to modify it.
effect id, brightness, hex  (0, 47
preset 1, 2

{"bri": value}
{"on": "t"}
{"seg": [seg]}
{"ps": preset_id})        preset 1, 2
{"seg": [seg] }  seg 0, 1?


