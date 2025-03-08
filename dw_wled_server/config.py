from queue import Queue
myQueue = Queue()

#Run in simulation mode
simulate = False

# Global power state of the LEDs




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
#WS2811_STRIP_BGR = _rpi_ws281x.WS2812_STRIP
#SK6812_STRIP = _rpi_ws281x.SK6812_STRIP
#SK6812W_STRIP = _rpi_ws281x.SK6812W_STRIP

if simulate:
    LED_COLOR=0
else:
    from rpi_ws281x import WS2811_STRIP_RGB, WS2811_STRIP_RBG, WS2811_STRIP_GRB, WS2811_STRIP_GBR, WS2811_STRIP_BRG, WS2811_STRIP_BGR
    LED_COLOR=WS2811_STRIP_BRG


#You'll need to configure the number of pixels and the type of strip you have
LED_COUNT = 30
#I use the first few leds for lighting under the table ... these are fixed to white
SEGMENT_0_START = 3

