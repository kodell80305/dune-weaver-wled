import time
import argparse
#from flask import Flask, send_from_directory, request, jsonify
import os
import math
import threading
from queue import Queue
from rpi_ws281x import *
import config
from wled_web_server import start_flask
from wled_rpi import init_rpi, run_rpi_app

init_rpi()
start_flask()
run_rpi_app()
