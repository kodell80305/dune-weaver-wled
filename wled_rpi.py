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
    LED_COLOR=WS2811_STRIP_BRG

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


#I don't think it really matters what we return from get_effects() anymore ... the javascript is 
#being overridden.

effects_data="[\"Solid\",\"Blink\",\"Breathe\",\"Wipe\"]"

def get_effects():
    json_effects = []
    return json.loads(effects_data)

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
        "description": "Pattern of one lit and two unlit LEDs running",
        "parameters": {                #speed, gap size
            "wait_ms": 20,
        }
    },
    {
        'ID': '14',
        "func": TheaterRainbow,
        "Effect": "Theater Rainbow",
        "description": "Same as Theater but uses colors of the rainbow",
        "parameters": {
            "wait_ms": 20,         #speed, gap size
        }
    },
    {
        'ID': '9',
        "func": Rainbow,
        "Effect": "Rainbow",
        "description": "Displays rainbow colors along the whole strip",
        "parameters": {
            "speed": 50,
            "intensity": 128       #speed, size
        }
    },
    {
        "func": TheaterRainbow,
        "Effect": "Theater Rainbow",
        "description": "Same as Theater but uses colors of the rainbow",
        "parameters" : {  #speed, gap size
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

def run_effects(effect_id):
    effect = next((effect for effect in effects_list if effect.get('ID') == str(effect_id)), None)
    if effect:
        function = effect['func']
        print("Running effect", effect['Effect'], "with id", effect_id)

        try:
            function(strip)
  
        except Exception as e:
            print(e)
    else:
        print("Effect with id", effect_id, "not found")

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

def update_effect(effect_id):
    global current_effect, current_pl
    current_pl  =  -1
    current_effect = effect_id


def update_playlist(playlist_id):
    global current_effect, current_pl   
    print("in update_playlist()", playlist_id)
    current_pl = playlist_id
    current_effect = -1


def init_rpi():
    global strip

    print("Initializing ", config.LED_COUNT)
    strip = PixelStrip(config.LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, 128, LED_CHANNEL, LED_COLOR )
    strip.begin()

 
def run_rpi_app():
    global current_effect
#

    for i in range(0, config.SEGMENT_0_START):
        strip.setPixelColor(i, Color(0,128,0))
    
    strip.show()
    
    try:    
        while True:
            if not config.myQueue.empty():
                func, args = config.myQueue.get()
                func(*args)

            if(current_effect > 0):
                run_effects(current_effect)
            else:
                time.sleep(100/1000.0)


    except Exception as e: 
        all_off()
        











