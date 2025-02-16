from queue import Queue
myQueue = Queue()
# Global power state of the LEDs

on=False
bri=128
transition=7       #time transition between effects units of 100 ms
#I'm not sure what som
#{"on":true,"bri":128,"transition":7,"ps":-1,"pl":-1,"ledmap":0,"AudioReactive":{"on":false},"nl":{"on":false,"dur":60,"mode":1,"tbri":0,"rem":-1},
#"udpn":{"send":false,"recv":true,"sgrp":1,"rgrp":1},"lor":0,"mainseg":0,"seg":[{"id":0,"start":0,"stop":30,"len":30,"grp":1,"spc":0,"of":0,
#"on":true,"frz":false,"bri":255,"cct":127,"set":0,"col":[[255,160,0],[0,0,0],[0,0,0]],"fx":0,"sx":128,"ix":128,"pal":0,"c1":128,"c2":128,

LED_COUNT = 16 
#Not scaled by brightness
led_colors = [(bri, bri, bri)] * LED_COUNT  

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




