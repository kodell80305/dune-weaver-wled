from flask import Flask, send_from_directory, request, jsonify, render_template
import logging

import os
import math
import threading
import config
import requests
import json


# Default data to pass to the template
settings_data = {
    "totalLeds": "41",  # Default total LEDs
    "colorOrder": "GRB",  # Default selected color order
    "brightness": "41",  # Default brightness
    "duration": "18"  # Default duration in minutes
}

state = '{"state" : {"on":true,"bri":128,"transition":7,"ps":-1,"pl":-1,"nl":{"on":false,"dur":60,"fade":true,"tbri":0},"udpn":{"send":false,"recv":true},"seg":[{"start":0,"stop":20,"len":20,"col":[[255,160,0,0],[0,0,0,0],[0,0,0,0]],"fx":0,"sx":127,"ix":127,"pal":0,"sel":true,"rev":false,"cln":-1}]}}'

app = Flask(__name__, static_folder='static')

    
config_data = {
    "LED_COUNT": 87,
    "SEGMENT_0_START": 11,
    "LED_STRIP" : "WS2811_STRIP_RGB",
    "LED_COLOR": [0, 0, 255]
}

# Define the path to the config file
config_file_path = "config.json"

def write_json(path, json_data):
    with open(path, 'w') as file_out:
        json.dump(json_data, file_out)


def read_json(path):
    with open(path) as file_in:
        return json.load(file_in)


# Check if the config file exists, if not create it with default config data
if not os.path.exists(config_file_path):
    write_json(config_file_path, config_data)
else:
    config_data = read_json(config_file_path)




pallets_data="[\n\"Default\",\"* Random Cycle\",\"* Color 1\",\"* Colors 1&2\",\"* Color Gradient\",\"* Colors Only\",\"Party\",\"Cloud\",\"Lava\",\"Ocean\",\n\"Forest\",\"Rainbow\",\"Rainbow Bands\",\"Sunset\",\"Rivendell\",\"Breeze\",\"Red & Blue\",\"Yellowout\",\"Analogous\",\"Splash\",\n\"Pastel\",\"Sunset 2\",\"Beach\",\"Vintage\",\"Departure\",\"Landscape\",\"Beech\",\"Sherbet\",\"Hult\",\"Hult 64\",\n\"Drywet\",\"Jul\",\"Grintage\",\"Rewhi\",\"Tertiary\",\"Fire\",\"Icefire\",\"Cyane\",\"Light Pink\",\"Autumn\",\n\"Magenta\",\"Magred\",\"Yelmag\",\"Yelblu\",\"Orange & Teal\",\"Tiamat\",\"April Night\",\"Orangery\",\"C9\",\"Sakura\",\n\"Aurora\",\"Atlantica\",\"C9 2\",\"C9 New\",\"Temperature\",\"Aurora 2\",\"Retro Clown\",\"Candy\",\"Toxy Reaf\",\"Fairy Reaf\",\n\"Semi Blue\",\"Pink Candy\",\"Red Reaf\",\"Aqua Flash\",\"Yelblu Hot\",\"Lite Light\",\"Red Flash\",\"Blink Red\",\"Red Shift\",\"Red Tide\",\n\"Candy2\"\n]"
fxdata_data="[\"\",\"!,Duty cycle;!,!;!;01\",\"!;!,!;!;01\",\"!,!;!,!;!\",\"!;;!\",\"!,Fade time;;!;01\",\"!,!;!,!;!\",\"!,!,,,,Smooth;;!\",\"!,Saturation;;!;01\",\"!,Size;;!\",\"!,# of dots,,,,,Overlay;!,!,!;!\",\"!,# of dots,,,,,Overlay;!,!,!;!\",\"!;!,!;!;01\",\"!,Gap size;!,!;!\",\"!,Gap size;,!;!\",\"!,Wave width;!,!;!\",\"!,Width;!,!;!\",\"!,!;!,!;!;;m12=0\",\"Repeat speed,Dissolve speed,,,,Random;!,!;!\",\"Repeat speed,Dissolve speed;,!;!\",\"!,,,,,,Overlay;!,!;!;;m12=0\",\"!,!,,,,,Overlay;Bg,Fx;!;;m12=0\",\"!,!,,,,,Overlay;Bg,Fx;!;;m12=0\",\"!;!,!;!;01\",\"!;,!;!;01\",\"!,!;!,!;!;01\",\"Frequency,Blink duration;!,!;!;01\",\"!,Width;!,!;!;;m12=1\",\"!,Width;!,!,!;!\",\"!,Width;!,,!;!\",\"!,Width;!,!;!\",\"!;Bg,Fx;!\",\"!;!,!;!\",\"!,Size;Bg;!\",\"!,Saturation;1,2,3;!\",\"!,US style;,!;!\",\"!;;!\",\"!,Width;!,!;!\",\"!,!;1,2,3;!;;sx=24,pal=50\",\"!,Zone size;;!\",\"!,Fade rate;!,!;!;;m12=0\",\"!,Fade rate;!,!;!\",\",Frequency;!,!;!;12;ix=192,pal=11\",\"!,Spawning rate;!,!;!;12;ix=128,pal=0\",\"!,Width,,,,One color;!,!;!;;sx=0,ix=0,pal=11,m12=1\",\"!,!;!;!;01\",\"!,Spread;!,!;!;;ix=16\",\"!,Fade;!,!;!;;ix=16\",\"!,# of balls,,,,Collisions,Overlay,Trails;!,!,!;!;1;m12=1\",\"!,# of flashers;!,!;!\",\"!,Dot size,,,,,Overlay;1,2,Bg;!\",\"!,!;!,!;!;;m12=0\",\"!,Wave width;L,!,R;!\",\"\",\"!,Size;1,2,3;!\",\"!;1,2,3;!\",\"!;1,2,3;!\",\"!,!,,,,,Overlay;!,!;!\",\"!,!,,,,,Overlay;!,!;!\",\"\",\"!,Fade rate;!,!,!;!;;m12=0\",\"!;;\",\"\",\"!;;\",\"!,Trail;;!;;sx=64,ix=128\",\"Cycle speed;;!;;c3=0,o2=0\",\"Cooling,Spark rate,,,Boost;;!;1;sx=64,ix=160,m12=1\",\"!,Hue;!;!\",\"!;!;!;;sx=64\",\"!;!;!\",\"!;!;!\",\"!;!;!\",\"!;!;!\",\"!;!;!\",\"Fade speed,Spawn speed;;!;;m12=0\",\"!;Fx;!\",\"!,Trail,,,,Gradient;;!;1\",\"!,Trail,,,,Gradient;;!;1\",\"!,Smoothness;1,2;!\",\"!,Wave #,,,,,Overlay;,!;!;12\",\"!,Twinkle rate,,,,Cool;!,!;!\",\"!,Twinkle rate,,,,Cool;!,!;!\",\"Duration,Eye fade time,,,,,Overlay;!,!;!;12\",\"Fg size,Bg size;Fg,!;!;;pal=0\",\",Size;1,2,3;;;pal=0\",\"Spread,Width,,,,,Overlay;!,!;!\",\"Spread,Width,,,,,Overlay;!,!;!\",\"!,!,,,,,Overlay;1,2,Glitter color;!;;pal=0,m12=0\",\"!,!;!,!;!;01;sx=96,ix=224,pal=0\",\"Chance,Fragments,,,,,Overlay;,!;!;;pal=11,m12=0\",\"Gravity,Firing side;!,!;!;12;pal=11,ix=128\",\"Gravity,# of balls,,,,,Overlay;!,!,!;!;1;m12=1\",\"!,Trail;!,!,!;!\",\"!,Trail;!,!,!;!\",\"!,Trail;,,!;!\",\"!,!,,,,,Overlay;!,!,!;!;;m12=1\",\"Gravity,# of drips,,,,,Overlay;!,!;!;;m12=1\",\"Phase,!;!;!\",\",% of fill,,,,One color;!,!;!\",\"!,Wave #;;!;12\",\"!,!;!,!;!;01;m12=1\",\"!,Angle;;!;;pal=51\",\"!,!;!,!;!;;sx=96,ix=224,pal=0\",\",!;Bg,,Glitter color;;;m12=0\",\"Time [min],Width;;!;;sx=60\",\"!,!;!,!;!\",\"!,Intensity;!,!;!;;m12=0\",\"!,Scale;;!\",\"\",\"!,!;!,!;!\",\"!,Zones;;!;;m12=1\",\"!,Gap size;!,!;!\",\"!,# of shadows;!;!\",\"!,!;;!\",\"\",\"Shift speed,Blend speed;;!\",\"!,!;;\",\"!,!;;!\",\"!,Blur;;!;2\",\"!,Blur;;;2\",\"Fade rate,Blur;;!;2\",\"!,# blobs,Blur,Trail;!;!;2;c1=8\",\"!,Y Offset,Trail,Font size,Rotate,Gradient,Overlay,Reverse;!,!,Gradient;!;2;ix=128,c1=0,rev=0,mi=0,rY=0,mY=0\",\"Fade,Blur;;;2\",\"!,Scale;;;2\",\"!,Smoothness;;!;2\",\"!,,Offset X,Offset Y,Legs;;!;2;\",\"!,,Amplitude 1,Amplitude 2,Amplitude 3;;!;2\",\"Fade rate,# of pixels;!,!;!;1v;m12=0,si=0\",\"!,Sensitivity;!,!;!;1v;ix=64,m12=2,si=0\",\"!,# of balls;!,!;!;1v;m12=0,si=0\",\"!,Brightness;!,!;!;1v;ix=64,m12=2,si=1\",\"Rate of fall,Sensitivity;!,!;!;1v;ix=128,m12=2,si=0\",\"Phase,# of pixels;!,!;!;1v;sx=128,ix=128,m12=0,si=0\",\"Fade rate,Puddle size;!,!;!;1v;m12=0,si=0\",\"Fade rate,Max. length;!,!;!;1v;ix=128,m12=1,si=0\",\"Fade rate,Width;!,!;!;1v;ix=128,m12=2,si=0\",\"Speed,Sound effect,Low bin,High bin,Pre-amp;;;1f;m12=2,si=0\",\"Speed,Sound effect,Low bin,High bin,Sensitivity;;;1f;m12=3,si=0\",\"Fade speed,Ripple decay,# of bands,,,Color bars;!,,Peaks;!;2f;c1=255,c2=64,pal=11,si=0\",\"!,Adjust color,Select bin,Volume (min);!,!;!;1f;c2=0,m12=2,si=0\",\"Fade rate,Starting color and # of pixels;!,!,;!;1f;m12=0,si=0\",\"\",\"!,!;;;1v;m12=2,si=0\",\"Fade rate,Puddle size,Select bin,Volume (min);!,!;!;1v;c2=0,m12=0,si=0\",\"Speed of perlin movement,Fade rate;!,!;!;1f;m12=0,si=0\",\"!,Scale;;!;2\",\"!,# of pixels,Fade rate;!,!;!\",\"Fade rate,Max # of ripples,Select bin,Volume (min);!,!;!;1v;c2=0,m12=0,si=0\",\"X scale,Y scale,,,,Palette;;!;2;pal=66\",\",,,,Blur;;!;2\",\"\",\"Scroll speed,Blur;;!;2\",\"!,Spawning rate,Trail,,,Custom color;Spawn,Trail;;2\",\"!;;!;2\",\"Fade rate,Starting color;!,!;!;1f;m12=0,si=0\",\"Rate of fall,Sensitivity;!,!;!;1v;ix=128,m12=2,si=0\",\"Rate of fall,Sensitivity;!,!;!;1v;ix=128,m12=3,si=0\",\"Rate of fall,Sensitivity;!,!;!;1f;ix=128,m12=0,si=0\",\"Speed;;;1f;m12=2,si=0\",\"Scroll speed,,# of bands;;;2f;si=0\",\"\",\"!,Blur;;!;2\",\"Fade rate,Blur;!,Color mix;!;1f;m12=0,si=0\",\"Rotation speed,Blur amount;;!;2\",\"Amplification,Sensitivity;;!;2v;ix=64,si=0\",\"Variance,Brightness;;;2\",\"Speed,# of lines,,,Blur,Gradient,,Dots;;!;2;c3=16\",\",Max iterations per pixel,X center,Y center,Area size;!;!;2;ix=24,c1=128,c2=128,c3=16\",\"\",\"\",\"\",\"!;!,!;!;2\",\"X scale,Y scale,,,Sharpness;;!;2\",\"!,Scale;;;2\",\"!,Sensitivity,Blur;,Bg Swirl;!;2v;ix=64,si=0\",\"X frequency,Fade rate,,,Speed;!;!;2;;c3=15\",\"X frequency,Y frequency,Blur;;!;2\",\"Speed,,Fade,Blur;;!;2\",\"Hue speed,Effect speed;;\",\"X scale,Y scale,,,Speed;!;!;2\",\"!,Dot distance,Fade rate,Blur;;!;2\",\"Scroll speed,Y frequency;;!;2\",\"Fade rate,Outer Y freq.,Outer X freq.,Inner X freq.,Inner Y freq.,Solid;!;!;2;pal=11\",\"!,Brightness variation,Starting color,Range of colors,Color variation;!;!\",\";!,!;!;1f;m12=1,si=0\",\"Color speed,Dance;Head palette,Arms & Legs,Eyes & Mouth;Face palette;2f;si=0\"]"
palx_data="{\"m\":8,\"p\":{\"0\":[[0,85,0,171],[16,132,0,124],[32,181,0,75],[48,229,0,27],[64,232,23,0],[80,184,71,0],[96,171,119,0],[112,171,171,0],[128,171,85,0],[144,221,34,0],[160,242,0,14],[176,194,0,62],[192,143,0,113],[208,95,0,161],[224,47,0,208],[240,0,7,249]],\"1\":[\"r\",\"r\",\"r\",\"r\"],\"2\":[\"c1\"],\"3\":[\"c1\",\"c1\",\"c2\",\"c2\"],\"4\":[\"c3\",\"c2\",\"c1\"],\"5\":[\"c1\",\"c1\",\"c1\",\"c1\",\"c1\",\"c2\",\"c2\",\"c2\",\"c2\",\"c2\",\"c3\",\"c3\",\"c3\",\"c3\",\"c3\",\"c1\"],\"6\":[[0,85,0,171],[16,132,0,124],[32,181,0,75],[48,229,0,27],[64,232,23,0],[80,184,71,0],[96,171,119,0],[112,171,171,0],[128,171,85,0],[144,221,34,0],[160,242,0,14],[176,194,0,62],[192,143,0,113],[208,95,0,161],[224,47,0,208],[240,0,7,249]],\"7\":[[0,0,0,255],[16,0,0,139],[32,0,0,139],[48,0,0,139],[64,0,0,139],[80,0,0,139],[96,0,0,139],[112,0,0,139],[128,0,0,255],[144,0,0,139],[160,135,206,235],[176,135,206,235],[192,173,216,230],[208,255,255,255],[224,173,216,230],[240,135,206,235]]}}"

si_data="{\"state\":{\"on\":true,\"bri\":100,\"transition\":0,\"ps\":1,\"pl\":-1,\"nl\":{\"on\":false,\"dur\":60,\"mode\":1,\"tbri\":0,\"rem\":-1},\"udpn\":{\"send\":false,\"recv\":true,\"sgrp\":1,\"rgrp\":1},\"lor\":0,\"mainseg\":0,\"seg\":[{\"id\":0,\"start\":0,\"stop\":85,\"len\":85,\"grp\":1,\"spc\":0,\"of\":0,\"on\":true,\"frz\":false,\"bri\":255,\"cct\":127,\"set\":0,\"col\":[[0,38,255],[0,0,0],[0,0,0]],\"fx\":0,\"sx\":150,\"ix\":150,\"pal\":0,\"c1\":128,\"c2\":128,\"c3\":16,\"sel\":true,\"rev\":false,\"mi\":false,\"o1\":false,\"o2\":false,\"o3\":false,\"si\":0,\"m12\":0},{\"id\":1,\"start\":0,\"stop\":3,\"len\":3,\"grp\":1,\"spc\":0,\"of\":0,\"on\":true,\"frz\":false,\"bri\":255,\"cct\":127,\"set\":0,\"col\":[[255,245,245],[0,0,0],[0,0,0]],\"fx\":0,\"sx\":128,\"ix\":128,\"pal\":0,\"c1\":128,\"c2\":128,\"c3\":16,\"sel\":true,\"rev\":false,\"mi\":false,\"o1\":false,\"o2\":false,\"o3\":false,\"si\":0,\"m12\":0}]},\"info\":{\"ver\":\"0.14.4\",\"vid\":2405180,\"leds\":{\"count\":85,\"pwr\":537,\"fps\":5,\"maxpwr\":850,\"maxseg\":32,\"seglc\":[1,1],\"lc\":1,\"rgbw\":false,\"wv\":0,\"cct\":0},\"str\":false,\"name\":\"WLED\",\"udpport\":21324,\"live\":false,\"liveseg\":-1,\"lm\":\"\",\"lip\":\"\",\"ws\":2,\"fxcount\":187,\"palcount\":71,\"cpalcount\":0,\"maps\":[{\"id\":0}],\"wifi\":{\"bssid\":\"50:EB:F6:73:0F:50\",\"rssi\":-39,\"signal\":100,\"channel\":3},\"fs\":{\"u\":16,\"t\":983,\"pmt\":1741284509},\"ndc\":0,\"arch\":\"esp32\",\"core\":\"v3.3.6-16-gcc5440f6a2\",\"lwip\":0,\"freeheap\":197820,\"uptime\":22385,\"time\":\"2025-3-6, 19:53:49\",\"opt\":79,\"brand\":\"WLED\",\"product\":\"FOSS\",\"mac\":\"f8b3b730969c\",\"ip\":\"192.168.50.150\"}}"
presets_data="{\"0\":{},\"1\":{\"on\":true,\"bri\":100,\"transition\":0,\"mainseg\":0,\"seg\":[{\"id\":0,\"start\":0,\"stop\":85,\"grp\":1,\"spc\":0,\"of\":0,\"on\":true,\"frz\":false,\"bri\":255,\"cct\":127,\"set\":0,\"n\":\"\",\"col\":[[0,38,255],[0,0,0],[0,0,0]],\"fx\":0,\"sx\":150,\"ix\":150,\"pal\":0,\"c1\":128,\"c2\":128,\"c3\":16,\"sel\":true,\"rev\":false,\"mi\":false,\"o1\":false,\"o2\":false,\"o3\":false,\"si\":0,\"m12\":0},{\"id\":1,\"start\":0,\"stop\":3,\"grp\":1,\"spc\":0,\"of\":0,\"on\":true,\"frz\":false,\"bri\":255,\"cct\":127,\"set\":0,\"n\":\"\",\"col\":[[255,245,245],[0,0,0],[0,0,0]],\"fx\":0,\"sx\":128,\"ix\":128,\"pal\":0,\"c1\":128,\"c2\":128,\"c3\":16,\"sel\":true,\"rev\":false,\"mi\":false,\"o1\":false,\"o2\":false,\"o3\":false,\"si\":0,\"m12\":0},{\"stop\":0},{\"stop\":0},{\"stop\":0},{\"stop\":0},{\"stop\":0},{\"stop\":0},{\"stop\":0},{\"stop\":0},{\"stop\":0},{\"stop\":0},{\"stop\":0},{\"stop\":0},{\"stop\":0},{\"stop\":0},{\"stop\":0},{\"stop\":0},{\"stop\":0},{\"stop\":0},{\"stop\":0},{\"stop\":0},{\"stop\":0},{\"stop\":0},{\"stop\":0},{\"stop\":0},{\"stop\":0},{\"stop\":0},{\"stop\":0},{\"stop\":0},{\"stop\":0},{\"stop\":0},{\"stop\":0},{\"stop\":0}],\"n\":\"startup\"}}"

state = json.loads(si_data)



#We'll only ever care about one segment
state['state']['seg'][0]['len'] = config.LED_COUNT

from wled_rpi import set_led, all_off, update_bri, get_effects, update_effect

led_colors = [(0, 0, 255)] * config.LED_COUNT  

app = Flask(__name__, static_folder='static')


# Route to serve the HTML file
@app.route('/')
def index():
    print("index")
    return render_template('index.htm')




@app.route('/settings', methods=["GET", "POST"])
def settings():
    # Options for the select box
    options = ['RGB', 'RBG', 'GRB']

    # Handle POST request to update the values
    if request.method == 'POST':
        settings_data['totalLeds'] = request.form.get('totalLeds', settings_data['totalLeds'])
        settings_data['colorOrder'] = request.form.get('my_select', settings_data['colorOrder'])
        settings_data['brightness'] = request.form.get('CA', settings_data['brightness'])
        settings_data['duration'] = request.form.get('TL', settings_data['duration'])

        # Update config_data and write to config.json
        config_data["LED_COUNT"] = int(settings_data['totalLeds'])
        config_data["LED_STRIP"] = settings_data['colorOrder']
        write_json(config_file_path, config_data)

        print(f"Updated settings: {settings_data}")

    # Pass data and options to the template
    selected_value = settings_data['colorOrder']  # Ensure selected_value matches colorOrder
    print(f"Options passed to template: {options}")
    print(f"Selected value passed to template: {selected_value}")

    return render_template('settings.htm', data=settings_data, options=options, selected_value=selected_value)


def set_color(rval, gval, bval):        #Set all leds to same color
    global state
    state['state']['pl'] = -1
    state['state']['seg'][0]['fx'] = -1
    led_colors = [(rval, gval, bval)]*config.LED_COUNT
    state['state']['seg'][0]['col'][0] = [rval, gval, bval]

    print("set_color", led_colors[0])
    config.myQueue.put((set_led, ((led_colors),)))    
   
def handle_on(on):
    global state
    state['state']['on'] = on
    if(on):        
        print("set power on")
        [config.DEFAULT_COLOR]*config.LED_COUNT
        config.myQueue.put((set_led, ((led_colors),)))
    else:
        print("set power off")
        config.myQueue.put((all_off, ()))
        
def handle_bri(bri):
    global state
    print(f'handle_bri({bri})')
    state['state']['bri'] = bri
    config.myQueue.put((update_bri, (bri,)))

def handle_effect(effect_id):
    print(f'handle_effect({effect_id})')
    global state
    if(effect_id == 0):        #effect 0 is solid color
        state['state']['seg'][0]['fx'] = -1
        handle_on(True)
        return   

    state['state']['pl'] = -1                #cancel any playlist currently active
    state['state']['seg'][0]['fx'] = effect_id
    config.myQueue.put((update_effect, (effect_id,)))

def handle_playlist(playlist_id):
    global state
    state['state']['pl'] = int(playlist_id)
    state['state']['seg'][0]['fx'] = -1
    print(f'handle_playlist({playlist_id})')
    config.myQueue.put((update_effect, (playlist_id,)))


@app.route("/json/fxdata", methods=["GET", "POST"])
def fxdata():
    return jsonify(json.loads(fxdata_data))

@app.route("/json/palx", methods=["GET", "POST"])
def palx():
    return jsonify(json.loads(palx_data))
    

@app.route("/json/palettes", methods=["GET", "POST"])
def pallets():
    return(json.loads(pallets_data))


@app.route("/json/si", methods=["GET", "POST"])
def si():
    return parse_state()

    

@app.route("/presets.json", methods=["GET", "POST"])
def presets():
    return(json.loads(presets_data))


def presets():
    return(json.loads(presets_data))

    
@app.route("/json/effects", methods=["GET", "POST"])
def parse_eff():
    var = get_effects()
    var2 = jsonify(var)
    return(var2)
    # return(json.loads(effects_data))



@app.route("/json/state", methods=["GET","POST"])
def parse_state():
    try:
        print("request", request)

        #No json data - this is just an info request
        if(not request.data):
            return(jsonify(state))

        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        
        # Process the JSON data here
        response = {
            "message": "JSON received successfully",
            "received_data": data
        }
        #print("data", data)

        
        for key, value in data.items() :
            match key:
                case 'on':
                    handle_on(value)
                case 'bri':
                    handle_bri(data['bri'])
                case 'seg':       #this sets color, but probably other things I'm not handling
                    if(isinstance(value, dict)):
                        if('col' in value):
                            led = value['col']
                            set_color(int(led[0][0]),int(led[0][1]), int(led[0][2]))
                        if('fx' in value):
                            print("data", data)
                            handle_effect(value['fx'])
                    else:
                        led = val['col']

                        if isinstance(led[0], list):
                            set_color(int(led[0][0]),int(led[0][1]), int(led[0][2]))
                        else:
                            set_color(int(led[0]),int(led[1]), int(led[2]))

                    response = state
                case 'effect':
                    handle_effect(value)
                case 'pl':
                    handle_playlist(value)
                case 'v':
                    response = state
                case 'time':
                    response = state        #should we do anything with this?
                case _:
                    print("no match", key)

        return jsonify(response), 200
        
    except Exception as e:
        breakpoint()
        return jsonify({"error": str(e)}), 500
    
@app.route("/json", methods=["POST"])
def parse_json():
    return parse_state()

#probably should change the port to somethings else

#socketio = SocketIO(app)

def run_flask_app():
#run on 127.0.0.0    app.run(debug=False, use_reloader=False)
    #see https://stackoverflow.com/questions/53522052/flask-app-valueerror-signal-only-works-in-main-thread
    #app.run(host="0.0.0.0", port=80, debug=True)

    #socketio = SocketIO(app)
    #socketio.run(app)
    app.logger.setLevel(logging.INFO)  # Set the logging level to INFO or lower
    app.logger.info("This will be logged if the level is set correctly")
    app.run(host="0.0.0.0", port=80)


#app = Flask(__name__)
#socketio = SocketIO(app)


#@socketio.on('connect')
#def handle_connect():
#    print('Client connected')

#@socketio.on('message')
#def handle_message(data):
#    print('Received message:', data)
    # Broadcast the message back to all clients
#    socketio.emit('message', data)

#@socketio.on('disconnect')
#def  handle_disconnect():
#    print('Client disconnected')

def start_flask():
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True  # Allow the main thread to exit even if the Flask thread is running
    flask_thread.start()








