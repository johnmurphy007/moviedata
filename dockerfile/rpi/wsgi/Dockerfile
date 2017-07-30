#Dockerfile: https://github.com/docker-library/python/blob/master/3.4/onbuild/Dockerfile
FROM python:2.7.8-onbuild
#2.7.8
EXPOSE 8000
EXPOSE 1883
#RUN chmod 755 /usr/src/app/mqtt_sub.py
#ENTRYPOINT ["/usr/src/app/mqtt_sub.py"]
CMD ["gunicorn", "--config=gunicorn.py", "app:app"]
