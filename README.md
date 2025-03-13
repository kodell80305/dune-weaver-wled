# dune-weaver-wled-server

This code is designed to run with the amazing [Dune Weaver](https://github.com/tuanchris/dune-weaver) project.  It's using the WLED code on a standalone ESP32 to control the leds for the sand table.   The project uses a raspberry pi to control a CNC board (mks dlc32 running Fluidnc).   An additional esp32 running WLED is used to control the LED strip surrounding the table.    Since the Raspberry Po zero 2w is an essential port of the system, I've implemented a WLED compatible server to replace the additional ESP32 device. 

#Installation

The web pages are all directly from the WLED project.  I've included this as a submodule  After cloning the repo, you should be able to run ```sudo python startService.py```.  This is (supposed to - needs more fresh install testing):
*If needed, populate the WLED submodule 
*If needed, ynamically build the templates and static directories used by the flask web server from the WLED sources (elminate websocket, hide unsupported features, work in flask, etc.) 
*If needed create or modify the service file
*Start the service
The command can also be used to stop the service (or the normal systemctl commands can be used).


Features implemented are going to be those that are used on the Dune Weaver project, but the intentions is to be as compatible as possible with the WLED functons.

Since the project has integrated the WLED api & html in the interface, I wanted to provide the same function from a flask server running on the raspberry pi.   Currently (as of 3/8/2025), I've copied the web interface from WLED and wrote a script to build a functional web page from their content (modify to make flask happy, insert stub code for WebSocket & hide buttons that are non-functional.   What does work is the control of brightness, power, color chosing from the web api.   I've also implemented a set of JSON commands from the WLED json API, but I don't know if they will be compatible with what the project will do in the future.


![image](https://github.com/user-attachments/assets/e7e116eb-890b-4bba-abfd-04471f5961ea)

As of 3/6/2025, it looks like this is the base interface ... web UI + mostly JSON commands.    Initial web UI is in ... stolen from WLED, so there are lots of things that aren't working & I've mostly tested in simulation.

Simplified version of embedded web UI
  _send_command()  json commands to the /state url - it needs the following in the state response:
"on", "ps", "pl, "bri" parameter


    def check_wled_status(self) -> Dict:
        """Check WLED connection status and brightness"""
        return self._send_command()

    def set_brightness(self, value: int) -> Dict:
        """Set WLED brightness (0-255)"""
        return self._send_command({"bri": value})

    def set_power(self, state: int) -> Dict:
        """Set WLED power state (0=Off, 1=On, 2=Toggle)"""
        if state not in [0, 1, 2]:
            return {"connected": False, "message": "Power state must be 0 (Off), 1 (On), or 2 (Toggle)"}
        if state == 2:
            return self._send_command({"on": "t"})  # Toggle
        return self._send_command({"on": bool(state)})

    def set_color(self, r: int = None, g: int = None, b: int = None, w: int = None, hex: str = None) -> Dict:
        """Set WLED color using RGB(W) values or hex color code"""
        if hex is not None:
            try:
                r, g, b = self._hex_to_rgb(hex)
            except ValueError as e:
                return {"connected": False, "message": str(e)}

        # Prepare segment with color
        seg = {"col": [[r or 0, g or 0, b or 0]]}
        if w is not None:
            if not 0 <= w <= 255:
                return {"connected": False, "message": "White value must be between 0 and 255"}
            seg["col"][0].append(w)

        return self._send_command({"seg": [seg]})

    def set_effect(self, effect_index: int, speed: int = None, intensity: int = None, 
                   brightness: int = None, palette: int = None,
                   # Primary color
                   r: int = None, g: int = None, b: int = None, w: int = None, hex: str = None,
                   # Secondary color
                   r2: int = None, g2: int = None, b2: int = None, w2: int = None, hex2: str = None,
                   # Transition
                   transition: int = 0) -> Dict:
        """
        Set WLED effect with optional parameters
        Args:
            effect_index: Effect index (0-101)
            speed: Effect speed (0-255)
            intensity: Effect intensity (0-255)
            brightness: LED brightness (0-255)
            palette: FastLED palette index (0-46)
            r, g, b: Primary RGB color values (0-255)
            w: Primary White value for RGBW (0-255)
            hex: Primary hex color code (e.g., '#ff0000' or 'ff0000')
            r2, g2, b2: Secondary RGB color values (0-255)
            w2: Secondary White value for RGBW (0-255)
            hex2: Secondary hex color code
            transition: Duration of crossfade in 100ms units (e.g. 7 = 700ms). Default 0 for instant change.
        """
        try:
            effect_index = int(effect_index)
        except (ValueError, TypeError):
            return {"connected": False, "message": "Effect index must be a valid integer between 0 and 101"}

        if not 0 <= effect_index <= 101:
            return {"connected": False, "message": "Effect index must be between 0 and 101"}

        # Convert primary hex to RGB if provided
        if hex is not None:
            try:
                r, g, b = self._hex_to_rgb(hex)
            except ValueError as e:
                return {"connected": False, "message": f"Primary color: {str(e)}"}

        # Convert secondary hex to RGB if provided
        if hex2 is not None:
            try:
                r2, g2, b2 = self._hex_to_rgb(hex2)
            except ValueError as e:
                return {"connected": False, "message": f"Secondary color: {str(e)}"}

        # Build segment parameters
        seg = {"fx": effect_index}
        
        if speed is not None:
            if not 0 <= speed <= 255:
                return {"connected": False, "message": "Speed must be between 0 and 255"}
            seg["sx"] = speed
        
        if intensity is not None:
            if not 0 <= intensity <= 255:
                return {"connected": False, "message": "Intensity must be between 0 and 255"}
            seg["ix"] = intensity

        # Prepare colors array
        colors = []
        
        # Add primary color
        primary = [r or 0, g or 0, b or 0]
        if w is not None:
            if not 0 <= w <= 255:
                return {"connected": False, "message": "Primary white value must be between 0 and 255"}
            primary.append(w)
        colors.append(primary)
        
        # Add secondary color if any secondary color parameter is provided
        if any(x is not None for x in [r2, g2, b2, w2, hex2]):
            secondary = [r2 or 0, g2 or 0, b2 or 0]
            if w2 is not None:
                if not 0 <= w2 <= 255:
                    return {"connected": False, "message": "Secondary white value must be between 0 and 255"}
                secondary.append(w2)
            colors.append(secondary)

        if colors:
            seg["col"] = colors

        if palette is not None:
            if not 0 <= palette <= 46:
                return {"connected": False, "message": "Palette index must be between 0 and 46"}
            seg["pal"] = palette

        # Combine with global parameters
        state = {"seg": [seg], "transition": transition}
        if brightness is not None:
            if not 0 <= brightness <= 255:
                return {"connected": False, "message": "Brightness must be between 0 and 255"}
            state["bri"] = brightness

        return self._send_command(state)

    def set_preset(self, preset_id: int) -> bool:
        preset_id = int(preset_id)
        # Send the command and get response
        response = self._send_command({"ps": preset_id})
        logger.debug(response)
        return response

def effect_loading(led_controller: LEDController):
    res = led_controller.set_effect(47, hex='#ffa000', hex2='#000000', palette=0, speed=150, intensity=150)
    if res.get('is_on', False):
        return True
    else:
        return False

def effect_idle(led_controller: LEDController):
    led_controller.set_preset(1)

def effect_connected(led_controller: LEDController):
    res = led_controller.set_effect(0, hex='#08ff00', brightness=100)
    time.sleep(1)
    led_controller.set_effect(0, brightness=0)  # Turn off
    time.sleep(0.5)
    res = led_controller.set_effect(0, hex='#08ff00', brightness=100)
    time.sleep(1)
    effect_idle(led_controller)
    if res.get('is_on', False):
        return True
    else:
        return False

def effect_playing(led_controller: LEDController):
    led_controller.set_preset(2)

def effect_error(led_controller: LEDController):
    res = led_controller.set_effect(0, hex='#ff0000', brightness=100)


There are four files that are used:  

startup.py  - starts the low level interface thread and then the flask/web server thread.

wled_rpi.py - the low level interface to control the leds.   Needs to run at root level

wled_web_server.py - web interface.  You probably don't want this to run at root.   I think flask drops levels(?) - need to verify this.    The intent is that this maintains the status/information on the leds and the low level interface just implements it.   The control is done by a message queue between flask/low level interface where the low level function pointer and all the arguments are passed in on the message queue. 

config.py - global values

run sudo python startup.py

The only things tested are the curl scripts in test.sh.  Run ./test.sh 127.0.0.1   (or use the IP address of a real WLED server.

The json parsing is minimal and a I haven't implemented any info/effects yet.   I want to work out how to change the brightness while doing effects/how to cancel effects without using yet another thread spawned from the low level interface.

Added the ability for effects/setting brightness without stopping effects (does cause restart right now ... not sure if this bothers me enough to fix it)  Only tested in simulation mode on windows, until I can test on pi.


