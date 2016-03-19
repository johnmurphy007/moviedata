#Dockerfile
FROM python:3.4-onbuild
#2.7.8
EXPOSE 8000
CMD ["gunicorn", "--config=gunicorn.py", "app:app"]
