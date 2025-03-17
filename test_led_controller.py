import unittest
from unittest.mock import MagicMock
from led_controller import LEDController
import argparse
import time  # Added for introducing delay
from wled_rpi import effects_list  # Import effects_list from wled_rpi.py

class TestLEDController(unittest.TestCase):
    # Default delay between tests (configurable via command-line argument)
    delay_between_tests = 3

    def setUp(self):
        # Initialize LEDController with a valid IP address or mock
        self.led_controller = LEDController(ip_address="192.168.50.10")  # Replace with your WLED IP
        # Alternatively, use a mocked strip object by not providing an IP address
        # self.led_controller = LEDController()

    def tearDown(self):
        # Introduce a delay between tests
        time.sleep(self.delay_between_tests)

    def test_set_color(self):
        # Test setting red, green, and blue colors across all LEDs
        print("Running test: test_set_color")
        colors = [
            {"r": 255, "g": 0, "b": 0, "name": "Red"},
            {"r": 0, "g": 255, "b": 0, "name": "Green"},
            {"r": 0, "g": 0, "b": 255, "name": "Blue"}
        ]
        for color in colors:
            print(f"    Testing color: {color['name']}")
            json_payload = {"seg": [{"col": [[color["r"], color["g"], color["b"]]]}]}
            print(f"    JSON payload being sent: {json_payload}")
            self.led_controller.set_color(r=color["r"], g=color["g"], b=color["b"])
            if not self.ip_address:
                self.assertEqual(self.led_controller.strip.setPixelColor.call_count, 50)  # Called for each LED
                self.led_controller.strip.setPixelColor.assert_any_call(
                    0, self.led_controller.Color(color["r"], color["g"], color["b"])
                )  # Verify color
                self.led_controller.strip.show.assert_called_once()
                self.led_controller.strip.reset_mock()  # Reset mock for the next color
            else:
                print(f"    Set color command sent to WLED device for color: {color['name']}.")
                print(f"        Expected behavior: All LEDs should display the color {color['name']}.")
            time.sleep(self.delay_between_tests)

    def test_set_brightness(self):
        # Test updating the brightness
        print("Running test: test_set_brightness")

        # Set brightness to 40
        brightness_value = 40
        json_payload = {"bri": brightness_value}
        print(f"    JSON payload being sent: {json_payload}")
        self.led_controller.set_brightness(brightness_value)  # Explicitly set brightness
        if not self.ip_address:
            self.led_controller.strip.setBrightness.assert_called_once_with(brightness_value)  # Ensure correct call
            self.led_controller.strip.show.assert_called_once()
        else:
            print(f"    Set brightness command sent to WLED device for brightness: {brightness_value}.")

        time.sleep(self.delay_between_tests)

        # Set brightness to 200
        brightness_value = 200
        json_payload = {"bri": brightness_value}
        print(f"    JSON payload being sent: {json_payload}")
        self.led_controller.set_brightness(brightness_value)  # Explicitly set brightness
        if not self.ip_address:
            self.led_controller.strip.setBrightness.assert_called_with(brightness_value)  # Ensure correct call
            self.led_controller.strip.show.assert_called()
        else:
            print(f"    Set brightness command sent to WLED device for brightness: {brightness_value}.")

    def test_turn_off(self):
        # Test turning off all LEDs
        print("Running test: test_turn_off")
        json_payload = {"on": False}
        print(f"    JSON payload being sent: {json_payload}")
        self.led_controller.turn_off()
        if not self.ip_address:
            # Assertions for mocked strip
            self.assertEqual(self.led_controller.strip.setPixelColor.call_count, 50)  # Called for each LED
            self.led_controller.strip.setPixelColor.assert_any_call(0, 0)  # Ensure LEDs are turned off
            self.led_controller.strip.show.assert_called_once()
        else:
            print("    Turn off command sent to WLED device.")

    def test_turn_on(self):
        # Test turning on the LEDs
        print("Running test: test_turn_on")
        json_payload = {"on": True}
        print(f"    JSON payload being sent: {json_payload}")
        self.led_controller.turn_on()
        print("    Turn on command sent to WLED device.")
        # Add assertions to verify behavior

    def test_all_effects(self):
        # Test all effects in the effects list
        print("Running test: test_all_effects")
        for effect in effects_list:
            effect_name = effect["Effect"]
            fx_id = int(effect["ID"])
            parameters = effect.get("parameters", {})
            print(f"    Testing effect: {effect_name} with fx ID: {fx_id} and parameters: {parameters}")

            # Construct the JSON payload for the effect
            payload = {"seg": [{"fx": fx_id}]}
            if "speed" in parameters:
                payload["seg"][0]["sx"] = parameters["speed"]
            if "intensity" in parameters:
                payload["seg"][0]["ix"] = parameters["intensity"]
            if "color" in parameters:
                payload["seg"][0]["col"] = [[int(parameters["color"][1:3], 16),  # Red
                                             int(parameters["color"][3:5], 16),  # Green
                                             int(parameters["color"][5:7], 16)]]  # Blue

            # Log additional parameters if present
            for key, value in parameters.items():
                if key not in ["speed", "intensity", "color"]:
                    print(f"        Additional parameter: {key} = {value}")

            print(f"    JSON payload being sent: {payload}")

            # Test the effect
            if not self.ip_address:
                # Mock the effect if no IP address is provided
                self.led_controller.effects = {effect_name: MagicMock()}
                self.led_controller.run_effect(effect_name)
                self.led_controller.effects[effect_name].assert_called_once()
                print(f"    Mocked effect '{effect_name}' should now be running.")
            else:
                # Send the effect to the WLED device
                self.led_controller.set_effect(fx_id, **{k: v for k, v in parameters.items() if k in ["speed", "intensity", "color"]})
                print(f"    Effect '{effect_name}' command sent to WLED device.")
                print(f"        Expected behavior: LEDs should display the '{effect_name}' effect.")

            time.sleep(self.delay_between_tests)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run LEDController tests.")
    parser.add_argument("ip_address", nargs="?", help="IP address of the WLED device (optional)", default=None)
    parser.add_argument("--delay", type=int, default=3, help="Delay between tests in seconds (default: 3)")
    args, remaining_args = parser.parse_known_args()  # Parse arguments and leave remaining for unittest

    # Pass the IP address and delay to the test class
    TestLEDController.ip_address = args.ip_address
    TestLEDController.delay_between_tests = args.delay

    # Run unittest with remaining arguments
    unittest.main(argv=[__file__] + remaining_args)
