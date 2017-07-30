#!/usr/bin/python
# app.py
from flask import Flask
from flask import request, render_template
import re
import sys
import pymongo
from pymongo import MongoClient
import urlparse
import requests
import logging
import os
from flask import json
from bson.objectid import ObjectId
import ast  # to convert unicode to dict
#import scanForFilms
# coding: utf-8
import paho.mqtt.client as mqtt

#mqtt info:
def mqtt_publish(topic, payload):
    host_mqtt = '192.168.1.71'
    port_mqtt = 1883  # SSL/TLS = 8883
    mqttc = mqtt.Client('python_pub')
    mqttc.connect(host_mqtt, port_mqtt)
    mqttc.publish(topic, payload)
    mqttc.loop(2) #timeout = 2s

    return


app = Flask(__name__)

app.logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_formatter = logging.Formatter('[%(asctime)s] [%(module)s:%(lineno)d][%(levelname)s] %(message)s')
stream_handler.setFormatter(stream_formatter)
app.logger.addHandler(stream_handler)

# global variable (not used at present)
config_file = "config.json"


if ('DB_PORT_27017_TCP_ADDR' in os.environ):
    host = os.environ['DB_PORT_27017_TCP_ADDR']
else:
    host = '192.168.99.100'

client = MongoClient(host, 27017)
db = client.movies  # db = client.primer


@app.route('/', methods=["GET"])
def route_getbase():
    app.logger.info('/ GET url')
    genres, directors, films = getBasicMetadata()
    posts = db.movies.find()
    return render_template('home.html', genres=genres, directors=directors, posts=films)


# Work in Progess - requires wsgi Container to have visibility on folders that videos are in.
@app.route('/movieinfo/scan', methods=["GET"])
def route_getmoviescan():
    app.logger.info('/movieinfo/scan GET url')
    # Call scanForFilms to scan/add movies to mongodB:
    mqtt_topic = 'hello/world'
    mqtt_payload = 'scanForFilms'
    mqtt_publish(mqtt_topic, mqtt_payload)
    # Insert mqtt call to trigger python call:
    #scanForFilms.main()

    page = 1
    pagesize = 25
    skip = page * pagesize
    posts = db.movies.find().sort(('Title'), pymongo.ASCENDING).limit(pagesize).skip(skip)

    return render_template('movieinfoall.html', posts=posts, page=page)


# @app.route('/movieinfo/delete/', methods=["GET"])
# def route_getmoviedelete():
#     app.logger.info('/movieinfo/delete GET url')
#     empty = db.movies.remove({"Title":""})
#     app.logger.info("deleted an item?")
#
#     page = 1
#     pagesize = 25
#     skip = page * pagesize
#     posts = db.movies.find().sort(('Title'), pymongo.ASCENDING).limit(pagesize).skip(skip)
#
#     return render_template('movieinfoall.html', posts=posts, page=page)


@app.route('/movieinfo/delete/<imdbid>/<page>', methods=["GET"])
def route_getmoviedeleteimdbid(imdbid, page):
    app.logger.info('/movieinfo/delete/<imdbid>/<page> GET url')

    if imdbid:
        app.logger.info(imdbid)
        # Remove record:
        post = db.movies.delete_one({'_id': ObjectId(imdbid)})

    if page:
        page = int(page)
    else:
        page = 1

    pagesize = 25
    skip = page * pagesize
    posts = db.movies.find().sort(('Title'), pymongo.ASCENDING).limit(pagesize).skip(skip)

    return render_template('movieinfoall.html', posts=posts, page=page)


@app.route('/movieinfo/all', methods=["GET"])
def route_getmovieinfoall():
    app.logger.info('/movieinfo/all GET url')
    url = request.values  # Get value from GET(/POST) request
    page = 1
    if 'page' in url:
        page = int(url['page'])

    pagesize = 25

    skip = page * pagesize
    app.logger.info(skip)
    posts = db.movies.find().sort(('Title'), pymongo.ASCENDING).limit(pagesize).skip(skip)

    return render_template('movieinfoall.html', posts=posts, page=page)


@app.route('/movieinfo/film', methods=["GET"])
def route_getmovieinfofilm():
    app.logger.info('/movieinfo/film GET url')
    url = request.values  # Get value from GET(/POST) request

    if 'moviename' in url:
        search = url['moviename']
        # Get matching entries
        posts = db.movies.find({'Title': {'$regex': search, "$options": "$i"}}).sort(('Title'), pymongo.DESCENDING)
    else:
        # Get all entries
        posts = db.movies.find().sort(('Title'), pymongo.DESCENDING)

    return render_template('movieinfofilm.html', posts=posts)


@app.route('/movieinfo/genre', methods=["GET"])
def route_getmoviegenre():
    app.logger.info('/movieinfo/genre GET url')
    url = request.values  # Get value from GET(/POST) request
    genres, directors, posts = getBasicMetadata()

    if url.keys():  # Get keys of url and add them to array
        genrelist = url.keys()
        app.logger.info(genrelist)
        search = '|'.join(genrelist)
        app.logger.info(search)
        posts = db.movies.find({'Genre': {'$regex': search, "$options": "$i"}}).sort(('imdbRating'), pymongo.DESCENDING)

    return render_template('movieinfogenre.html', posts=posts, genres=genres)


@app.route('/movieinfo/director', methods=["GET"])
def route_getmoviedirector():
    app.logger.info('/movieinfo/director GET url')

    url = request.values  # Get value from GET(/POST) request
    genres, directors, posts = getBasicMetadata()
    if 'director' in url:
        # Get matching entries
        search = url['director']
        app.logger.info(search)
        posts = db.movies.find({'Director': {'$regex': search, "$options": "$i"}}).sort(('Title'), pymongo.DESCENDING)
    else:
        # Get all entries
        posts = db.movies.find().sort(('Title'), pymongo.DESCENDING)

    return render_template('movieinfodirector.html', posts=posts, directors=directors)


@app.route('/movieinfo/imdb', methods=["GET"])
def route_getmovieimdb():
    app.logger.info('/movieinfo/imdb GET url')
    url = request.values  # Get value from GET(/POST) request

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
            app.logger.info(opt_operator)
        else:
            app.logger.warn("Not defined!")

    if 'optimdbrating' in url:
        opt_imdbrating = url['optimdbrating']
        app.logger.info(opt_imdbrating)

    if 'sort' in url:
        sort = url['sort']
        app.logger.info(sort)
    if opt_operator and opt_imdbrating:
        # posts = db.movies.find({"imdbRating": {operator: imdbrating, "$ne": "N/A", opt_operator: opt_imdbrating}}).sort(('imdbRating'), pymongo.DESCENDING).limit(pagesize).skip(page*pagesize)
        if sort == "DESCENDING":
            posts = db.movies.find({"imdbRating": {operator: imdbrating, "$ne": "N/A", opt_operator: opt_imdbrating}}).sort(('imdbRating'), pymongo.DESCENDING)
        else:
            posts = db.movies.find({"imdbRating": {operator: imdbrating, "$ne": "N/A", opt_operator: opt_imdbrating}}).sort(('imdbRating'), pymongo.ASCENDING)

    else:
        if sort == "DESCENDING":
        # posts = db.movies.find({"imdbRating": {operator: imdbrating, "$ne": "N/A"}}).sort(('imdbRating'), pymongo.DESCENDING).limit(pagesize).skip(page*pagesize)
            posts = db.movies.find({"imdbRating": {operator: imdbrating, "$ne": "N/A"}}).sort(('imdbRating'), pymongo.DESCENDING)
        else:
            posts = db.movies.find({"imdbRating": {operator: imdbrating, "$ne": "N/A"}}).sort(('imdbRating'), pymongo.ASCENDING)

    return render_template('movieinfoimdb.html', posts=posts)


@app.route('/movieinfo', methods=["GET"])
def route_getexample():
    app.logger.info('/movieinfo GET url')

    url = request.values  # Get value from GET(/POST) request
    app.logger.info(url)

    if 'moviename' in url:
        posts = db.movies.find({"Title": url['moviename']}).sort(('Title'), pymongo.DESCENDING)
        found = posts.count()
        return render_template('index.html', posts=posts, found=found)

    if url:
        for i in url:
            temp = url[i]  # url[i] is unicode.
            # Strip '[' & ']' from temp, use ast to convert unicode dict string to real dict.
            moviejson = ast.literal_eval(temp[1:len(temp)-1])
            app.logger.info(type(moviejson))
            app.logger.info(moviejson)
            posts = db.movies.insert_one(moviejson)
            posts = db.movies.find({"Title": moviejson['Title']})
            found = 1
            return render_template('index.html', posts=posts, found=found)

    posts = json.dumps({'text': '1234'})
    found = 0
    return render_template('index.html', posts=posts, found=found)


@app.route('/movieinfo', methods=["POST"])
def route_postexample():
    app.logger.info('/movieinfo POST url')
    httpsearch = request.form['text']
    app.logger.info(httpsearch)
    posts = db.movies.find({"Title": httpsearch})
    app.logger.info(posts.count())
    if posts.count() > 0:
        found = 1
        return render_template('index.html', posts=posts, found=found)
    else:
        posts = getmatch(httpsearch)
        if posts:
            found = "yes"
        else:
            posts = {"Title": "X-men"}  # Dummy data
            found = 0

        return render_template('index.html', posts=posts, found=found)


@app.route('/image', methods=["GET"])
def route_getimage():
    app.logger.info('/image GET url')
    genres, directors, films = getBasicMetadata()
    moviejson = db.movies.find({"Title": "Fargo"}).limit(1)
    app.logger.info(moviejson)
    getPoster(moviejson)
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
            for i in genrefile:
                genres.append(i.strip())

        if "Director" in film:
            dirfile = film['Director'].split(",")
            for i in dirfile:
                directors.append(i.strip())

        if "Title" in film:
            films.append(film['Title'])

    gen = list(set(genres))
    dirs = list(set(directors))

    return gen, dirs, list(set(films))


def getPoster(cursor):
    for moviejson in cursor:
        app.logger.info(moviejson)
        if "Poster" in moviejson:
           app.logger.info(moviejson['Poster'])
           image = requests.get(moviejson['Poster'])

           poster = str(moviejson['Poster'])
           index = poster.rfind('.')
           ext = poster[index + 1:]
           name = str(moviejson['Title'])

           try:
               with open(name + '.' + ext, "wb") as code1:
                   #app.logger.info(image.content)
                   code1.write(image.content)
               code1.close()
           except:
               pass
    return


def getmatch(film):

    movielist = []
    baseUrl = "http://www.omdbapi.com/"

    try:
        r = requests.get(baseUrl + "?t="+film+"&y=&plot=long&r=json")
        app.logger.info(r.status_code)
        moviejson = r.json()
    except requests.exceptions.RequestException as e:
        app.logger.warn(e)
        sys.exit(1)

    app.logger.info(moviejson)
    movielist.append(moviejson)
    return movielist  # str(db.users.find().pretty())






###########################################
# WIP Stuff
###########################################
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
    global config_file # = "config.json"
    with open(config_file, mode='r') as out:
        input_json = json.load(out)
    out.close()

    return input_json


@app.route('/options', methods=["GET"])
def route_getoptions():
    app.logger.info('/options GET url')
    genres, directors, posts = getBasicMetadata()
    url = request.values  # Get value from GET(/POST) request
    posts = {"Title": "X-men"}
    app.logger.info(url)
    if len(url) == 1:
        query = {}
        value = url.values()  # Get values from dict
        query['Genre'] = value[0]
        posts = db.movies.find(query).sort(('imdbRating'), pymongo.DESCENDING)
        app.logger.info(value[0])
    else:
        query = []
        for u in url:
            querydict = {}
            querydict['Genre'] = url[u]
            query.append(querydict)
        app.logger.info(query)
        posts = db.movies.find({'$or': query}).sort(('imdbRating'), pymongo.DESCENDING)
        app.logger.info(posts)

    page = 1
    if 'page' in url:
        page = int(url['page'])

    pagesize = 20
    if 'pagesize' in url:
        pagesize = str(url['pagesize'])
    #posts = db.movies.find({"Genre": "Adventure"})
    posts = db.movies.find().sort(('Title'), pymongo.DESCENDING).limit(pagesize).skip(page*pagesize)
    #for f in posts:
    #    app.logger.info(f)
    # result = db.test.delete_one({'x': 1})

    # directors = getDirector()
    return render_template('displayOptions.html', genres=genres, directors=directors, posts=posts, page=page, pagesize=pagesize)


@app.route('/options', methods=["POST"])
def route_postoptions():
    app.logger.info('/options POST url')
    text1 = request.form['0']
    app.logger.info(text1)
    genres, directors = getGenre()
    # directors = getDirector()
    # bb
    return render_template('displayOptions.html', genres=genres, directors=directors)

    # List of reference accesses via pymongo that I've tried:
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
    # resultdb = db.movies.insert_one(moviejson)
    # moviejson = db.movies.find({"Title": "Fargo"}).limit(1)\

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
