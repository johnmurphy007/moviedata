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
