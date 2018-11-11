#!/usr/bin/python
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
    configjson = readConfig()
    films_to_search_for = configjson['movie_file_format']
    filmformats = films_to_search_for.keys()

    result = []
    app.logger.info("Search for Movies")
    app.logger.info(path1)
    for path, dirs, files in os.walk(path1):
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


def main():
    # Read config.py file
    configjson = readConfig()
    path_to_search = configjson['path_to_search']
    app.logger.info(path_to_search)

    # scan folders for movies.  Array/list returned and captured in 'movies'
    movies = searchformovies(path_to_search)
    with open('movies.txt', 'w') as f:
        for item in movies:
            f.write("%s\n" % item)


def readConfig():
    #config_file # = "config.json"
    with open(config_file, mode='r') as out:
        input_json = json.load(out)
    out.close()

    return input_json


if __name__ == '__main__':
    main()
