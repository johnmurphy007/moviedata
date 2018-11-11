# moviedata

### Pre-requisties:
Docker
If running on Mac (or Windows) then need to use Docker-machine.

For Mac (from terminal):
* docker-machine start <env name>
* eval $(docker-machine env <env name>)
where <env name> is the docker-machine environment you want to use.

### To run:
cd to folder where 'docker-compose.yml' is located.

Everytime you have a new docker image to use, type:
docker-compose build
...this builds the docker images.

Otherwise, run the application using:
docker-compose up

To bring application down:
docker-compose down

### Updates:
`scanForFilms.py`
Python script to scan folders for movies.  Outputs results into a file
called 'movies.txt' in the format `name of movie` and `year` (if present).

`readFilmListAndAddToDB.py`
Python script that reads 'movie.txt' and will add film to MongoDB (if it
does not exist)
*TODO: Update the error file output. Currently checks if 'None' is returned.
New json object returned: {"Response":"False","Error":"Movie not found!"}
Need to use this instead.*

`verifyDBContent.py`
Used to read 'movies.txt' and check the mongo database if the film is in dB.
*TODO: Looks for an exact match.  Needs to be more tolerant.
Maybe the `readFilmListAndAddToDB.py` should update the entries in 'movies.txt'
when a match is found. 
