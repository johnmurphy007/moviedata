#Dockerfile: https://github.com/docker-library/python/blob/master/3.4/onbuild/Dockerfile
FROM python:2.7.8-onbuild
#2.7.8
EXPOSE 8000
CMD ["gunicorn", "--config=gunicorn.py", "app:app"]
