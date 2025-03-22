import time
import argparse
import math
from queue import Queue
import importlib
import json
import random
from shared_resources import myQueue, app  # Import shared resources


# Check if rpi_ws281x is available
rpi_ws281x_available = importlib.util.find_spec("rpi_ws281x") is not None



if not rpi_ws281x_available:
    LED_COLOR = 0
    app.logger.info("WARNING - You are running in simulation mode - no hardware will be controlled. Set simulate=False in config.py to run on hardware")

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
            app.logger.info("Simulated PixelStrip initialized")

        def show(self):
            app.logger.info("Simulated PixelStrip show")

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
    from rpi_ws281x import PixelStrip, Color  # Import only the necessary components


# empty variable declarations, to stop Python from complaining
Theater = lambda x: x
Rainbow = lambda x: x
TheaterRainbow = lambda x: x
strip = None
current_effect = -1   # -1 = no effect
current_playist = -1
current_func = None
current_color = (0,0,0)

# Define global variables for segment values
seg0s = 0
seg0e = 0
seg1s = 0
seg1e = 0
individAddr = False

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
        for i in range(seg0s, seg0e):  # Use global seg0s
            strip.setPixelColor(i, wheel((i + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)
       
        if checkCancel():
            return

# Define functions which animate LEDs in various ways.
def colorWipe(strip, color=Color(*current_color), wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(seg0s, seg0e):  # Use global seg0s
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
            for i in range(seg0s, seg0e, 3):  # Use global seg0s
                strip.setPixelColor(i + q, color)
            strip.show()
            time.sleep(wait_ms / 1000.0)
            #every effect should return if anything is in the queue
     
            for i in range(seg0s, seg0e, 3):  # Use global seg0s
                strip.setPixelColor(i + q, 0)
        if checkCancel():
            return


def Rainbow(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256 * iterations):
        for i in range(seg0s, seg0e):  # Use global seg0s
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
            for i in range(seg0s, seg0e, 3):  # Use global seg0s
                strip.setPixelColor(i + q, wheel((i + j) % 255))
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(seg0s, seg0e, 3):  # Use global seg0s
                 strip.setPixelColor(i + q, 0)
        if checkCancel():
            return

def Loading(strip, wait_ms=50, iterations=10):
    """
    Moves a sawtooth pattern along the strip.
    """
  

    if  individAddr:
        pattern_length = 10
    else:
        pattern_length = 6  # Length of the sawtooth pattern



    for j in range(iterations):
        for i in range(seg0s, seg0e):
            # Clear the strip
            strip.setPixelColor(i, Color(0, 0, 0))

            # Calculate brightness for each pixel in the sawtooth pattern
            for k in range(pattern_length):
                if i + k < seg0e:
                    brightness = max(0, 255 - (255 * k // pattern_length))

                strip.setPixelColor(i + k, Color(brightness, 0, 0))
                strip.show()
                time.sleep(wait_ms / 1000.0)

            if checkCancel():
                return

def BouncingBalls(strip, gravity=9.8, num_balls=3, overlay=False, wait_ms=50, iterations=100):
    """
    Simulates bouncing balls with gravity.
    """

    positions = [0.0] * num_balls
    velocities = [0.0] * num_balls
    colors = [wheel(int(i * 256 / num_balls)) for i in range(num_balls)]

    for _ in range(iterations):
        for i in range(num_balls):
            velocities[i] += gravity / 1000.0  # Simulate gravity
            positions[i] += velocities[i]

            if positions[i] >= seg0e - 1:  # Bounce off the end
                positions[i] = seg0e - 1
                velocities[i] = -velocities[i] * 0.9  # Lose some energy on bounce

        if not overlay:
            for j in range(seg0s, seg0e):  # Use global seg0s
                strip.setPixelColor(j, Color(0, 0, 0))  # Clear the strip

        for i in range(num_balls):
            strip.setPixelColor(int(positions[i]), colors[i])

        strip.show()
        time.sleep(wait_ms / 1000.0)

        if checkCancel():
            return

def Fairy(strip, speed=50, num_flashers=10, iterations=100):
    """
    Simulates twinkling lights inspired by Christmas lights.
    """
 
    flashers = [random.randint(0, seg0e - 1) for _ in range(num_flashers)]
    colors = [random.randint(0, 255) for _ in range(num_flashers)]  # Store color positions for the wheel

    for _ in range(iterations):
        for i in range(seg0s, seg0e):  # Use global seg0s
            strip.setPixelColor(i, Color(0, 0, 0))  # Clear the strip

        for i, flasher in enumerate(flashers):
            brightness = random.randint(50, 255)  # Random brightness for twinkle
            color = wheel(colors[i])  # Get the color from the wheel
            r = (color >> 16) & 0xFF
            g = (color >> 8) & 0xFF
            b = color & 0xFF
            strip.setPixelColor(flasher, Color(r * brightness // 255, g * brightness // 255, b * brightness // 255))

        strip.show()
        time.sleep(speed / 1000.0)

        if checkCancel():
            return

def Glitter(strip, speed=50, intensity=128, overlay=False, iterations=100):
    """
    Rainbow effect with white sparkles.
    """
    num_pixels = seg0e-seg0s  # Use global seg0s and seg0e
    for _ in range(iterations):
        for i in range(seg0s, seg0e):
            if not overlay:
                strip.setPixelColor(i, Color(0, 0, 0))  # Clear the strip

            # Add rainbow colors
            strip.setPixelColor(i, wheel((i * 256 // num_pixels) & 255))

            # Add white sparkles randomly
            if random.randint(0, 255) < intensity:
                strip.setPixelColor(i, Color(255, 255, 255))

        strip.show()
        time.sleep(speed / 1000.0)

        if checkCancel():
            return

def HalloweenEyes(strip, duration=5000, fade_time=500, overlay=False):
    """
    Simulates a pair of blinking eyes at random intervals along the strip.
    """
    app.logger.debug(f"seg0s: {seg0s} (type: {type(seg0s)}), seg0e: {seg0e} (type: {type(seg0e)})")

    start_time = time.time()
    eye_color = Color(255, 0, 0)  # Red eyes
    bg_color = Color(0, 0, 0)  # Background color

    while (time.time() - start_time) * 1000 < duration:
        # Randomly select a position for the eyes
        eye_position = random.randint(seg0s, seg0e - 2)
        strip.setPixelColor(eye_position, eye_color)
        strip.setPixelColor(eye_position + 1, eye_color)

        strip.show()
        time.sleep(fade_time / 1000.0)

        # Fade out the eyes
        for i in range(fade_time, 0, -50):
            brightness = i / fade_time
            strip.setPixelColor(eye_position, Color(int(255 * brightness), 0, 0))
            strip.setPixelColor(eye_position + 1, Color(int(255 * brightness), 0, 0))
            strip.show()
            time.sleep(50 / 1000.0)

        # Clear the eyes
        strip.setPixelColor(eye_position, bg_color)
        strip.setPixelColor(eye_position + 1, bg_color)
        strip.show()

        if checkCancel():
            return

effects_list = [
    {
        # Static color effect - should always be first - defines the default
        # state of the LEDs
        "ID": "0",
        "Effect": 'Solid',
        "description": "Solid color lighting effect",
        "parameters": {
            "color": "#0000FF",
            "brightness": 128
      }
    },
    {
        'ID': '13',
        "func": Theater,
        "Effect": 'Theater',
        "description": "Pattern of one lit and two unlit LEDs running",
        "parameters": {                #speed, gap size
            "wait_ms": 20,
        }
    },
    {
        'ID': '47',
        "func": Loading,
        "Effect": 'Loading',
        "description": "Moves a sawtooth pattern along the strip",
        "parameters": {                #speed, gap size
            "wait_ms": 20,
            "iterations" : 10
        
        }
    },
    {
        'ID': '14',
        "func": BouncingBalls,
        "Effect": 'Bouncing Balls',
        "description": "Bouncing ball effect",
        "parameters": {
            "wait_ms": 20,         #speed, gap size
            'gravity': 9.8,
            'num_balls': 3,
            'overlay': False,
            'wait_ms': 50,
            'iterations': 100
        }
       },
    {
        'ID': '9',
        "func": Rainbow,
        "Effect": 'Rainbow',
        "description": "Displays rainbow colors along the whole strip",
        "parameters": {
            "speed": 50,
            "intensity": 128       #speed, size
        }
    },
    {
        'ID': '14',
        "func": TheaterRainbow,
        "Effect": 'Theater Rainbow',
        "description": "Same as Theater but uses colors of the rainbow",
        "parameters" : {  #speed, gap size
            "wait_ms": 50,      
            "intensity": 128
        }
    },

    {
        'ID': '49',
        'func': Fairy,
        'Effect': 'Fairy',
        'description': 'Simulates twinkling lights inspired by Christmas lights',
        'parameters': {
            'speed': 50,
            'num_flashers': 10,
            'iterations': 100
        }
    },
    {
        'ID': '87',
        'func': Glitter,
        'Effect': 'Glitter',
        'description': 'Rainbow with white sparkles',
        'parameters': {
            'speed': 50,
            'intensity': 128,
            'overlay': False,
            'iterations': 100
        }
    },
    {
        'ID': '82',
        'func': HalloweenEyes,
        'Effect': 'Halloween Eyes',
        'description': 'One pair of blinking eyes at random intervals along the strip',
        'parameters': {
            'duration': 5000,
            'fade_time': 500,
            'overlay': False
        }
    }
]


def get_effects():
    """
    Returns the list of available effects extracted from effects_list.
    """
    return [effect["Effect"] for effect in effects_list]

def get_effects_js():
    """
    Generates a JavaScript string for the effects list in the format:
    var effects = [
        ['0', "Solid"],
        ['9', "Rainbow"],
        ['14', "Theater Rainbow"],
    ];
    """
   
  
    effects_js = "var effects = [\n"
    for effect in effects_list:
        effects_js += f"    [\'{effect['ID']}\', \"{effect['Effect']}\"],\n"
    effects_js += "];"

    return effects_js



#For now I'm just using the fact that a message is waiting to interrupt the effect ... if it's
#a command like setting the led brightness, then we'll restart the pattern.   Any other command
#will set a different effect to run.  
def checkCancel():
    if not myQueue.empty():
        return True
    return False    

def run_effects(effect_id):


    effect = next((effect for effect in effects_list if effect.get('ID') == str(effect_id)), None)
    if effect:
        function = effect['func']

        app.logger.debug(f"Running effect {effect['Effect']} with id {effect_id}")

        try:
            function(strip)
  
        except Exception as e:
            app.logger.info(e)
    else:
        app.logger.info(f"Effect with id {effect_id} not found")

def update_bri(bri_arg):
    strip.setBrightness(bri_arg)
    strip.show()
 
        
def all_off():
    global current_effect, current_pl
    current_effect = -1
    current_pl = -1


    for i in range(0, strip.numPixels()):  # Use global seg0e
        strip.setPixelColor(i, Color(0, 0, 0))
    
    strip.show()

def set_led(led_color):
    global current_effect, current_pl
    current_effect = -1
    current_pl = -1

    # Validate led_color
    if not isinstance(led_color, (list, tuple)) or len(led_color) != 3:
        raise ValueError(f"Invalid led_color: {led_color}. Expected a tuple or list of 3 integers.")

    for i in range(seg0s, seg0e):  # Use global seg0s and seg0e
        strip.setPixelColor(i, Color(*led_color))
    strip.show()

def update_effect(effect_id):
    global current_effect, current_pl
    current_pl  =  -1
    current_effect = effect_id


def update_playlist(playlist_id):
    global current_effect, current_pl   
    app.logger.debug(f"in update_playlist() {playlist_id}")
    current_pl = playlist_id
    current_effect = -1



LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53


from rpi_ws281x import WS2811_STRIP_RGB, WS2811_STRIP_RBG, WS2811_STRIP_GRB, WS2811_STRIP_GBR, WS2811_STRIP_BRG, WS2811_STRIP_BGR

# Map colorOrder values to corresponding WS2811_STRIP constants
color_order_map = {
    'RGB': WS2811_STRIP_RGB,
    'RBG': WS2811_STRIP_RBG,
    'GRB': WS2811_STRIP_GRB,
    'GBR': WS2811_STRIP_GBR,
    'BRG': WS2811_STRIP_BRG,
    'BGR': WS2811_STRIP_BGR
     }

# Add a global variable to store the current LED_COLOR
current_led_color = None

def init_rpi(config_data):
    global strip, seg0s, seg0e, seg1s, seg1e
    # Save segment values in global variables
    # Save segment values in global variables0e'])  # Ensure seg0e is an integer
    seg0s = int(config_data.get('seg0s', 0))       # Default to 0 if not provided
    seg0e = int(config_data.get('seg0e', 0))
    seg1s = int(config_data.get('seg1s', 0))  #
    seg1e = int(config_data.get('seg1e', 0))  # Default to 0 if not provided
    current_color = config_data.get('defaultColor', (0, 0, 255))  # Default to blue if not provided    individAddr = config_data['individAddress']

    individAddr = config_data['individAddress']   

    if not individAddr:
        seg0s //= 3
        seg1s //= 3
        seg0e //= 3
        seg1e //= 3    # Calculate LED count as the maximum of seg0e and seg1e
    # Calculate LED count as the maximum of seg0e and seg1e
    led_count = int(max(seg0e, seg1e))  # Explicitly cast to integer    # Set LED_COLOR based on colorOrder in config_data
  # Default to 'RGB' if not specified
    # Set LED_COLOR based on colorOrder in config_dataIP_RGB if invalid
    color_order = config_data.get('colorOrder', 'RGB')  # Default to 'RGB' if not specified
    LED_COLOR = color_order_map.get(color_order, WS2811_STRIP_RGB)  # Default to WS2811_STRIP_RGB if invalid    print(f"{type(led_count)} {type(LED_PIN)} {type(LED_FREQ_HZ)} {type(LED_DMA)} {type(LED_INVERT)} {type(LED_CHANNEL)} {type(LED_COLOR)}")

    print(f"{type(led_count)} {type(LED_PIN)} {type(LED_FREQ_HZ)} {type(LED_DMA)} {type(LED_INVERT)} {type(LED_CHANNEL)} {type(LED_COLOR)}")
    print(f"Initializing with LED count: {led_count} and color order: {color_order}")

    try:
        strip = PixelStrip(led_count, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, 128, LED_CHANNEL, LED_COLOR)
        strip.begin()
    except Exception as e:
        #doesn't exist yet
        #app.logger.info(e)
        print(e)


def display_color():
    time.sleep(5)    
    

    app.logger.info(f"red ..") 
    for i in range(0, strip.numPixels()):
        strip.setPixelColor(i, Color(255, 0, 0))
    strip.show()
    time.sleep(1)    
    app.logger.info(f"green ..")

    for i in range(0, strip.numPixels()):
        strip.setPixelColor(i, Color(0, 255, 0))
    strip.show()
    time.sleep(1)    
    
    for i in range(0, strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 255))
    strip.show()
    time.sleep(1)   

    app.logger.info(f"blue")
    for i in range(0, strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()
    time.sleep(1)

  
def update_segments(new_config_data):
    """
    Updates segment values and reinitializes the LED strip if necessary.
    """
    global seg0s, seg0e, seg1s, seg1e, strip, individAddr, current_led_color
    from wled_web_server import app as app    # Check if any segment values have changed

    # Check if any segment values have changedw_config_data['seg0s'] or
    seg_changed = (
        seg0s != int(new_config_data.get('seg0s', 0)),
        seg0e != int(new_config_data.get('seg0e', 0)),
        seg1s != int(new_config_data.get('seg1s', 0)),
        seg1e != int(new_config_data.get('seg1e', 0))
    )    

    seg0s = int(new_config_data.get('seg0s', 0))
    seg0e = int(new_config_data.get('seg0e', 0))
    seg1s = int(new_config_data.get('seg1s', 0))
    seg1e = int(new_config_data.get('seg1e', 0))

    individAddr = new_config_data['individAddress']    # Adjust segments if not individually addressable

    # Adjust segments if not individually addressable
    if not individAddr:
        seg0s //= 3
        seg1s //= 3
        seg0e //= 3
        seg1e //= 3    # Calculate new LED count and LED color

    # Calculate new LED count and LED color'colorOrder', 'RGB')
    new_led_count = int(max(seg0e, seg1e))
    new_color_order = new_config_data.get('colorOrder', 'RGB')
    new_LED_COLOR = color_order_map.get(new_color_order, WS2811_STRIP_RGB)    # Reinitialize the LED strip only if led_count or LED_COLOR has changed

    # Reinitialize the LED strip only if led_count or LED_COLOR has changed
    if strip is None or new_led_count != strip.numPixels() or new_LED_COLOR != current_led_color:
        
    
        try:
            strip = PixelStrip(new_led_count, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, 128, LED_CHANNEL, new_LED_COLOR)
            strip.begin()
            current_led_color = new_LED_COLOR  # Update the stored LED_COLOR
            app.logger.info("LED strip reinitialized due to configuration changes.") 
            display_color()
        
        except Exception as e:
            app.logger.error("Failed to reinitialize LED strip.")
            print(e)

def run_rpi_app():
    global current_effect
    try:    
        while True:
            if not myQueue.empty():  # Corrected the syntax here
                func, args = myQueue.get()
                app.logger.debug(f"Running function: {func} with args: {args}")

                # Validate func and args
                if not callable(func):
                    app.logger.error(f"Invalid function in queue: {func}")
                    continue
                if not isinstance(args, tuple):
                    app.logger.error(f"Invalid arguments in queue: {args}")
                    continue

                func(*args)

            if current_effect > 0:
                run_effects(current_effect)
            else:
                time.sleep(100 / 1000.0)

    except Exception as e: 
        app.logger.info(f"Error in run_rpi_app() {e} {func} {type(func)} {args} {type(args)}")
        app.logger.info(e)
        all_off()



def cleanup_leds():
    """
    Cleans up the LED strip by turning off all LEDs and releasing resources.
    """
    global strip    
    
    if strip:
        # Turn off all LEDs
        for i in range(0, strip.numPixels()):
            strip.setPixelColor(i, Color(0, 0, 0))  # Fixed syntax error
        strip.show()
        # Release the strip object
        strip = None












