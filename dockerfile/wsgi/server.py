#!/usr/bin/python

import logging
import os

from flask import Flask
from flask import request
from flask import json
#from flask import (Flask, request, json)

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_formatter = logging.Formatter('[%(asctime)s] [%(module)s:%(lineno)d] [%(levelname)s] %(message)s')
stream_handler.setFormatter(stream_formatter)
app.logger.addHandler(stream_handler)

@app.route('/hello', methods=["GET"])
def route_hello():
    if 'name' not in request.args:
        app.logger.warn('Missing name parameter')
        return "Missing name parameter", 400
    return "Hi %s" % request.args['name'], 200


@app.route('/hello/<name>', methods=["GET"])
def route_hello_name(name):
    return "Hi %s" % name, 200

@app.route('/postexample', methods=["POST"])
def route_postexample():
    return json.dumps({'id':'1234'}), 201, {'Content-Type': 'application/json'}

if __name__ == "__main__":
    app.run(host='0.0.0.0')
'''
def app(environ, start_response):
      data = b"Hello, World!\n"
      start_response("200 OK", [
          ("Content-Type", "text/plain"),
          ("Content-Length", str(len(data)))
      ])
      return iter([data])
'''
