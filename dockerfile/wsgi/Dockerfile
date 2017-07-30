#FROM resin/rpi-raspbian:jessie-20160831
FROM resin/rpi-raspbian:latest
#RUN apt-get update && \
#    apt-get -y install curl python python-dev build-essential && \
#    curl https://bootstrap.pypa.io/get-pip.py | python && \
RUN apt-get update && \
	apt-get install -y python python-dev build-essential python-pip

RUN pip install flask gunicorn requests pymongo

EXPOSE 8000
WORKDIR /usr/src/app/
CMD ["gunicorn", "--config=gunicorn.py", "app:app"]
