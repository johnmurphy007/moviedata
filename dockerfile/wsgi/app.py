#!/usr/bin/python
# app.py
from flask import Flask
from flask import request, render_template
# , redirect, url_for, send_from_directory
import re
import sys
from pymongo import MongoClient
import urlparse
import requests
import logging
import os
from flask import json

app = Flask(__name__)

app.logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_formatter = logging.Formatter('[%(asctime)s] [%(module)s:%(lineno)d][%(levelname)s] %(message)s')
stream_handler.setFormatter(stream_formatter)
app.logger.addHandler(stream_handler)

# global variable
config_file = "config.json"


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
    url = request.values  # Get value from GET(/POST) request

    if 'moviename' in url:
        # Get matching entries
        search = url['moviename']
        posts = db.movies.find({'Title': {'$regex': search, "$options": "$i"}})
    else:
        # Get all entries
        posts = db.movies.find()

    return render_template('movieinfoall.html', posts=posts)


@app.route('/movieinfo/genre', methods=["GET"])
def route_getmoviegenre():
    app.logger.warn('/movieinfo/genre GET url')
    url = request.values  # Get value from GET(/POST) request

    if url.keys():  # Get keys of url and add them to array
        genrelist = url.keys()
        app.logger.info(genrelist)
        search = '|'.join(genrelist)
    app.logger.info(search)
    posts = db.movies.find({'Genre': {'$regex': search, "$options": "$i"}})

    return render_template('movieinfogenre.html', posts=posts)
    # posts = db.movies.find({'Title': '/.*Sup.*/'})
    # posts = db.movies.find({"Genre": {"$elemMatch": {"$eq": "Action", "$eq": "Comedy"}}})
    # posts = db.movies.find({"$or": [{"Genre": {"$in": genrelist}}]})
    # posts = db.movies.find({"$where": 'function() {var genre = this.Genre.split(","); for (i = 0; i < genre.length; i++) { if (genre == "Action") return this.genre; } }'})
    # db.inventory.find( { $or: [ { quantity: { $lt: 20 } }, { price: 10 } ] })
    # posts = db.movies.find({"Genre": "Action, Adventure, Drama"})
    # posts = db.movies.find({"Genre": { $elemMatch: {"$in": genrelist}}})
    # posts = db.movies.find({"Genre": {"$elemMatch": {"Genre": genrelist}}})
    # posts = db.movies.find()
    # posts = db.movies.find({"Genre": { "$in": genrelist}})
    # posts = db.movies.find({"Genre": { "$in": genrelist}})
    # posts = db.movies.find({"Genre": { $elemMatch: {"$in": genrelist}}})
    # posts = db.movies.find()


@app.route('/movieinfo/director', methods=["GET"])
def route_getmoviedirector():
    app.logger.warn('/movieinfo/director GET url')

    url = request.values  # Get value from GET(/POST) request

    if 'director' in url:
        # Get matching entries
        search = url['director']
        # search.replace('+', ' ')
        app.logger.info(search)
        posts = db.movies.find({'Director': {'$regex': search, "$options": "$i"}})
    else:
        # Get all entries
        posts = db.movies.find()

    return render_template('movieinfoall.html', posts=posts)


# @app.route('/movieinfo/imdb/<rating>', methods=["GET"])
# def route_getmovieimdb(rating):
@app.route('/movieinfo/imdb', methods=["GET"])
def route_getmovieimdb():
    app.logger.warn('/movieinfo/imdb GET url')
    # imdbrating = rating  # float(rating)
    url = request.values  # Get value from GET(/POST) request
    # ?optsortby=asc&optimdbrating=9.5
    if 'sortby' in url:
        if url['sortby'] == "asc":
            operator = "$gte"
        elif url['sortby'] == "desc":
            operator = "$lte"
        else:
            operator = "$eq"

    if 'imdbrating' in url:
        imdbrating = url['imdbrating']

    if 'optsortby' in url:
        opt_operator = ''
        if url['optsortby'] == "asc":
            opt_operator = "$gte"
        elif url['optsortby'] == "desc":
            opt_operator = "$lte"
        elif url['optsortby'] == "equal":
            opt_operator = "$eq"
        if opt_operator:
            app.logger.warn(opt_operator)
        else:
            app.logger.warn("Not defined!")

    if 'optimdbrating' in url:
        opt_imdbrating = url['optimdbrating']
        app.logger.warn(opt_imdbrating)

    if opt_operator and opt_imdbrating:
        posts = db.movies.find({"imdbRating": {operator: imdbrating, "$ne": "N/A", opt_operator: opt_imdbrating}})
    else:
        posts = db.movies.find({"imdbRating": {operator: imdbrating, "$ne": "N/A"}})

    return render_template('movieinfoall.html', posts=posts)


@app.route('/movieinfo', methods=["GET"])
def route_getexample():
    app.logger.warn('/movieinfo GET url')

    url = request.values  # Get value from GET(/POST) request
    posts = json.dumps({'text': '1234'})
    if 'moviename' in url:
        posts = db.movies.find({"Title": url['moviename']})
    return render_template('index.html', posts=posts)


@app.route('/options', methods=["GET"])
def route_getoptions():
    app.logger.warn('/options GET url')
    genres, directors, posts = getBasicMetadata()
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
    genres, directors, films = getBasicMetadata()
    posts = db.movies.find()
    return render_template('home.html', genres=genres, directors=directors, posts=films)


def getBasicMetadata():
    alltype = db.movies.find()
    genres = []
    directors = []
    films = []

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

        if "Title" in film:
            films.append(film['Title'])

    # app.logger.info("Final")
    gen = list(set(genres))
    dirs = list(set(directors))
    # app.logger.info(gen)
    # app.logger.info(dirs)
    return gen, dirs, list(set(films))


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


def writeConfig(json_to_write):
    with open(config_file, mode='w') as out:
        res = json.dump(
            json_to_write,
            out,
            sort_keys=True,
            indent=4,
            separators=(
                ',',
                ': '))
    out.close()
    return


def readConfig():
    # config_file = "config.json"
    with open(config_file, mode='r') as out:
        input_json = json.load(out)
    out.close()

    return input_json
