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

def readConfig():
    with open(config_file, mode='r') as out:
        input_json = json.load(out)
    out.close()

    return input_json

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


def main():
    with open('movies.txt.bak','r') as f:
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
            movielisterror.append(movie)
        else:
            app.logger.info("Film in database already")

    if movielisterror:
        print "Errors found in:"
        print movielisterror
        try:
            with open("errorfile.txt", 'w') as outfile:
                for movieerror in movielisterror:
                    outfile.write(str(movieerror) + "\n")
            outfile.close()
        except EnvironmentError:
            app.logger.warn('error writing to file')
    return

if __name__ == '__main__':
    main()
