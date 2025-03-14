import os
import shutil
import subprocess
import time
from datetime import datetime
import argparse

def run_command(command):
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout.decode('utf-8')

def check_submodule():
    if not os.path.exists("WLED/wled00"):
        print("Submodule WLED not found. Initializing submodule...")
        run_command("git submodule update --init")
        run_command("git submodule update")
    else:
        print("Submodule WLED already populated.")

def backup_directories(enable_backup):
    if not enable_backup:
        print("Backup creation is disabled.")
        return

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


def display_none(line, key):
    if f">{key}" in line:
        line = line.replace(f">{key}", f" style=\"display: none;\">{key}")
        print(f"    {line.lstrip()}", end="")
    return line



def fix_url(line):
    url_mappings = [
        ("styles", "index.css"),
        ("js", "rangetouch.js"),
        ("js", "common.js"),
        ("js", "index.js"),
        ("js", "iro.js")
    ]

    for type_, page in url_mappings:
        if page in line and "url_for" not in line:
            line = line.replace(page, f"{{{{ url_for('static', filename='{type_}/{page}') }}}}")
            print(f"    {line.lstrip()}", end="")
    return line

def hide_button(line, button):
    """
    Replace the specified button string with 'hidden<button>' in the given line.
    :param line: The input string to process.
    :param button: The button string to hide.
    :return: The modified string with the button hidden, or the original line if the button is not found.
    """
    if button not in line:
        return line

    line = line.replace(button, f" hidden{button}")
    print(f"    {line.lstrip()}", end="")
    return line


def hide_button_post(line, button):
    """
    Replace the specified button string with 'hidden<button>' in the given line.
    :param line: The input string to process.
    :param button: The button string to hide.
    :return: The modified string with the button hidden, or the original line if the button is not found.
    """
    if button not in line:
        return line

    if "hidden" not in line:
        line = line.replace(button, f" {button} hidden")
        print(f"    {line.lstrip()}", end="")

    return line

def patch_index_html():
    print("Patching index.htm")

    buttons_to_hide = [
        ">Reboot WLED",
        ">Update WLED",
        ">Instance",
        ">Reset segments"
    ]

    buttons_to_hide_post = [
        "toggleLiveview()\"",
        "toggleSync()\"",
        "toggleNodes()\""
    ]
    with open("WLED/wled00/data/index.htm", "r") as infile, open("templates/index.htm", "w") as outfile:
        for line in infile:
            line = fix_url(line)
            for button in buttons_to_hide:
                line = hide_button(line, button)
            for button in buttons_to_hide_post:
                line = hide_button_post(line, button)
            outfile.write(line)

def patch_settings_html():
    print("Patching settings.htm")

    buttons_to_hide = ["Security & Updates",
                       "Usermods",
                       "Time & Macros",
                          "Sync Interfaces",
                          "User Interface",
                          "2D Configuration",
                          "WiFi Setup"
    ]

    with open("WLED/wled00/data/settings.htm", "r") as infile:
        lines = infile.readlines()

    with open("templates/settings.htm", "w") as outfile:
        for line in lines:
            line = fix_url(line)
            for button in buttons_to_hide:
                line = display_none(line, button)
            outfile.write(line)

def create_stub_websocket():
    print("    create StubWebSocket class")
    
    stub_websocket = """class StubWebSocket {

  constructor(url) {
    this.url = url;
    this.readyState = StubWebSocket.CONNECTING;
    this.sentMessages = [];

    console.log("Creating StubWebSocket");


    
    // Simulate connection opening after a short delay
    setTimeout(() => {
      //this.readyState = StubWebSocket.OPEN;
      if (this.onopen) {
        console.log("calling onopen");
        this.onopen();
        //this.readyState = StubWebSocket.OPEN;
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
    this.readyState = StubWebSocket.OPEN;
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

def generate_inforow(line, key, label, value):
    """
    Generate an inforow line for the index.js file if the key is in the line.
    :param line: The current line being processed.
    :param key: The key to identify the inforow (e.g., "Build").
    :param label: The label to display (e.g., "Build").
    :param value: The value to display (e.g., "Dune Weaver WLED").
    :return: The modified line if the key matches, otherwise the original line.
    """
    if "inforow" in line and key in line:
        return f'${{inforow("{label}","{value}")}}'
    return line

def patch_index_js():
    print("Patching index.js")

    create_stub_websocket()

    with open("WLED/wled00/data/index.js", "r") as infile, open("static/js/index.js", "a") as outfile:
        for line in infile:
            line = line.replace("WebSocket", "StubWebSocket")
            outfile.write(line)

    with open("new_effects.js", "r") as effects_file:
        new_effects = effects_file.read()

    with open("static/js/index.js", "r") as infile:
        lines = infile.readlines()

    with open("static/js/index.js", "w") as outfile:
        for line in lines:
            if "var effects = eJson;" in line:  # Detect the line where effects are defined
                outfile.write(line)
                outfile.write(new_effects)  # Insert the new effects content
                print(f"    new_effects.js content inserted after 'var effects = eJson;'")
            else:
                outfile.write(line)

    inforow_data = [
        ("Build", "Build", "Dune Weaver WLED"),
        ("Time", " ", " "),
        ("Signal strength", " ", " "),
        ("Uptime", "Not Official WLED", "so don't blame them"),
        ("Free heap", "But do support them", "it's a great resource"),
        ("Environment", " ", " "),
        ("Flash size", " ", " "),
        ("CPU clock", " ", " "),
        ("MAC address", " ", " "),
        ("Estimated current", " ", " "),
        ("Average FPS", " ", " "),
        ("Filesystem", " ", " ")
    ]

    with open("static/js/index.js", "r") as infile:
        lines = infile.readlines()

    with open("static/js/index.js", "w") as outfile:
        for line in lines:
            for key, label, value in inforow_data:
                line = generate_inforow(line, key, label, value)
            outfile.write(line)

def main():
    parser = argparse.ArgumentParser(description="Build the web interface for Dune Weaver WLED.")
    parser.add_argument("--backup", action="store_true", help="Enable creation of backup directories.")
    args = parser.parse_args()

    print("Building web interface")
    check_submodule()
    backup_directories(args.backup)
    
    print("Creating directories templates, static/styles, static/js")
    os.makedirs("templates", exist_ok=True)
    os.makedirs("static/styles", exist_ok=True)
    os.makedirs("static/js", exist_ok=True)
    
    print("Copying files from WLED submodule")
    copy_files()
    patch_index_html()
    patch_settings_html()
    patch_index_js()

if __name__ == "__main__":
    main()