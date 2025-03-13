#!/bin/bash

# Initialize and update the WLED submodule
if [ ! -d "WLED" ]; then
    echo "Submodule WLED not found. Initializing submodule..."
    git submodule update --init
fi
git submodule update

echo "Building web interface"
mkdir -p templates
mkdir -p static/styles
mkdir -p static/js

echo "Copying files index.scss, iro.js, rangetouch.js, common.js, 404.htm"
cp WLED/wled00/data/index.css static/styles
cp WLED/wled00/data/iro.js static/js
cp WLED/wled00/data/rangetouch.js static/js
cp WLED/wled00/data/common.js static/js
cp WLED/wled00/data/404.htm templates
cp WLED/wled00/data/settings_leds.htm templates
echo "word count setings.htm"
wc templates/settings.htm
cp WLED/wled00/data/settings.htm templates

#<button id="buttonSr" onclick="toggleLiveview()"><i class="icons">&#xe410;</i><p class="tab-label">Peek</p></button>
#sed "s/toggleLiveView()\"/toggleLiveView()\" hidden/g" |
echo "Patching index.htm"


cat  WLED/wled00/data/index.htm | sed "s/index\.css/ {{ url_for('static', filename='styles\/index.css') }}/g" | 
sed "s/rangetouch\.js/{{ url_for('static', filename='js\/rangetouch.js') }}/g" |
sed "s/common\.js/{{ url_for('static', filename='js\/common.js') }}/g" |
sed "s/index\.js/{{ url_for('static', filename='js\/index.js') }}/g"  |
sed "s/toggleLiveview()\"/toggleLiveview()\" hidden/g" |
sed "s/toggleSync()\"/toggleSync()\" hidden/g" |
sed "s/settings');./settings');\" hidden/g" | 
sed "s/iro\.js/{{ url_for('static', filename='js\/iro.js') }}/g" > templates/index.htm
perl  -i -pe 's/>Reboot WLED/ hidden>Reboot WLED/' templates/index.htm
perl  -i -pe 's/>Update WLED/ hidden>Update WLED/' templates/index.htm
perl  -i -pe 's/>Instance/ hidden>Instance/' templates/index.htm
perl  -i -pe 's/>Reset segments/ hidden>Reset segments/' templates/index.htm
#my SegClass=q(<div class="seg btn btn-s${off?' off':''}" style="padding:0;margin-bottom:12px;">);
#my SegClassHidden=q(<div class="seg btn btn-s${off?' off':''}" style="display:none;">);
#perl -i -pe 's/$SegClass/$SegClassHidden/' templates/index.htm

#index.js wants websocket ... let's create a fake web socket class

echo "Create StubWebSocket class"
insert_stub=$(cat <<EOF
class StubWebSocket {
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
EOF
)

file_to_patch="path/to/your/file.js"

# Define the effects to insert
insert_effects=$(cat <<EOF
var effects = [
    ['0', "Solid"],
    ['9', "Rainbow"],
    ['13', "Theater"],
    ['14', "Theater Rainbow"]
];
EOF
)

# Use sed to find the line and insert the new lines after it
#sed -i "/var effects = eJson;/a $insert_lines" "$file_to_patch"
#last is ugly hack, my brain is too tired to deal with sed right now ..
#sed 's/if (!s) return false/return false/' >> static/js/index.js




echo "$insert_stub"  > static/js/index.js
cat WLED/wled00/data/index.js |
sed "s/WebSocket/StubWebSocket/g" |
sed "s/var useWs = (ws && ws.readyState === StubWebSocket.OPEN);/var useWs = false/" >> static/js/index.js



echo "xxxword count setttings.htm"
wc templates/settings.htm

cat WLED/wled00/data/settings.htm |
sed "s/common\.js/{{ url_for('static', filename='js\/common.js') }}/g" >> templates/settings.htm


echo "wxxxord count setttings.htm"
wc templates/settings.htm

perl  -i -pe "s/var effects = eJson;/$insert_effects/" static/js/index.js

# Insert a return after the text "function showErrorToast() {" in index.js
#perl -i -pe 's|(function showErrorToast\(\)\s*{)|$1\n    return;|' static/js/index.js

# Hide the delete icon for the segments in index.js
#perl -i -pe 's|(<i class="icons delete-icon">)|$1\n    style="display:none;"|' static/js/index.js

# Comment out lines containing specific text in index.js
#perl -i -pe 's|.*Signal Strength.*|//&|' static/js/index.js
#perl -i -pe 's|.*Uptime.*|//&|' static/js/index.js
#perl -i -pe 's|.*Time.*|//&|' static/js/index.js
#perl -i -pe 's|.*Free Heep.*|//&|' static/js/index.js
#perl -i -pe 's|.*Free PSRPM.*|//&|' static/js/index.js
#perl -i -pe 's|.*Estimated Current.*|//&|' static/js/index.js
#perl -i -pe 's|.*Average FPS.*|//&|' static/js/index.js
#perl -i -pe 's|.*MAC address.*|//&|' static/js/index.js
perl -i -pe 's|.*CPU Clock.*|//&|' static/js/index.js
#perl -i -pe 's|.*Flash Size.*|//&|' static/js/index.js
#perl -i -pe 's|.*File System.*|//&|' static/js/index.js

echo "index.js patched successfully."

