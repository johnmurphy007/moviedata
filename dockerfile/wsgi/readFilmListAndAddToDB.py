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
import time
from pymongo import MongoClient
import requests
import logging
from flask import json
from flask import Flask


# Setting static_folder=None disables built-in static handler.
app = Flask(__name__)  # static_url_path='')
app.logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_formatter = logging.Formatter('[%(asctime)s] [%(module)s:%(lineno)d] [%(levelname)s] %(message)s')
stream_handler.setFormatter(stream_formatter)
app.logger.addHandler(stream_handler)

# global variable
config_file = "config.json"
configjson = readConfig()

if ('DB_PORT_27017_TCP_ADDR' in os.environ):
    host = os.environ['DB_PORT_27017_TCP_ADDR']
else:
    host = configjson["db_host"]

client = MongoClient(host, 27017)
db = client.movies


def searchformovies(path1):
    '''
    Recursively search the folder location ('path1') for films that match
    the film formats as specified in the 'config.json' file.  The config.json
    uses a key:value pair, where:
        key = format of movie file
        value = if a value other than '/' is specified, then the path is
            truncated by this value.
            For example, VOB files typically are found in a subfolder called:
            "VIDEO_TS".  Want to get the name of the folder that this folder
            is contained in.  Specifying a key: value pair of
            "VOB": "/VIDEO_TS" will remove the /VIDEO_TS from the path.
    '''
    # avi, mov, mp4, .mkv, .vob, .ogg, .wmv, .mp2
    # if .vob: folder will be VIDEO_TS (need to filter back for this)
    films_to_search_for = configjson['movie_file_format']
    filmformats = films_to_search_for.keys()

    result = []
    app.logger.info("Search for Movies")
    app.logger.info(path1)
    for path, dirs, files in os.walk(path1):
        print path, dirs, files
        sys.exit(0)
        if files:
            for indfile in files:
                for formattype in filmformats:
                    if indfile.endswith("."+str(formattype)):
                        # next test is geared towards VOB files which are
                        # in a subfolder called VIDEO_TS
                        moviename = path.split("/")
                        if path.find(films_to_search_for[formattype]):
                            movie = moviename[len(moviename)-2]
                        else:
                            movie= moviename[len(moviename)-1]
                        result.append(movie)
    app.logger.info("Finished scanning")
    app.logger.info(result)

    scannedmovies = set(result)  # extract unique values
    return scannedmovies


def processdir(dirname):
    '''
    Process the 'dirname' for the name of the film and the year of the
    film (if it is there).  The method return the name and year of film.
    '''
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
    '''
    Get film metadata from omdbapi.com
    '''
    # Read config.py file
    apikey = configjson["apikey"]
    baseUrl = "http://www.omdbapi.com/?apikey=" + str(apikey)

    try:
        if year:
            year = str(year)
        else:
            year = ''
    except:
        year = ''

    try:
        r = requests.get(baseUrl + "&t="+film+"&y="+year+"&plot=full&r=json")
        app.logger.info(r.status_code)
        moviejson = r.json()  # capture json data
    except requests.exceptions.RequestException as e:
        app.logger.warn(e)

    if r.status_code == 200:
        app.logger.info("Match found on omdbapi")
        moviejson['naslocation'] = fullpathtomovie
        resultdb = db.movies.insert_one(moviejson)
        app.logger.info("Adding New Film: Name = "+str(name)+": "+str(resultdb.inserted_id))
        return None
    return fullpathtomovie


def main():
    with open('movies.txt','r') as f:
        movies = f.read().splitlines()

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

        if _items is None:
            # If movie not found in MongoDB, get metdata from omdbapi:
            newfilmresult = getfilmdata(name, year, movie)
            if newfilmresult is not None:
                movielisterror.append(newfilmresult)
        else:
            app.logger.info("Film in database already")
        time.sleep(90)

    if movielisterror:
        try:
            with open("errorfile.txt", 'w') as outfile:
                outfile.writelines(errorfile)
            outfile.close()
        except EnvironmentError:
            app.logger.warn('error writing to file')
    return


def readConfig():
    with open(config_file, mode='r') as out:
        input_json = json.load(out)
    out.close()

    return input_json


if __name__ == '__main__':
    main()
