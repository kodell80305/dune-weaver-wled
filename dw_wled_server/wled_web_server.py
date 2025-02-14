from flask import Flask, send_from_directory, request, jsonify
import os
import math
import threading
import config

app = Flask(__name__)


# Route to serve the HTML file
@app.route("/", methods = ['GET', 'POST'])
def index():
    return send_from_directory(".", "index.html")

@app.route("/json/eff", methods = ['GET', 'POST'])
def send_effects():
    return send_from_directory(".", "json_data")
#       return jsonify("effects": [{"id": 0, "name": "Static", "description": "Solid color lighting effect", "parameters": {"color": "#FF0000", "brightness": 128}}]), 200

        

# API route to toggle power
@app.route("/json/state", methods=["POST"])
def send_state():
    config.myQueue.put(f'state')
#     return send_from_directory(".", "state.html")
    return jsonify({"on": config.power_state}), 200

# API route to toggle power
@app.route("/api/power_toggle", methods=["POST"])
def send_power_toggle():
    config.myQueue.put(f'power_toggle')
    return jsonify({"power": config.power_state}), 200

# API route to toggle ppwer
@app.route("/json", methods=["POST"])
def send_json():
    config.myQueue.put(f'json')
    return jsonify({"power": config.power_state}), 200
 

def run_flask_app():
#run on 127.0.0.0    app.run(debug=False, use_reloader=False)
    app.run(host="0.0.0.0", port=80)
    
def start_flask():
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True  # Allow the main thread to exit even if the Flask thread is running
    flask_thread.start()
    






