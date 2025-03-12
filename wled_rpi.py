#!/usr/bin/env python3
# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.

import time
import argparse
import math
from queue import Queue
import config
import importlib
import json

# Check if rpi_ws281x is available
rpi_ws281x_available = importlib.util.find_spec("rpi_ws281x") is not None

if not rpi_ws281x_available:
    LED_COLOR=0
    print("WARNING - You are running in simulation mode - no hardware will be controlled.  Set simulate=False in config.py to run on hardware")

    class PixelStrip:
        def __init__(self, num, pin, freq_hz=800000, dma=10, invert=False, brightness=255, channel=0, strip_type=None):
            self.num = num
            self.pin = pin
            self.freq_hz = freq_hz
            self.dma = dma
            self.invert = invert
            self.brightness = brightness
            self.channel = channel
            self.strip_type = strip_type
            self.pixels = [(0, 0, 0)] * num

        def begin(self):
            print("Simulated PixelStrip initialized")

        def show(self):
            print("Simulated PixelStrip show")

        def setPixelColor(self, n, color):
            if n < self.num:
                self.pixels[n] = color

        def setBrightness(self, brightness):
            self.brightness = brightness

        def numPixels(self):
            return self.num

    def Color(red, green, blue):
        return (red, green, blue)
else:
    from rpi_ws281x import WS2811_STRIP_RGB, WS2811_STRIP_RBG, WS2811_STRIP_GRB, WS2811_STRIP_GBR, WS2811_STRIP_BRG, WS2811_STRIP_BGR
    from rpi_ws281x import PixelStrip, Color  # Import only the necessary components
    LED_COLOR=WS2811_STRIP_GRB


LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

# empty variable declarations, to stop Python from complaining
Theater = lambda x: x
Rainbow = lambda x: x
TheaterRainbow = lambda x: x
strip = None
current_effect = -1   # -1 = no effect
current_playist = -1
current_func = None
current_color = config.DEFAULT_COLOR


def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)


def Rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256 * iterations):
        for i in range(config.SEGMENT_0_START, strip.numPixels()):
            strip.setPixelColor(i, wheel((i + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)
       
        if checkCancel():
            print("cancelling rainbow")
            return

# Define functions which animate LEDs in various ways.
def colorWipe(strip, color=Color(*current_color), wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(config.SEGMENT_0_START, strip.numPixels()):
 
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)
        #every effect should return if anything is in the queue
        if checkCancel():
            return  


def Theater(strip, color=Color(*current_color), wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(config.SEGMENT_0_START, strip.numPixels(), 3):
                strip.setPixelColor(i + q, color)
            strip.show()
            time.sleep(wait_ms / 1000.0)
            #every effect should return if anything is in the queue
     
            for i in range(config.SEGMENT_0_START, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0)
        if checkCancel():
            return


def Rainbow(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256 * iterations):
        for i in range(config.SEGMENT_0_START, strip.numPixels()):
            strip.setPixelColor(i, wheel(
                (int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)    
        if checkCancel():     
            return

def TheaterRainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""

    for j in range(256):
        for q in range(3):
            for i in range(config.SEGMENT_0_START, strip.numPixels(), 3):
                strip.setPixelColor(i + q, wheel((i + j) % 255))
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(config.SEGMENT_0_START, strip.numPixels(), 3):
                 strip.setPixelColor(i + q, 0)
        if checkCancel():
            return
    

#this is the complete list ... we need to send this back to the web server
from effects_list import effects_list2

effects_list = [
    {
        # Static color effect - should always be first - defines the default
        # state of the LEDs
        "ID": "0",
        "Effect": "Solid",
        "description": "Solid color lighting effect",
        "parameters": {
            "color": "#0000FF",
            "brightness": 128
      }
    },
    {
        'ID': '13',
        "func": Theater,
        "Effect": "Theater",
        "description": "Movie theater light style chaser animation.",
        "parameters": {
            "wait_ms": 20,
        }
    },
    {
        'ID': '14',
        "func": TheaterRainbow,
        "Effect": "Theater Rainbow",
        "description": "A smooth Rainbow effect that cycles through colors",
        "parameters": {
            "wait_ms": 20,
        }
    },
    {
        'ID': '9',
        "func": Rainbow,
        "Effect": "Rainbow",
        "description": "Draw rainbow that uniformly distributes itself across all pixels.",
        "parameters": {
            "speed": 50,
            "intensity": 128
        }
    },
    {
        "func": TheaterRainbow,
        "Effect": "Theater Rainbow",
        "description": "Rainbow movie theater light style chaser animation",
        "parameters" : {
            "wait_ms": 50,      
            "intensity": 128
        }
    }
]

#For now I'm just using the fact that a message is waiting to interrupt the effect ... if it's
#a command like setting the led brightness, then we'll restart the pattern.   Any other command
#will set a different effect to run.  
def checkCancel():
    if not config.myQueue.empty():
        return True
    return False    

#effects_data="[\"Solid\",\"Blink\",\"Breathe\",\"Wipe\"]"
effects_data="[\"Solid\",\"Blink\",\"Breathe\",\"Wipe\",\"Wipe Random\",\"Random Colors\",\"Sweep\",\"Dynamic\",\"Colorloop\",\"Rainbow\",\"Scan\",\"Scan Dual\",\"Fade\",\"Theater\",\"Theater Rainbow\",\"Running\",\"Saw\",\"Twinkle\",\"Dissolve\",\"Dissolve Rnd\",\"Sparkle\",\"Sparkle Dark\",\"Sparkle+\",\"Strobe\",\"Strobe Rainbow\",\"Strobe Mega\",\"Blink Rainbow\",\"Android\",\"Chase\",\"Chase Random\",\"Chase Rainbow\",\"Chase Flash\",\"Chase Flash Rnd\",\"Rainbow Runner\",\"Colorful\",\"Traffic Light\",\"Sweep Random\",\"Chase 2\",\"Aurora\",\"Stream\",\"Scanner\",\"Lighthouse\",\"Fireworks\",\"Rain\",\"Tetrix\",\"Fire Flicker\",\"Gradient\",\"Loading\",\"Rolling Balls\",\"Fairy\",\"Two Dots\",\"Fairytwinkle\",\"Running Dual\",\"RSVD\",\"Chase 3\",\"Tri Wipe\",\"Tri Fade\",\"Lightning\",\"ICU\",\"Multi Comet\",\"Scanner Dual\",\"Stream 2\",\"Oscillate\",\"Pride 2015\",\"Juggle\",\"Palette\",\"Fire 2012\",\"Colorwaves\",\"Bpm\",\"Fill Noise\",\"Noise 1\",\"Noise 2\",\"Noise 3\",\"Noise 4\",\"Colortwinkles\",\"Lake\",\"Meteor\",\"Meteor Smooth\",\"Railway\",\"Ripple\",\"Twinklefox\",\"Twinklecat\",\"Halloween Eyes\",\"Solid Pattern\",\"Solid Pattern Tri\",\"Spots\",\"Spots Fade\",\"Glitter\",\"Candle\",\"Fireworks Starburst\",\"Fireworks 1D\",\"Bouncing Balls\",\"Sinelon\",\"Sinelon Dual\",\"Sinelon Rainbow\",\"Popcorn\",\"Drip\",\"Plasma\",\"Percent\",\"Ripple Rainbow\",\"Heartbeat\",\"Pacifica\",\"Candle Multi\",\"Solid Glitter\",\"Sunrise\",\"Phased\",\"Twinkleup\",\"Noise Pal\",\"Sine\",\"Phased Noise\",\"Flow\",\"Chunchun\",\"Dancing Shadows\",\"Washing Machine\",\"RSVD\",\"Blends\",\"TV Simulator\",\"Dynamic Smooth\",\"Spaceships\",\"Crazy Bees\",\"Ghost Rider\",\"Blobs\",\"Scrolling Text\",\"Drift Rose\",\"Distortion Waves\",\"Soap\",\"Octopus\",\"Waving Cell\",\"Pixels\",\"Pixelwave\",\"Juggles\",\"Matripix\",\"Gravimeter\",\"Plasmoid\",\"Puddles\",\"Midnoise\",\"Noisemeter\",\"Freqwave\",\"Freqmatrix\",\"GEQ\",\"Waterfall\",\"Freqpixels\",\"RSVD\",\"Noisefire\",\"Puddlepeak\",\"Noisemove\",\"Noise2D\",\"Perlin Move\",\"Ripple Peak\",\"Firenoise\",\"Squared Swirl\",\"RSVD\",\"DNA\",\"Matrix\",\"Metaballs\",\"Freqmap\",\"Gravcenter\",\"Gravcentric\",\"Gravfreq\",\"DJ Light\",\"Funky Plank\",\"RSVD\",\"Pulser\",\"Blurz\",\"Drift\",\"Waverly\",\"Sun Radiation\",\"Colored Bursts\",\"Julia\",\"RSVD\",\"RSVD\",\"RSVD\",\"Game Of Life\",\"Tartan\",\"Polar Lights\",\"Swirl\",\"Lissajous\",\"Frizzles\",\"Plasma Ball\",\"Flow Stripe\",\"Hiphotic\",\"Sindots\",\"DNA Spiral\",\"Black Hole\",\"Wavesins\",\"Rocktaves\",\"Akemi\"]"

def get_effects():
    json_effects = []
    return json.loads(effects_data)

def check_effects(effect_id): 
    effect = next((effect for effect in effects_list2 if effect['ID'] == str(effect_id)), None)
    if effect:
        name = effect['Effect']
        print("Running effect", name, "with id", effect_id)
        
        # Find the equivalent effect in effects_list
        
        equivalent_effect = next((e for e in effects_list if e['Effect'] == name), None)
        if equivalent_effect:
            print(f"Equivalent effect found: {equivalent_effect['Effect']}")
            # You can now run the equivalent effect function if needed
            # equivalent_effect['func'](strip)
            return equivalent_effect['func']
        else:
            print(f"No equivalent effect found for {name}")
    else:
        print("Effect with id", effect_id, "not found")
        return None


def run_effects(effect_id):
    effect = next((effect for effect in effects_list if effect.get('ID') == str(effect_id)), None)
    if effect:
        function = effect['func']
        print("Running effect", effect['Effect'], "with id", effect_id, "and function", function)

        try:
            function(strip)
  
        except Exception as e:
            print("Error running effect", effect['Effect'], "with id", effect_id, "and function", function)
            print(e)
    else:
        print("Effect with id", effect_id, "not found")





def update_effect(effect_id):
    global current_effect, current_pl
    print("in update_effect()", effect_id)
    current_pl  =  -1
    current_effect = effect_id

def update_effect2(effect_id):
    global current_effect, current_pl, current_func

    print("in update_effect()", effect_id)

    current_func = check_effects(effect_id) 
    
    current_pl  =  -1
    current_effect = effect_id

    if current_func:
        print("in update_effect() - found effect id ", effect_id)
    else:
        print("in update_effect() - did not find effect id ", effect_id)

    return current_func




def update_playlist(playlist_id):
    global current_effect, current_pl   
    print("in update_playlist()", playlist_id)
    current_pl = playlist_id
    current_effect = -1


def init_rpi():
    global strip

    print("Initializing", config.LED_COUNT)
    strip = PixelStrip(config.LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, 128, LED_CHANNEL, LED_COLOR )
  
    strip.begin()

def init_effects():
    for effect2 in effects_list2:
        name = effect2['Effect']
        equivalent_effect = None
        for e in effects_list:
            if e['Effect'] == name:
                equivalent_effect = e
                break
        if equivalent_effect:
            print(f"Adding ID {effect2['ID']} to effect {name}")
            equivalent_effect['ID'] = effect2['ID']
 

def run_rpi_app():
    global current_effect
#

#Need to patch the index.js file instead 
    init_effects()

    
    for i in range(0, config.SEGMENT_0_START):
        strip.setPixelColor(i, Color(128,128,128))
    
    try:
        print('Waiting for cmd')      
        while True:
            time.sleep(100/1000.0)
            
            if not config.myQueue.empty():
                func, args = config.myQueue.get()
                func(*args)

            if(current_effect > 0):
                run_effects(current_effect)


    except Exception as e: # KeyboardInterrupt:
        breakpoint()
        all_off()

    
def update_bri(bri_arg):
    strip.setBrightness(bri_arg)
    strip.show()
 
        
def all_off():
    global current_effect, current_pl
    current_effect = -1
    current_pl = -1

    for i in range(0, strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
    
    strip.show()

def set_led(led_colors):
    global current_effect, current_pl
    current_effect = -1
    current_pl = -1
    #set leds to the values in the list led_colors

    for i in range(0, config.SEGMENT_0_START):
        strip.setPixelColor(i, Color(128,128,128))
    for i in range(config.SEGMENT_0_START, strip.numPixels()):
        strip.setPixelColor(i, Color(*led_colors[i]))
    strip.show()











