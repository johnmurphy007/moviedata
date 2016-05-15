#!/usr/bin/python
# import parse_md
"""
Program: .py
Rev: 1.0.0
Author: John Murphy
Date:
Developed on Python 2.7.10
"""
import os
import re
import sys
#
# import json
from pymongo import MongoClient
import requests
import logging
from flask import json
from flask import Flask
from flask import request, render_template, redirect, url_for, send_from_directory

# Setting static_folder=None disables built-in static handler.
app = Flask(__name__)  # static_url_path='')
app.logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_formatter = logging.Formatter('[%(asctime)s] [%(module)s:%(lineno)d] [%(levelname)s] %(message)s')
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


def searchformovies(path):
    # avi, mov, mp4, .mkv, .vob, .ogg, .wmv, .mp2
    # if .vob: folder will be VIDEO_TS (need to filter back for this)
    filmformats = ['.avi', '.mov', '.mp4', '.mkv', '.ogg', '.wmv', '.mp2']
    filmformatvob = '.VOB'
    remove = '/Volumes'
    prepend = '/share'
    result = []
    for path, dirs, files in os.walk(path):
        if files:
            for indfile in files:
                for formattype in filmformats:
                    if re.search(formattype, indfile):
                        naspath = prepend + path[len(remove):]
                        result.append(naspath)
                if re.search(filmformatvob, indfile):
                    if path.find("VIDEO_TS"):
                        index = path.rfind('/VIDEO_TS')
                    else:
                        index = path.rfind('/')
                    naspath = prepend + path[len(remove):index]
                    result.append(naspath)
    scannedmovies = set(result)
    return scannedmovies


def processdir(dirname):
    index = dirname.rfind('/')
    dirname = dirname[index + 1:].strip()
    name = ""
    year = ''
    if len(dirname) > 6:
        if dirname[len(dirname) - 1] == ")":
            if dirname[len(dirname) - 6] == "(":
                year = dirname[len(dirname)-5:len(dirname) - 1]
                name = dirname[:len(dirname) - 6]
                name = name.strip()
        elif dirname[len(dirname)-5] == " ":
            try:
                year = int(dirname[len(dirname)-4:])
                name = dirname[:len(dirname) - 5]
                name = name.strip()
                if name[len(name) - 1] == "-":
                    name = name[:len(name-1)].strip()
            except:
                name = dirname
                pass
        else:
            name = dirname
    return name, year


def getfilmdata(film, year, fullpathtomovie):
    # Else, dealing with situation that no Movie match was found:
    baseUrl = "http://www.omdbapi.com/"  # "?t=Frozen&y=&plot=short&r=json
    # film = "Frozen"
    try:
        if year:
            year = str(year)
        else:
            year = ''
    except:
        year = ''

    try:
        r = requests.get(baseUrl + "?t="+film+"&y="+year+"&plot=full&r=json")
        app.logger.info(r.status_code)
        moviejson = r.json()  # capture json data
    except requests.exceptions.RequestException as e:
        app.logger.warn(e)

    if r.status_code == 200:
        app.logger.info("Match found on omdbapi")
        moviejson['naslocation'] = fullpathtomovie
        resultdb = db.movies.insert_one(moviejson)
        app.logger.info("Adding New Film "+str(resultdb.inserted_id))
        return None
    return fullpathtomovie


def main():

    configjson = readConfig()
    path_to_search = configjson['path_to_search']
    app.logger.info(path_to_search)

    movies = searchformovies(path_to_search)
    #app.logger.info(movies)

    movielisterror = []
    for movie in movies:
        name, year = processdir(movie)
        app.logger.info(name)
        app.logger.info(year)
        # Check for match in MongoDB:
        if year:
            _items = db.movies.find_one({"Title": name, "Year": year})
        else:
            _items = db.movies.find_one({"Title": name})

#        db.movies.delete_one({"Title": name})
        if _items is None:
            newfilmresult = getfilmdata(name, year, movie)
            if newfilmresult is not None:
                movielisterror.append(newfilmresult)
        else:
            app.logger.info("Film in database already")

    if movielisterror:
        try:
            with open("errorfile.txt", 'w') as outfile:
                outfile.writelines(errorfile)
            outfile.close()
        except EnvironmentError:
            app.logger.warn('error writing to file')
    return


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


if __name__ == '__main__':
    main()
