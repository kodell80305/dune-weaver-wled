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




