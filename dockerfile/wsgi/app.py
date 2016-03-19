#!/usr/bin/python
#app.py
#from flask import Flask
#app = Flask(__name__)

#@app.route('/')
#def hello():
#    return '<h1>Hello everyone again in H1 or maybe not!!</h1>'
from flask import Flask
from flask import request, render_template, redirect, url_for
#from flask.ext.sqlalchemy import SQLAlchemy
#from config import BaseConfig
#JM added imports:
import re
import sys
#import json
from pymongo import MongoClient
import requests

import logging
import os

from flask import json
#from flask import (Flask, request, json)

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_formatter = logging.Formatter('[%(asctime)s] [%(module)s:%(lineno)d] [%(levelname)s] %(message)s')
stream_handler.setFormatter(stream_formatter)
app.logger.addHandler(stream_handler)

if ('DB_PORT_27017_TCP_ADDR' in os.environ):
	host = os.environ['DB_PORT_27017_TCP_ADDR']
else:
	host = '192.168.99.100'

client = MongoClient(host, 27017)
db = client.movies  # db = client.primer


@app.route('/hello', methods=["GET"])
def route_hello():
    if 'name' not in request.args:
        app.logger.warn('Missing name parameter')
        return "Missing 1 name parameter", 400
    return "Hi %s" % request.args['name'], 200


@app.route('/hello/<name>', methods=["GET"])
def route_hello_name(name):
    return "Hi %s" % name, 200

@app.route('/postexample', methods=["POST"])
def route_postexample():
    app.logger.warn('/postexample url')
    text1 = request.form['text']
#    post = Post(text)
    app.logger.warn(text1)
#    app.logger.warn(Post)
    #posts=json.dumps({'text':'1234'})
    posts = getmatch(text1)
    #posts = []
    #posts.append(moviejsonresponse)
    #posts={"text":text1}
    app.logger.warn(posts)
    return render_template('index.html', posts=posts)
    #return json.dumps({'id':'1234'}), 201, {'Content-Type': 'application/json'}


@app.route('/postexample', methods=["GET"])
def route_getexample():
    app.logger.warn('/postexample GET url')
#    text = request.form['text']
#    post = Post(text)
#    app.logger.warn(text)
#    app.logger.warn(Post)
    posts=json.dumps({'text':'1234'})
    app.logger.warn(posts)
    return render_template('index.html',posts=posts)
    #return json.dumps({'id':'1234'}), 201, {'Content-Type': 'application/json'}
#'''
'''
def app(environ, start_response):
      data = b"Hello, World!\n"
      start_response("200 OK", [
          ("Content-Type", "text/plain"),
          ("Content-Length", str(len(data)))
      ])
      return iter([data])
'''
def getmatch(film):
#    path = "./Movefile"
#    result = []
#    for path, dirs, files in os.walk(path):
#        for f in files:
#            if re.search('.py', f[len(f)-3:]):
    #            print str(path)+'/'+str(f)
#                result.append(str(path)+'/'+str(f))
                #Genre, rating, description, score
                #path to copy.
#    scp <source> <destination>

    # Search MongoDB first for match. If none, get info from omdbapi and then
    # add to MongoDB.
    _items = db.movies.find()
    movielist = []
    for item in _items:
        if re.search(film, item['Title']):
            movielist.append(item)
            app.logger.warn("Match in MongoDB found: "+str(item))
    if movielist:
        return movielist

    #Else, dealing with situation that no Movie match was found:

    baseUrl = "http://www.omdbapi.com/" #"?t=Frozen&y=&plot=short&r=json
#    film = "Frozen"
    try:
        r = requests.get(baseUrl + "?t="+film+"&y=&plot=short&r=json") #, auth=(username,token))
        app.logger.warn(r.status_code)
        moviejson = r.json() #capture json data
    except requests.exceptions.RequestException as e:
        app.logger.warn(e)
        sys.exit(1)

    if "imdbRating" in moviejson:
        app.logger.warn(str(moviejson['imdbRating']))

    #You can also access databases using dictionary-style access, which removes
    #Python-specific naming restrictions, as in the following:
    #db = client['primer']
#    coll = db.dataset

#Issue with next line:
    resultdb = db.movies.insert_one(moviejson)
    app.logger.warn("Adding New Film "+str(resultdb.inserted_id))
#    resultdb = db.users.insert(transfer)
#    resultdb.inserted_id
#    print resultdb.inserted_id

#        print time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(epochtime))
#        sys.exit(0)
#    print "Reading from Mongo: "+str(db.users.find())
#    cursor = db.users.find()
#Iterate the cursor and print the documents.

#    for film in cursor:
#        app.logger.warn("file"+str(film))


#
#    print "Reading from Mongo: "+str(db.users.find().pretty())
######################################################################
#    for r in result:
#         app.logger.warn('Path = '+ getlink(r,"path")+', File Name = '+ getlink(r,"filename"))
    #print result
    movielist.append(moviejson)
    return movielist  # str(db.users.find().pretty())

def getlink(full_path_file_name,return_type):

    path_file_name = full_path_file_name.split('/')

    if len(path_file_name) > 1:
        filename = path_file_name[len(path_file_name)-1]

        path = path_file_name[0]
        for p in range(1, len(path_file_name)-1):
            path = path +'/' + path_file_name[p]
    else:
        filename = path_file_name[0]
        path = ''

    if return_type == "filename":
        return filename
    else:
        return path
