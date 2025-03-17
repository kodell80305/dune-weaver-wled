import requests
import json
from typing import Dict, Optional
import time
import logging
from wled_rpi import effects_list  # Import effects_list from wled_rpi.py

logger = logging.getLogger(__name__)

class LEDController:
    def __init__(self, ip_address: Optional[str] = None):
        self.ip_address = ip_address
        self.effects = {
            "Rainbow": self.rainbow_effect,
            # Add other effects here if needed
        }
        self.strip = None  # Initialize strip as None
        if not self.ip_address:
            # Mock the strip object if no IP address is provided
            from unittest.mock import MagicMock
            self.strip = MagicMock()
            self.strip.numPixels.return_value = 50  # Default to 50 LEDs

    def _get_base_url(self) -> str:
        """Get base URL for WLED JSON API"""
        if not self.ip_address:
            raise ValueError("No WLED IP configured")
        return f"http://{self.ip_address}/json"

    def set_ip(self, ip_address: str) -> None:
        """Update the WLED IP address"""
        self.ip_address = ip_address

    def _send_command(self, state_params: Dict = None) -> Dict:
        """Send command to WLED and return status"""
        try:
            url = self._get_base_url()
            
            # First check current state
            response = requests.get(f"{url}/state", timeout=2)
            response.raise_for_status()
            current_state = response.json()
            
            # If WLED is off and we're trying to set something, turn it on first
            if not current_state.get('on', False) and state_params and 'on' not in state_params:
                # Turn on power first
                requests.post(f"{url}/state", json={"on": True}, timeout=2)
            
            # Now send the actual command if there are parameters
            if state_params:
                response = requests.post(f"{url}/state", json=state_params, timeout=2)
                response.raise_for_status()
                response = requests.get(f"{url}/state", timeout=2)
                response.raise_for_status()
                current_state = response.json()
                
            preset_id = current_state.get('ps', -1)
            playlist_id = current_state.get('pl', -1)

            # Use True as default since WLED is typically on when responding
            is_on = current_state.get('on', True)
            
            return {
                "connected": True,
                "is_on": is_on,
                "preset_id": preset_id,
                "playlist_id": playlist_id,
                "brightness": current_state.get('bri', 0),
                "message": "WLED is ON" if is_on else "WLED is OFF"
            }

        except ValueError as e:
            return {"connected": False, "message": str(e)}
        except requests.RequestException as e:
            return {"connected": False, "message": f"Cannot connect to WLED: {str(e)}"}
        except json.JSONDecodeError as e:
            return {"connected": False, "message": f"Error parsing WLED response: {str(e)}"}

    def check_wled_status(self) -> Dict:
        """Check WLED connection status and brightness"""
        return self._send_command()

    def set_brightness(self, value: int) -> Dict:
        """Set WLED brightness (0-255)"""
        if not 0 <= value <= 255:
            return {"connected": False, "message": "Brightness must be between 0 and 255"}
        return self._send_command({"bri": value})

    def set_power(self, state: int) -> Dict:
        """Set WLED power state (0=Off, 1=On, 2=Toggle)"""
        if state not in [0, 1, 2]:
            return {"connected": False, "message": "Power state must be 0 (Off), 1 (On), or 2 (Toggle)"}
        if state == 2:
            return self._send_command({"on": "t"})  # Toggle
        return self._send_command({"on": bool(state)})

    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color string to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            raise ValueError("Hex color must be 6 characters long (without #)")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def set_color(self, r: int = None, g: int = None, b: int = None, w: int = None, hex: str = None, rgb: tuple = None) -> None:
        """
        Set the color of all LEDs using RGB(W) values, a hex color code, or an RGB tuple.
        If a WLED IP address is configured, send the command via the WLED API.
        Otherwise, use the mocked strip object.
        """
        if rgb is not None:
            r, g, b = rgb  # Unpack the RGB tuple
        elif hex is not None:
            r, g, b = self._hex_to_rgb(hex)

        if self.ip_address:
            # Use the WLED API to set the color
            color_data = {"seg": [{"col": [[r or 0, g or 0, b or 0]]}]}
            if w is not None:
                color_data["seg"][0]["col"][0].append(w)
            self._send_command(color_data)
        else:
            # Use the mocked strip object
            color = self.Color(r or 0, g or 0, b or 0)  # Create the color
            for i in range(self.strip.numPixels()):  # Iterate over all LEDs
                self.strip.setPixelColor(i, color)  # Set the color for each LED
            self.strip.show()  # Update the strip

    def set_effect(self, effect_index: int, speed: int = None, intensity: int = None, 
                   brightness: int = None, palette: int = None,
                   # Primary color
                   r: int = None, g: int = None, b: int = None, w: int = None, hex: str = None,
                   # Secondary color
                   r2: int = None, g2: int = None, b2: int = None, w2: int = None, hex2: str = None,
                   # Transition
                   transition: int = 0, color: str = None) -> Dict:
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
            color: Hex color string (e.g., '#0000FF') for primary color.
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

        # Convert `color` parameter to RGB if provided
        if color is not None:
            try:
                r, g, b = self._hex_to_rgb(color)
            except ValueError as e:
                return {"connected": False, "message": f"Color parameter: {str(e)}"}

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

    def run_effect(self, effect_name):
        """
        Runs the specified effect if it exists.
        """
        if effect_name in self.effects:
            # Log the effect being run
            print(f"Running effect: {effect_name}")
            # Log the JSON payload for the effect
            if self.ip_address:
                payload = {"seg": [{"fx": 0, "col": [[255, 0, 0], [0, 255, 0], [0, 0, 255]]}]}
                print(f"JSON payload being sent for effect '{effect_name}': {payload}")
            self.effects[effect_name]()
        else:
            raise ValueError(f"Effect '{effect_name}' not found")

    def _get_effect_id(self, effect_name: str) -> Optional[int]:
        """
        Retrieve the fx ID for a given effect name from the effects list.
        """
        for effect in effects_list:
            if effect.get("Effect") == effect_name:
                return int(effect["ID"])
        return None

    def rainbow_effect(self):
        """
        Implementation of a rainbow effect.
        If a WLED IP address is configured, send the command via the WLED API.
        Otherwise, use the mocked strip object.
        """
        fx_id = self._get_effect_id("Rainbow")
        if fx_id is None:
            raise ValueError("Rainbow effect ID not found in effects list")

        if self.ip_address:
            # JSON payload for the Rainbow effect
            payload = {"seg": [{"fx": fx_id, "sx": 50, "ix": 128, "pal": 6}]}  # Example values for speed, intensity, and palette
            print(f"JSON payload being sent for Rainbow effect: {payload}")
            self._send_command(payload)
        else:
            # Use the mocked strip object
            for i in range(self.strip.numPixels()):
                color = self.wheel((i * 256 // self.strip.numPixels()) & 255)
                self.strip.setPixelColor(i, color)
            self.strip.show()

    def wheel(self, pos):
        """
        Generate rainbow colors across 0-255 positions.
        """
        if pos < 85:
            return self.Color(pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return self.Color(255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return self.Color(0, pos * 3, 255 - pos * 3)

    def Color(self, red, green, blue):
        """
        Helper function to create a color.
        """
        return (red << 16) | (green << 8) | blue

    def turn_off(self):
        """
        Turns off all LEDs.
        If a WLED IP address is configured, send the command via the WLED API.
        Otherwise, use the mocked strip object.
        """
        if self.ip_address:
            # Use the WLED API to turn off the LEDs
            self._send_command({"on": False})
        else:
            # Use the mocked strip object
            for i in range(self.strip.numPixels()):  # Iterate over all LEDs
                self.strip.setPixelColor(i, 0)  # Set each LED to off
            self.strip.show()  # Update the strip

    def set_brightness(self, brightness):
        """
        Set the brightness of the LEDs.
        If a WLED IP address is configured, send the command via the WLED API.
        Otherwise, use the mocked strip object.
        """
        if self.ip_address:
            # Use the WLED API to set brightness
            self._send_command({"bri": brightness})
        else:
            # Use the mocked strip object
            self.strip.setBrightness(brightness)
            self.strip.show()

    def turn_on(self):
        """
        Turns on all LEDs with a default color (e.g., white).
        If a WLED IP address is configured, send the command via the WLED API.
        Otherwise, use the mocked strip object.
        """
        if self.ip_address:
            # Use the WLED API to turn on the LEDs
            self._send_command({"on": True})
        elif self.strip:
            # Use the mocked strip object
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, self.Color(255, 255, 255))  # Default to white
            self.strip.show()
        else:
            raise ValueError("LED strip is not initialized")

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