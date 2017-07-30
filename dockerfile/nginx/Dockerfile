# Set the base image
#FROM resin/rpi-raspbian:jessie-20160831
FROM resin/rpi-raspbian:latest

# Install nginx
# Separate nginx user not required, as www-data account is already being used
RUN apt-get update && apt-get install -y nginx

# Copy start script
#COPY files/start-nginx.sh /opt/
RUN rm /etc/nginx/sites-enabled/default
ADD sites-enabled/ /etc/nginx/sites-enabled
#WORKDIR /usr/src/app/
# Copy start script
COPY files/start-nginx.sh /opt/
CMD ["bash", "/opt/start-nginx.sh"]


## IMAGE CONFIGURATION

# Expose HTTP & HTTPS
#EXPOSE 80 443

# Update (optional) & start nginx
#CMD ["bash", "/opt/start-nginx.sh"]
