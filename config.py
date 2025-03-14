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

#Run in simulation mode - for testing only
simulate = True
#You'll need to configure the number of pixels and the type of strip you have.   Also if you want to have the first SEGMENT_0_START pixels be used for undertable
#lighting, set SEGMENT_0_START.  Otherwise make it 0.  These pixels will always be white, but will respond to brightness/power on or off
LED_COUNT = 200
SEGMENT_0_START = 11


  
from queue import Queue
myQueue = Queue()
DEFAULT_COLOR=(0, 0, 255)