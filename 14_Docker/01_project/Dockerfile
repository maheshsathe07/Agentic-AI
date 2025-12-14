# FROM ubuntu 

# # to install nodejs on ubuntu
# # firstly need to install curl
# RUN apt-get update
# RUN apt install -y curl  
# # curl to get nodejs setup script for version 20
# RUN curl -sL https://deb.nodesource.com/setup_20.x -o /tmp/nodesource_setup.sh
# RUN bash /tmp/nodesource_setup.sh
# RUN apt install -y nodejs

# # COPY file_from_local file_to_container(docker image) can specify file path to 
# COPY index.js /home/app/index.js 
# COPY package-lock.json /home/app/package-lock.json
# COPY package.json /home/app/package.json

# # set working directory
# WORKDIR /home/app

# # doing installation in working directory
# RUN npm install


# Optimizing Dockerfile
# can use node official image which has nodejs preinstalled as with earlier image is coming too heavy
FROM node:20.17.0-alpine3.19

# set working directory
WORKDIR /home/app

# COPY file_from_local file_to_container(docker image) can specify file path to 
# this wildcard will copy both package.json and package-lock.json and . means current working directory
COPY package*.json .

# doing installation in working directory
RUN npm install

COPY index.js index.js 
# because of above modification if source code changes we don't need to do npm install again

# Exposing port for automapping:
EXPOSE 3000

# this command get executed when container starts
CMD ["npm", "start"]