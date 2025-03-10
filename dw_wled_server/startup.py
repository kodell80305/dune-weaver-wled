import time
import argparse
#from flask import Flask, send_from_directory, request, jsonify
import os
import math
import threading
from queue import Queue
import config

from wled_web_server import start_flask
if config.simulate:
    from wled_rpi_sim import init_rpi, run_rpi_app
else:
    from wled_rpi import init_rpi, run_rpi_app

#The order seems to be impportant here - I'm not sure why we need to start the pixel strip before starting the flask server, but it seems to work
#The run_rpi_app() function is the main loop that runs the effects.  It will run until the program is terminated.  The flask server runs in a separate thread
#and will continue to run until the program is terminated.  The flask server is used to send commands to the rpi app to change the effect or the playlist
#The rpi app will run the effect until it is interrupted by a command from the flask server.  
init_rpi()
start_flask()
run_rpi_app()
