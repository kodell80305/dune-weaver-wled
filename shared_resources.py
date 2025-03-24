from flask import Flask
from queue import Queue

# Initialize shared resources
app = Flask(__name__)
myQueue = Queue()
