#!/usr/bin/env python3
# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.

import time
from rpi_ws281x import *
import argparse
#from flask import Flask, send_from_directory, request, jsonify
import os
import math
import threading
from queue import Queue
import config


from wled_web_server import start_flask

# LED strip configuration:
#LED_COUNT = 16 #LED_COUNT = 16 in config.py
LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)

LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

last_bri = config.bri



def update_bri():
    global last_bri
    #We need to update the leds to an abs
    # Restore LEDs to their previous colors
    print("set brightness to ", config.bri, last_bri)
    
    strip.setBrightness(config.bri)
    strip.show()
 
        
def all_off():
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()

def restore():
    # Restore LEDs to their previous colors
        # Restore LEDs to their previous colors
    print("restore called")
    for i in range(0, config.LED_COUNT):
        led = config.led_colors[i]
        print("Set led ", i, type(led), led[0], led[1], led[2])
        strip.setPixelColor(i, Color(led[0], led[1], led[2]))
    strip.show()
    

# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)


def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, color)
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0)


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


def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)


def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel(
                (int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)


def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, wheel((i + j) % 255))
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0)

#SK6812_STRIP_RGBW = _rpi_ws281x.SK6812_STRIP_RGBW
#SK6812_STRIP_RBGW = _rpi_ws281x.SK6812_STRIP_RBGW
#SK6812_STRIP_GRBW = _rpi_ws281x.SK6812_STRIP_GRBW
#SK6812_STRIP_GBRW = _rpi_ws281x.SK6812_STRIP_GBRW
#SK6812_STRIP_BRGW = _rpi_ws281x.SK6812_STRIP_BRGW
#SK6812_STRIP_BGRW = _rpi_ws281x.SK6812_STRIP_BGRW
#SK6812_SHIFT_WMASK = _rpi_ws281x.SK6812_SHIFT_WMASK
#WS2811_STRIP_RGB = _rpi_ws281x.WS2811_STRIP_RGB
#WS2811_STRIP_RBG = _rpi_ws281x.WS2811_STRIP_RBG
#WS2811_STRIP_GRB = _rpi_ws281x.WS2811_STRIP_GRB
#WS2811_STRIP_GBR = _rpi_ws281x.WS2811_STRIP_GBR
#WS2811_STRIP_BRG = _rpi_ws281x.WS2811_STRIP_BRG
#WS2811_STRIP_BGR = _rpi_ws281x.WS2811_STRIP_BGR
#WS2812_STRIP = _rpi_ws281x.WS2812_STRIP
#SK6812_STRIP = _rpi_ws281x.SK6812_STRIP
#SK6812W_STRIP = _rpi_ws281x.SK6812W_STRIP

#default is WS2811_STRIP_GRB
                #RB
                

# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    # Create NeoPixel object with appropriate configuration.
    #not rbg, rgb, grb, brg
    strip = PixelStrip(config.LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, config.bri, LED_CHANNEL, WS2811_STRIP_GBR )
    # Intialize the library (must be called once before other functions).
    strip.begin()

    print('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')
        
    start_flask()
    
    try:
        print('Waiting for cmd')      
        while True:
      
            if not config.myQueue.empty():
                cmd = config.myQueue.get()
                print('Received cmd ', cmd)
                match cmd:
                    case "all_off":
                        all_off()                 
                    case "restore":
                        restore()
                    case "update_state":
                        update_state()
                    case "update_bri":
                        update_bri()
                        
                    case _:
                        print("Invalid command")
                

                
#           print('Color wipe animations.')
#            colorWipe(strip, Color(255, 0, 0))  # Red wipe
#            colorWipe(strip, Color(0, 255, 0))  # Green wipe
#            colorWipe(strip, Color(0, 0, 255))  # Blue wipe
#            print('Theater chase animations.')
#            theaterChase(strip, Color(127, 127, 127))  # White theater chase
#            theaterChase(strip, Color(127, 0, 0))  # Red theater chase
#            theaterChase(strip, Color(0, 0, 127))  # Blue theater chase
#            print('Rainbow animations.')
#            rainbow(strip)
#            rainbowCycle(strip)
#            theaterChaseRainbow(strip)

    except KeyboardInterrupt:
        if args.clear:
            colorWipe(strip, Color(0, 0, 0), 10)
