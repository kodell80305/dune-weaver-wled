from flask import Flask, send_from_directory, request, jsonify
import os
import math
import threading
import config
import requests
import json


#state='{"state" : {"on":true,"bri":127,"transition":7,"ps":-1,"pl":-1,"nl":{"on":false,"dur":60,"fade":true,"tbri":0},"udpn":{"send":false,"recv":true},"seg":[{"start":0,"stop":20,"len":20,"col":[[255,160,0,0],[0,0,0,0],[0,0,0,0]],"fx":0,"sx":127,"ix":127,"pal":0,"sel":true,"rev":false,"cln":-1}]},"info":{"ver":"0.8.4","vid":1903252,"leds":{"count":20,"rgbw":true,"pin":[2],"pwr":0,"maxpwr":65000,"maxseg":1},"name":"WLEDLight","udpport":21324,"live":false,"fxcount":80,"palcount":47,"arch":"esp8266","core":"2_4_2","freeheap":13264,"uptime":17985,"opt":127,"brand":"WLED","product":"DIYlight","btype":"src","mac":"60019423b441"},"effects":["Solid","Blink","Breathe","Wipe","WipeRandom","RandomColors","Sweep","Dynamic","Colorloop","Rainbow","Scan","DualScan","Fade","Chase","ChaseRainbow","Running","Saw","Twinkle","Dissolve","DissolveRnd","Sparkle","DarkSparkle","Sparkle+","Strobe","StrobeRainbow","MegaStrobe","BlinkRainbow","Android","Chase","ChaseRandom","ChaseRainbow","ChaseFlash","ChaseFlashRnd","RainbowRunner","Colorful","TrafficLight","SweepRandom","Running2","Red&Blue","Stream","Scanner","Lighthouse","Fireworks","Rain","MerryChristmas","FireFlicker","Gradient","Loading","InOut","InIn","OutOut","OutIn","Circus","Halloween","TriChase","TriWipe","TriFade","Lightning","ICU","MultiComet","DualScanner","Stream2","Oscillate","Pride2015","Juggle","Palette","Fire2012","Colorwaves","BPM","FillNoise","Noise1","Noise2","Noise3","Noise4","Colortwinkle","Lake","Meteor","SmoothMeteor","Railway","Ripple"],"palettes":["Default","RandomCycle","PrimaryColor","BasedonPrimary","SetColors","BasedonSet","Party","Cloud","Lava","Ocean","Forest","Rainbow","RainbowBands","Sunset","Rivendell","Breeze","Red&Blue","Yellowout","Analogous","Splash","Pastel","Sunset2","Beech","Vintage","Departure","Landscape","Beach","Sherbet","Hult","Hult64","Drywet","Jul","Grintage","Rewhi","Tertiary","Fire","Icefire","Cyane","LightPink","Autumn","Magenta","Magred","Yelmag","Yelblu","Orange&Teal","Tiamat","AprilNight"]}'

state = '{"on":true,"bri":128,"transition":7,"ps":-1,"pl":-1,"nl":{"on":false,"dur":60,"fade":true,"tbri":0},"udpn":{"send":false,"recv":true},"seg":[{"start":0,"stop":20,"len":20,"col":[[255,160,0,0],[0,0,0,0],[0,0,0,0]],"fx":0,"sx":127,"ix":127,"pal":0,"sel":true,"rev":false,"cln":-1}]}'
state = json.loads(state)
 

if config.simulate:
    from wled_rpi_sim import set_led, all_off, update_bri, get_effects, update_effect
else:
    from wled_rpi import set_led, all_off, update_bri, get_effects, update_effect

led_colors = [(0, 0, 255)] * config.LED_COUNT  


app = Flask(__name__)

# Route to serve the HTML file
@app.route("/", methods = ['GET', 'POST'])
def index():
    return send_from_directory(".", "index.html")

def set_color(rval, gval, bval):        #Set all leds to same color
    led_colors = [(rval, gval, bval)]*config.LED_COUNT

    config.myQueue.put((set_led, ((led_colors),)))    
   
def handle_on(on_arg):
    global state
    state['on'] = on
    if(on_arg == 't'):        
        config.myQueue.put((set_led, ((led_colors),)))
        
    if(on_arg == 'f'):
        config.myQueue.put((all_off, ()))
        
def handle_bri(bri_arg):
    global state
    state['bri'] = bri_arg
    config.myQueue.put((update_bri, (bri,)))

def handle_effect(effect_arg):
    print("handle_effect")
    print(effect_arg)
    config.myQueue.put((update_effect, (effect_arg,)))

def handle_play(play_arg):
    print("handle_play")
    config.myQueue.put((update_effect, (play_arg,)))
    
@app.route("/json/eff", methods=["GET", "POST"])
def parse_eff():
    try:
    
        # Process the JSON dat here
        response = {
            "message": "JSON received successfully"
        }   
        return jsonify({"effects": get_effects()}), 200
          
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/json/state", methods=["GET","POST"])
def parse_state():
    try:
        print("request", request)
        data = request.get_json()
        
        print("parse state")
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        
        # Process the JSON dat here
        response = {
            "message": "JSON received successfully",
            "received_data": data
        }
        print(json.dumps(data, indent=4))
        
    
        for key, value in data.items() :
            print (key, "value", value)
            match key:
                case 'on':
                    handle_on(value)
                case 'bri':
                    handle_bri(data['bri'])
                case 'seg':       #this sets color, but probably other things I'm not handling
                    for val in value:
                        #not sure what format(s) are possible in json
     
                        led = val['col']
                        print("val is", val, "led is", led ) 
                        if isinstance(led[0], list):
                            set_color(int(led[0][0]),int(led[0][1]), int(led[0][2]))
                        else:
                            set_color(int(led[0]),int(led[1]), int(led[2]))
                case 'effect':
                    print("data", data)
                    handle_effect(value)
                case 'pl':
                    print("play", value)
                    handle_play(value)
                case 'v':
                    print("v", value)        #return the state information
                    response = jsonify(state), 200
                case _:
                    print("no match")
                    
        return jsonify(response), 200
        
    except Exception as e:
        breakpoint()
        return jsonify({"error": str(e)}), 500
    
@app.route("/json", methods=["POST"])
def parse_json():
    return parse_state()

#probably should change the port to somethings else
def run_flask_app():
#run on 127.0.0.0    app.run(debug=False, use_reloader=False)
    app.run(host="0.0.0.0", port=80)
    
def start_flask():
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True  # Allow the main thread to exit even if the Flask thread is running
    flask_thread.start()
    






