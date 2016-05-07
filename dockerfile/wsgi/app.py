#!/usr/bin/python
# app.py
from flask import Flask
from flask import request, render_template
# , redirect, url_for, send_from_directory
import re
#import yaml
import sys
# import json
from pymongo import MongoClient
import urlparse
import requests
import logging
import os
from flask import json

# Added 2-5-2016 static...
app = Flask(__name__)

app.logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_formatter = logging.Formatter('[%(asctime)s] [%(module)s:%(lineno)d][%(levelname)s] %(message)s')
stream_handler.setFormatter(stream_formatter)
app.logger.addHandler(stream_handler)

#config = yaml.safe_load(open("config.yml"))

if ('DB_PORT_27017_TCP_ADDR' in os.environ):
    host = os.environ['DB_PORT_27017_TCP_ADDR']
else:
    host = '192.168.99.100'

client = MongoClient(host, 27017)
db = client.movies  # db = client.primer


@app.route('/movieinfo', methods=["POST"])
def route_postexample():
    app.logger.warn('/movieinfo POST url')
    text1 = request.form['text']
    app.logger.warn(text1)
    posts = getmatch(text1)
    # app.logger.warn(posts)
    return render_template('index.html', posts=posts)


@app.route('/movieinfo/all', methods=["GET"])
def route_getmovieinfoall():
    app.logger.warn('/movieinfo/all GET url')
    posts = db.movies.find()
    return render_template('movieinfoall.html', posts=posts)


@app.route('/movieinfo/imdb/<rating>', methods=["GET"])
def route_getmovieimdb(rating):
    app.logger.warn('/movieinfo/imdb/<rating> GET url')
    imdbrating = rating  # float(rating)
    posts = db.movies.find({"imdbRating": {"$gte": imdbrating, "$ne": "N/A"}})
    return render_template('movieinfoall.html', posts=posts)


@app.route('/movieinfo', methods=["GET"])
def route_getexample():
    app.logger.warn('/movieinfo GET url')
    posts = json.dumps({'text': '1234'})
    # app.logger.warn(posts)
    return render_template('index.html')


@app.route('/options', methods=["GET"])
def route_getoptions():
    app.logger.warn('/options GET url')
    genres, directors = getGenre()
    url = request.values  # Get value from GET(/POST) request
    posts = {"Title": "X-men"}
    app.logger.info(url)
    if len(url) == 1:
        query = {}
        value = url.values()  # Get values from dict
        query['Genre'] = value[0]
        posts = db.movies.find(query)
        app.logger.info(value[0])
    else:
        query = []
        for u in url:
            querydict = {}
            querydict['Genre'] = url[u]
            query.append(querydict)
        app.logger.info(query)
        posts = db.movies.find({'$or': query})
        app.logger.info(posts)
    # query = {"Genre": "Adventure"}
    posts = db.movies.find({"Genre": "Adventure"})
    for f in posts:
        app.logger.info(f)
    # result = db.test.delete_one({'x': 1})

    # app.logger.warn(posts)
    # directors = getDirector()
    return render_template('displayOptions.html', genres=genres, directors=directors, posts=posts)


@app.route('/options', methods=["POST"])
def route_postoptions():
    app.logger.warn('/options POST url')
    text1 = request.form['0']
    app.logger.info(text1)
    genres, directors = getGenre()
    # directors = getDirector()
    # bb
    return render_template('displayOptions.html', genres=genres, directors=directors)


@app.route('/', methods=["GET"])
def route_getbase():
    app.logger.warn('/ GET url')
    return render_template('home.html')


def getGenre():
    alltype = db.movies.find()
    genres = []
    directors = []

    for film in alltype:
        if "Genre" in film:
            genrefile = film['Genre'].split(",")
            # app.logger.warn(genrefile)
            for i in genrefile:
                # app.logger.info(i.strip())
                genres.append(i.strip())

        if "Director" in film:
            dirfile = film['Director'].split(",")
            # app.logger.warn(dirfile)
            for i in dirfile:
                # app.logger.info(i.strip())
                directors.append(i.strip())

    # app.logger.info("Final")
    gen = list(set(genres))
    dirs = list(set(directors))
    # app.logger.info(gen)
    # app.logger.info(dirs)
    return gen, dirs


def getmatch(film):
    # items = db.movies.find()
    movielist = []
    items = db.movies.find({"Title": film})
    # app.logger.warn("Match in MongoDB found: "+str(items))
    for item in items:
        if "Title" in item:
            app.logger.warn("Match in MongoDB found: "+str(item))
            movielist.append(item)
    if movielist:
        return movielist

    # Else, dealing with situation that no Movie match was found:
    baseUrl = "http://www.omdbapi.com/"  # "?t=Frozen&y=&plot=short&r=json
    # film = "Frozen"
    try:
        r = requests.get(baseUrl + "?t="+film+"&y=&plot=long&r=json")
        app.logger.warn(r.status_code)
        moviejson = r.json()
    except requests.exceptions.RequestException as e:
        app.logger.warn(e)
        sys.exit(1)

    app.logger.warn(moviejson)
    if "Poster" in moviejson:
        app.logger.warn(moviejson['Poster'])
        image = requests.get(moviejson['Poster'])
        poster = str(moviejson['Poster'])
        index = poster.rfind('.')
        ext = poster[index + 1:]
        name = str(moviejson['Title'])
        # Get Poster Image content
        # try:
        #    with open(name + '.' + ext, "wb") as code1:
        #        app.logger.warn(image.content)
        #        code1.write(image.content)
        #        code1.close()
        # except:
        #    pass

    app.logger.warn(moviejson)
    app.logger.warn("Next")
    # if "imdbRating" in moviejson:
    #    app.logger.warn(str(moviejson['imdbRating']))
    #    app.logger.warn(str(moviejson))
    # if "Poster" in moviejson:
    #    app.logger.warn(moviejson['Poster'])
    #    image = requests.get(moviejson['Poster'])
    #    poster = str(moviejson['Poster'])
    #    index = poster.rfind('.')
    #    ext = poster[index + 1:]
    #    # name = str(moviejson.Title)

    #    try:
    #        with open(film + '.' + ext, "wb") as code1:
    #            app.logger.warn(image.content)
    #            code1.write(image.content)
    #        code1.close()
    #    except:
    #        pass
    resultdb = db.movies.insert_one(moviejson)
    app.logger.warn("Adding New Film "+str(resultdb.inserted_id))
    # scanforfilms()
    movielist.append(moviejson)
    return movielist  # str(db.users.find().pretty())


def getlink(full_path_file_name, return_type):

    path_file_name = full_path_file_name.split('/')

    if len(path_file_name) > 1:
        filename = path_file_name[len(path_file_name)-1]

        path = path_file_name[0]
        for p in range(1, len(path_file_name)-1):
            path = path + '/' + path_file_name[p]
    else:
        filename = path_file_name[0]
        path = ''

    if return_type == "filename":
        return filename
    else:
        return path
