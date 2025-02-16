from flask import Flask, send_from_directory, request, jsonify
import os
import math
import threading
import config
import requests
import json
from wled_rpi import restore, all_off, update_bri

on=False
bri=128
transition=7       #time transition between effects units of 100 ms
#I'm not sure what som
#{"on":true,"bri":128,"transition":7,"ps":-1,"pl":-1,"ledmap":0,"AudioReactive":{"on":false},"nl":{"on":false,"dur":60,"mode":1,"tbri":0,"rem":-1},
#"udpn":{"send":false,"recv":true,"sgrp":1,"rgrp":1},"lor":0,"mainseg":0,"seg":[{"id":0,"start":0,"stop":30,"len":30,"grp":1,"spc":0,"of":0,
#"on":true,"frz":false,"bri":255,"cct":127,"set":0,"col":[[255,160,0],[0,0,0],[0,0,0]],"fx":0,"sx":128,"ix":128,"pal":0,"c1":128,"c2":128,
#Not scaled by brightness
led_colors = [(bri, bri, bri)] * config.LED_COUNT  

app = Flask(__name__)



# Route to serve the HTML file
@app.route("/", methods = ['GET', 'POST'])
def index():
    return send_from_directory(".", "index.html")

@app.route("/json/eff", methods = ['GET', 'POST'])
def send_effects():
    return send_from_directory(".", "json_data")
#       return jsonify("effects": [{"id": 0, "name": "Static", "description": "Solid color lighting effect", "parameters": {"color": "#FF0000", "brightness": 128}}]), 200

   
def update_color(rval, gval, bval):        # Restore LEDs to their previous colors
    print("in update_color")

    for i in range(0, config.LED_COUNT):
        led_colors[i] = (rval,gval,bval)

    config.myQueue.put((restore, ((led_colors),)))    
   
    
def handle_on(on_arg):
    on = on_arg
    if(on_arg == 't'):        
        config.myQueue.put((restore, ((led_colors),)))
        
    if(on_arg == 'f'):
        config.myQueue.put((all_off, ()))
        
def handle_bri(bri_arg):
    bri = bri_arg
    config.myQueue.put((update_bri, (bri,)))
    
        
@app.route("/json/state", methods=["POST"])
def parse_state():
    try:
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
  #                      for index, led in val:
                      led = val['col']
                      print("call update color")
                      update_color(int(led[0][0]),int(led[0][1]), int(led[0][2]))
                      

                      
                    
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/json", methods=["POST"])
def parse_json():
    parse_state()


#probaly should change the port to somethings else
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

def run_flask_app():
#run on 127.0.0.0    app.run(debug=False, use_reloader=False)
    app.run(host="0.0.0.0", port=80)
    
def start_flask():
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True  # Allow the main thread to exit even if the Flask thread is running
    flask_thread.start()
    






