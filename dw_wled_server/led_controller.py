from flask import Flask, send_from_directory, request, jsonify
from rpi_ws281x import PixelStrip, Color, ws
import os
import time
import math

# LED strip configuration
LED_COUNT = 20
LED_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 50
LED_INVERT = False
LED_CHANNEL = 0
LED_ORDER = ws.WS2811_STRIP_RGB

# Initialize the LED strip
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_ORDER)
strip.begin()

app = Flask(__name__)
led_colors = [(0, 0, 0)] *   # Initialize with all LEDs off

# Global power state of the LEDs
power_state = True  # Assume LEDs are on initially

# Function to interpolate between two colors
def interpolate_color(start_color, end_color, step, total_steps):
    r_start, g_start, b_start = start_color
    r_end, g_end, b_end = end_color

    # Calculate the difference in each channel
    r_diff = r_end - r_start
    g_diff = g_end - g_start
    b_diff = b_end - b_start

    # Calculate the interpolated color
    r = int(r_start + (r_diff * step / total_steps))
    g = int(g_start + (g_diff * step / total_steps))
    b = int(b_start + (b_diff * step / total_steps))

    return (r, g, b)

# Function to move LED colors clockwise with dissolve effect
def move_led_dissolve(interval, steps=10):
    global led_colors  # Use the global led_colors list

    # Move LED colors one position clockwise
    last_color = led_colors[-1]
    for i in range(LED_COUNT - 1, 0, -1):
        led_colors[i] = led_colors[i - 1]
    led_colors[0] = last_color

    # Update the LED strip with dissolve effect
    for step in range(1, steps + 1):
        for i in range(LED_COUNT):
            # Interpolate between the current and next LED color
            next_color = led_colors[(i - 1) % LED_COUNT]
            current_color = led_colors[i]
            interpolated_color = interpolate_color(current_color, next_color, step, steps)

            strip.setPixelColor(i, Color(*interpolated_color))
        strip.show()

        time.sleep(interval / steps)  # Adjust the speed of the transit




move_led_dissolve(2, steps=10)
    
# Route to serve the HTML file
@app.route("/")
def index():
    return send_from_directory(".", "index.html")

# API route to set LED color
@app.route("/api/set_led", methods=["POST"])
def set_led():
    data = request.json
    led_index = int(data["led_index"])
    r, g, b = data["color"]
    strip.setPixelColor(led_index, Color(r, g, b))
    strip.show()
    led_colors[led_index] = (r, g, b)
    return jsonify({"status": "success", "colors": led_colors}), 200

@app.route("/api/get_led_colors", methods=["GET"])
def get_led_colors():
    return jsonify({"colors": led_colors}), 200

# API route to toggle power
@app.route("/api/power_toggle", methods=["POST"])
def power_toggle():
    global power_state
    power_state = not power_state
    if not power_state:
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(0, 0, 0))
        strip.show()
    else:
        # Restore LEDs to their previous colors
        for i, (r, g, b) in enumerate(led_colors):
            strip.setPixelColor(i, Color(r, g, b))
        strip.show()
    return jsonify({"power": power_state}), 200

# API route to set brightness
@app.route("/api/set_brightness", methods=["POST"])
def set_brightness():
    data = request.json
    brightness = int(data["brightness"])
    strip.setBrightness(brightness)
    strip.show()
    return jsonify({"brightness": brightness}), 200

# Route to start the dissolve animation
@app.route("/api/start_dissolve", methods=["POST"])
def start_dissolve():
    global power_state
    interval = float(request.json["interval"])  # Get the interval from the request

    power_state = True  # Ensure LEDs are on
    while power_state:
        move_led_dissolve(interval)

    return jsonify({"status": "success"}), 200

# Route to stop the dissolve animation
@app.route("/api/stop_dissolve", methods=["POST"])
def stop_dissolve():
    global power_state
    power_state = False  # Stop the animation
    return jsonify({"status": "success"}), 200


# Run the Flask app
#if __name__ == "__main__":
#    app.run(host="0.0.0.0", port=5000)

