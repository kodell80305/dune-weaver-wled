import os
import shutil
import subprocess
import time
from datetime import datetime

def run_command(command):
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout.decode('utf-8')

def check_submodule():
    if not os.path.exists("WLED"):
        print("Submodule WLED not found. Initializing submodule...")
        run_command("git submodule update --init")
        run_command("git submodule update")
    else:
        print("Submodule WLED already populated.")

def backup_directories():
    timestamp = datetime.now().strftime("web-%Y-%m%dT%H:%M")
    backup_dir = os.path.join("backup_web", timestamp)
    os.makedirs(backup_dir, exist_ok=True)
    
    if os.path.exists("templates"):
        shutil.move("templates", os.path.join(backup_dir, "templates"))
    if os.path.exists("static"):
        shutil.move("static", os.path.join(backup_dir, "static"))

def copy_files():
    print("Copying files index.scss, iro.js, rangetouch.js, common.js, 404.htm")
    files_to_copy = [
        ("WLED/wled00/data/index.css", "static/styles"),
        ("WLED/wled00/data/iro.js", "static/js"),
        ("WLED/wled00/data/rangetouch.js", "static/js"),
        ("WLED/wled00/data/common.js", "static/js"),
        ("WLED/wled00/data/404.htm", "templates"),
        ("WLED/wled00/data/settings_leds.htm", "templates"),
        ("WLED/wled00/data/settings.htm", "templates")
    ]
    for src, dst in files_to_copy:
        run_command(f"cp {src} {dst}")

def patch_index_html():
    print("Patching index.htm")
    with open("WLED/wled00/data/index.htm", "r") as infile, open("templates/index.htm", "w") as outfile:
        for line in infile:
            line = line.replace("index.css", " {{ url_for('static', filename='styles/index.css') }}")
            line = line.replace("rangetouch.js", "{{ url_for('static', filename='js/rangetouch.js') }}")
            line = line.replace("common.js", "{{ url_for('static', filename='js/common.js') }}")
            line = line.replace("index.js", "{{ url_for('static', filename='js/index.js') }}")
            line = line.replace("toggleLiveview()\"", "toggleLiveview()\" hidden")
            line = line.replace("toggleSync()\"", "toggleSync()\" hidden")
            line = line.replace("settings');", "settings');\" hidden")
            line = line.replace("iro.js", "{{ url_for('static', filename='js/iro.js') }}")
            line = line.replace(">Reboot WLED", " hidden>Reboot WLED")
            line = line.replace(">Update WLED", " hidden>Update WLED")
            line = line.replace(">Instance", " hidden>Instance")
            line = line.replace(">Reset segments", " hidden>Reset segments")
            outfile.write(line)

def patch_settings_html():
    print("Patching settings.htm")
    with open("WLED/wled00/data/settings.htm", "r") as infile, open("templates/settings.htm", "w") as outfile:
        content = infile.read()
        content = content.replace("common.js", "{{ url_for('static', filename='js/common.js') }}")
        outfile.write(content)

def create_stub_websocket():
    print("Create StubWebSocket class")
    stub_websocket = """
class StubWebSocket:
    def __init__(self, url):
        self.url = url
        self.readyState = StubWebSocket.CONNECTING
        self.sentMessages = []

        # Simulate connection opening after a short delay
        time.sleep(0.01)
        self.readyState = StubWebSocket.OPEN
        if self.onopen:
            self.onopen()

    def send(self, data):
        self.sentMessages.append(data)
        if self.onmessage:
            self.onmessage({'data': data})

    def close(self):
        self.readyState = StubWebSocket.CLOSED
        if self.onclose:
            self.onclose()

    def onopen(self):
        print('Connected to WebSocket server')
        self.send('Hello, server!')

    def onmessage(self, event):
        print('Received message:', event['data'])

    def onwerror(self, error):
        print('WebSocket error:', error)

    def onclose(self):
        print('Disconnected from WebSocket server')

    def simulateMessage(self, data):
        if self.onmessage:
            self.onmessage({'data': data})

StubWebSocket.CONNECTING = 0
StubWebSocket.OPEN = 1
StubWebSocket.CLOSING = 2
StubWebSocket.CLOSED = 3
"""
    with open("static/js/index.js", "w") as outfile:
        outfile.write(stub_websocket)

def patch_index_js():
    print("Patching index.js")
    with open("WLED/wled00/data/index.js", "r") as infile, open("static/js/index.js", "a") as outfile:
        for line in infile:
            line = line.replace("WebSocket", "StubWebSocket")
            line = line.replace("var useWs = (ws && ws.readyState === StubWebSocket.OPEN);", "var useWs = false")
            outfile.write(line)

    with open("new_effects.js", "r") as effects_file:
        new_effects = effects_file.read()

    with open("static/js/index.js", "r") as infile:
        lines = infile.readlines()

    with open("static/js/index.js", "w") as outfile:
        for line in lines:
            if "var effects = eJson;" in line:
                line = new_effects
            outfile.write(line)

    with open("static/js/index.js", "r") as infile:
        lines = infile.readlines()
    
    hideTable = False

    with open("static/js/index.js", "w") as outfile:
        for line in lines:
            if(hideTable):
                line = line.replace('<i class="icons delete-icon">', '<i class="icons delete-icon" style="display:none;">')
                line = line.replace("Signal Strength", "//Signal Strength")
                line = line.replace("Uptime", "//Uptime")
                line = line.replace("Time", "//Time")
                line = line.replace("Free heap", "//Free heap")
                line = line.replace("Free PSRAM", "//Free PSRAM")
                line = line.replace("Estimated current", "//Estimated current")
                line = line.replace("Average FPS", "//Average FPS")
                line = line.replace("MAC address", "//MAC address")
                line = line.replace("CPU clock", "//CPU clock")
                line = line.replace("Flash size", "//Flash size")
                line = line.replace("Filesystem", "//Filesystem")
                outfile.write(line)

def main():
    print("Building web interface")
    check_submodule()
    backup_directories()
    
    os.makedirs("templates", exist_ok=True)
    os.makedirs("static/styles", exist_ok=True)
    os.makedirs("static/js", exist_ok=True)

    copy_files()
    patch_index_html()
    patch_settings_html()
    create_stub_websocket()
    patch_index_js()

    print("index.js patched successfully.")

if __name__ == "__main__":
    main()