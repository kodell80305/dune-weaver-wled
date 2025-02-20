
import time
import argparse
import math
from queue import Queue
import config

current_effect = 0   # 0 = no effect
strip = 0

def init_rpi():
    global strip
    # Create NeoPixel object with appropriate configuration.
    #not rbg, rgb, grb, brg
    print("Initializing ", config.LED_COUNT)




    

def set_led(led_colors):
    global current_effect
    print("in set_led()")
    current_effect = 0

def all_off():
    global current_effect
    current_effect = 0
    print("all_off")

def update_bri(bri_arg):
    print("update_bri")

def theaterChase(strip, color, wait_ms=50, iterations=10):
    time.sleep(1)

def rainbow(strip, wait_ms=20, iterations=1):
    while True:
        print("in rainbow()")
        time.sleep(1)
        #every effect should return if anything is in the queue
        if not config.myQueue.empty():
            return


def rainbowCycle(strip, wait_ms=20, iterations=5):
    time.sleep(1)

def theaterChaseRainbow(strip, wait_ms=50):
    time.sleep(1)

# empty variable declarations, to stop Python from complaining

theaterChase = lambda x: x
rainbow = lambda x: x
rainbowCycle = lambda x: x
theaterChaseRainbow = lambda x: x
strip = None

effects_list = [
    {
        "func": theaterChase,
        "name": "theaterChase",
        "description": "Movie theater light style chaser animation.",
        "parameters": {
            "wait_ms": 20,
        }
    },
    {
        "func": rainbow,
        "name": "rainbow",
        "description": "A smooth rainbow effect that cycles through colors",
        "parameters": {
            "wait_ms": 20,
        }
    },
    {
        "func": rainbowCycle,
        "name": "rainbowCycle",
        "description": "Draw rainbow that uniformly distributes itself across all pixels.",
        "parameters": {
            "speed": 50,
            "intensity": 128
        }
    },
    {
        "func": theaterChaseRainbow,
        "name": "theaterChaseRainbow",
        "description": "Rainbow movie theater light style chaser animation",
        "parameters": {
            "speed": 50,
            "intensity": 128
        }
    }
]


def get_effects():
    json_effects = []
    # enumerate(iter) takes an iterable and adds an index
    # Can also be done as
    # for i in range(len(effects_list)):
    #     effect = effects_list[i]
    # but this is the more common way to do it
    for i, effect in enumerate(effects_list):
        # Make copy of effect before modifying it
        effect = dict(effect)
        # Add id to function
        effect['id'] = i
        del effect['func']  # Can't put functions into a JSON, so remove it
        json_effects.append(effect)

    return json_effects

def run_effects(effect_id):
    print("in run_effects()", effect_id)
    
    effect = effects_list[effect_id] 
    function = effect['func']
    print("Running effect", effect['name'])    

    function(strip)


def update_effect(effect_id):
    global current_effect
    print("in update_effect()", effect_id)
    current_effect = effect_id

def run_rpi_app():
    # Process arguments
    global current_effect
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    print('Initializing im simulation mode', config.LED_COUNT)
    print('Press Ctrl-C to quit.', args)
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')
        
    
    try:
        print('Waiting for cmd')      
        while True:

            time.sleep(100/1000.0)

            if not config.myQueue.empty():
                func, args = config.myQueue.get()
                func(*args)
            
                print("current_effect", current_effect)
                if(current_effect > 0):
                    run_effects(current_effect)


    except Exception as e: # KeyboardInterrupt:

        if args.clear:
            all_off()

        print("Exiting")
        raise e 
