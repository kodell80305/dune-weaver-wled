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
            line = line.replace("toggleSync()\"", "toggleSync()\" hidden")

            line = line.replace("toggleLiveview()\"", "toggleLiveview()\" hidden")
                        #todo extra quote her/
            if("toggleInfo()") in line:
                print("toggleInfo() found")
#                continue
#            line = line.replace("toggleInfo()", "toggleInfo()\" hidden ")
            line = line.replace("settings');\"", "settings');\" hidden")
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
   
        print(f'****** content start {len(content)}')
  
        ncontent = content.replace("common.js", "{{ url_for('static', filename='js/common.js') }}")
        print(f'****** content now {len(content)}')
        outfile.write(content + ncontent)


def create_stub_websocket():
    print("Create StubWebSocket class")
    stub_websocket = """class StubWebSocket {
  constructor(url) {
    this.url = url;
    this.readyState = StubWebSocket.CONNECTING;
    this.sentMessages = [];
    
    // Simulate connection opening after a short delay
    setTimeout(() => {
      this.readyState = StubWebSocket.OPEN;
      if (this.onopen) {
        this.onopen();
      }
    }, 10); 
  }

  send(data) {
    this.sentMessages.push(data);
    if (this.onmessage) {
      this.onmessage({ data: data });
    }
  }

  close() {
    this.readyState = StubWebSocket.CLOSED;
    if (this.onclose) {
      this.onclose();
    }
  }

  onopen() {
    console.log('Connected to WebSocket server');
    this.send('Hello, server!');
  }

  onmessage(event) {
    console.log('Received message:', event.data);
  } 

  onwerror(error) {
    console.error('WebSocket error:', error);
  }

  onclose () {
    console.log('Disconnected from WebSocket server');
  }
  
  simulateMessage(data) {
      if (this.onmessage) {
          this.onmessage({ data: data });
      }
  }
}

StubWebSocket.CONNECTING = 0;
StubWebSocket.OPEN = 1;
StubWebSocket.CLOSING = 2;
StubWebSocket.CLOSED = 3;
"""
    with open("static/js/index.js", "w") as outfile:
        outfile.write(stub_websocket)

def patch_index_js():
    print("Patching index.js")

    create_stub_websocket()

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

    with open("static/js/index.js", "w") as outfile:
        for line in lines:
            #Format of the table
            #${inforow("nothing strength",i.wifi.signal +"% ("+ i.wifi.rssi, " dBm)")}

            if("inforow" in line):

                if "Build" in line:
                    line = '''${inforow(\"Build","Dune Weaver WLED")}'''


            
                if "Time" in line:
                    line = '''${inforow(" "," ")}'''

                if("Signal strength") in line:
                    line = '''${inforow(" "," ")}'''

                if("Uptime") in line:
                    line = '''${inforow(\"Not Official WLED","so don't blame them\")}'''

                if("Free heap") in line:
                    line = '''${inforow(\"But do support them","it's a great resource\")}'''
                
                
                if("Environment") in line:
                    line = '''${inforow(" "," ")}'''
                
                        
                if("Flash size") in line:
                    line = '''${inforow(" "," ")}'''
                    
                if("CPU clock") in line:
                    line = '''${inforow(" "," ")}'''

                if("MAC address") in line:
                    line = '''${inforow(" "," ")}'''

                
                if("Estimated current") in line:
                    line = '''${inforow(" "," ")}'''

                if("Average FPS") in line:
                    line = '''${inforow(" "," ")}'''

                if("Filesystem") in line:
                    line = '''${inforow(" "," ")}'''


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
    patch_index_js()



if __name__ == "__main__":
    main()