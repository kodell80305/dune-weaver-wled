# dune-weaver-wled

##
There are really several ways you can try this out.   The easiest would be to just clone it to a mac or pc and run "python app.py".  The software will detect that it doesn't have the rpi_wx28x1 module and run in simulation mode.   At this point it's just a web server.

If you do this you could also modify your Dune Weaver WLED settings to point to your PC to get an idea of how it would look from the UI.  You won't really be controlling anything, but you'll get a chance to see if the software is worth trying.

## This is early beta software

I wanted to let people know that using it would be an option - if you're doing the wiring for your Dune Weaver Pro, it might we worthwhile including an extra ground and a GPIO 18 connection to your Raspberry PI.  I was hoping to include a section on wiring.  The Raspberry PI is driving a 5 volt data line with a 3 volt signal.  I haven't seen problems with this, but it makes me nervouse.

You can try it out, either in simulation or running on the PI with no hardware connected just to get a glimpse of what it might look like.

I've got some remaining work to debug the Javascript/HTML for the UI but that part is around 90% complete.  I should be able to work through the remaining javascript errors over the next couple of weeks. 

Configuration is done on the server side but some of the data is not getting updated in the correct spot.  In the meantime, you can edit the config.json file that gets created. I'll put an explanation of the values at the end of this document

Getting the behavior to match the real WLED will take some additional time, mostly to figure what is working/not working.  I need to make a version of he DW front end that sends the commands to a real WLED device as well as my sofware so I can compare strips side by side.   While there are relatively few commands being used from the software, the ability to do playlists and presets means that the real device can do pretty much anything in response to an event.  

My plan for handling playlists/presets is to use a (very, very small)  list of pre-defined behaviors that seem appropriate for whatever event has been triggered.   Trying to extract code from WLED would be difficult, but there are other resources like FastLED that are easier to borrow code from.  Anyone is welcome to take the code and implement what they want to see, and I can't see spending a lot of time just to save someone $20 on the real controller.  

I'm a little out of loop with how the DW software is using the WLED product ... there's been so much development done in the last month or so that I can't keep up.  Hopefully now that the DW pro is release things will calm down (at least things that might change what this software needs to do.

So there is work to be done - but nothing particularly difficult.   I don't want to make this a full time job, but I'm willing to commit to a few hours a day for a while.  I'm retired, but I've got several other projects I'm eager to work on.  Any help is welcome.
  
I may not be able to get changing color order working without restarting the service ... a little bit of a pain, but if eveyryone is using strips from the DW BOM, we can probably figure out the more popular strips and I can document it here. 

## The really short introduction

For those with short attention spans who just want to try this software, copy and paste the following into your Raspberry Pi terminal session:
```
git clone  https://github.com/kodell80305/dune-weaver-wled.git
cd dune-weaver-wled
sudo python scripts/startService.py start
```
That's it, you're done as far as the software is concerned.  Wait until the service has started and open a browser with the address of your Raspberry Pi.

If you want to actually see the LEDs you'll need to hook up the data from the LED to GPIO 18.


## If you're still here

This code is designed to run with the amazing [Dune Weaver](https://github.com/tuanchris/dune-weaver) project.  The Dune Weaver project uses standalone WLED devices to control the lighting for the sand table.   The project uses a Raspberry Pi to control a CNC board (mks dlc32 running Fluidnc).   Since the Raspberry Pi Zero 2w is an essential part of the system, I've implemented WLED compatible software to replace the additional ESP32 device.  The commercial WLED devices are probably far less hassle and provide some needed level shifting/wiring simplification as well as many more features, so using these might be your best choice.   I was interested in having one less device that needs to be on my network and simplifying the overall hardware design, so I've implemented this software.

The image below shows this software integrated into the Dune Weaver interface.  It looks almost exactly like the WLED interface (most of the web code is theirs, so it's not surprising).  

![Screenshot 2025-03-13 164145](https://github.com/user-attachments/assets/1a2445e7-8293-41fc-a84b-e79efbb004a6)




## Installation

The web pages are all directly from the WLED project.  I've included WLED as a submodule. Note that I have not tested this software using a virtual environment or using docker.  After cloning the repo, you should be able to run 

```
sudo python scripts/startService.py start
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
sudo python scripts/startService.py start
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
* I'm not sure if the behavior matches WLED in all cases - I need to do some direct comparisons
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

## Docker, virtual environment

I haven't really investigated running in these conditions.   Docker can be somewhat strange when it comes with interfacing with hardware and supporting this is probably never going to be a priority for me.  There should be no reason that virtual environments will be an issue, but this is untested.  The service itself currently runs at root level due to the access of /dev/mem.  

## Testing procedure and installation

Run on standard Ombonad Dune Weaver table.   Fresh install latest 64 bit Bookworm 88following the https://github.com/tuanchris/dune-weaver/wiki/Deploying-backend-code instructions.   Software version <??>
```
git clone  https://github.com/kodell80305/dune-weaver-wled.git
cd dune-weaver-wled
sudo python scripts/startService.py start
```
I created test case for all the current Dune Weaver API calls.   You can run the command
```
python test_led_controller.py
```
All the test cases pass, where pass they all do something.   I need to run these against a real controller and compare the behavior.   There are definately things that don't act quite the same.    The UI still has some issues ... my javascript and html is about 30 years out of date.   

## config.json parameters

Sample configuration is:

{
  "colorOrder": "GRB",
  "duration": 7,
  "seg0s": 0,
  "seg0e": 130,
  "seg0bri": 128,
  "seg0pwr": true,
  "seg1s": 0,
  "seg1e": 10,
  "seg1bri": 128,
  "seg1pwr": true,
  "timer": 0,
  "effect": "",
  "defaultColor": [
    0,
    34,
    255
  ],
  "individAddress": true
}

colorOrder - one of six values RGB, RBG, GRB, GBR, BRG, BGR   I'll flash what is supposed to be a Red/Green/Blue sequence.  If you don't know the color order, it will be some trial and error to figure this one out.   This doesn't get updated unless the service restarts.

seg0s and seg0e are the starting and ending LED's for the strip around the table.  seg0bri and segPwr are mostly for the system to remember the last settings after a restart.
seg1s and seg1e are starting/ending LEDS reservered but an under the table light (e.g. I use the bottom of the Omnobod as a display case).   You'll be able to control on/off/brightness for this, and I may put a time-of-day scheduling in, but it's mostly for future use.  It will respond to the brightness and on/off settings, but no effects or other control.

 Use the actual number of LED's for.  If you have a strip with individually addressable LED's, set "individAddress" to true.   If you can only control blocks of three, set this to false.   I've mostly tested with an individually addressable strip, so many of the effects are completely broken for the non-individually addressable case. 
 
timer doesn't do anything right now.  But it will

So set seg0s, seg0e and colorOrder and ignore the rest for now.  seg0bri, seg0pwr, defaultColor are used to store whatever you did last ... after a reboot/restart, system should restore itself to it's previous state (except for power?)





