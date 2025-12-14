to keep same codebase, packages across all the team, environment we need some kind of solution:
1. Virtualization: takes to much memory, heavy.
Levels: heavier
OS's (full OS)
Hypervisor (heavy)
windows kernel
hardware

2. Docker: it is lightweight, as it uses local systems kernel, not using full blown OS
Levels: lighter
OS(slice of os) known as images/image (as per actual os)
Docker Engine
window kernel
harware


Docker:
1. Difference between Docker container and Docker images/images:
=> docker container is an isolated environment to run docker images/image.


commands:
1. docker run -it {images/image} => will create and run a container with provided images/image. -i(--interactive - keep STDIN(standard input) open even if not attached), -t(--tty :Allocate a pseudo tty means i wanted my systems terminal connected with Docker Engine's terminal)
- first time it will check in your system if not found pull it from docker up and next time it directly uses the same images/image but for another container.
Note: docker run -it --name my-container ubuntu => creates container with name my-container
2. docker ps => lists all running the container
3. docker ps -a => lists all the containers (running/not running all), alias(docker container ls, docker container pd, docker container list)
4. docker images/images => list all the images/images have on machine, same as docker images/image ls
5. docker version
6. docker info => all the information of docker engine
7. docker pull images/image-name => manually pulling images/images for future purpose from docker-hub, docker images/image pull images/image-name
8. docker images/image inspect images/image-name => all the details will come
9. docker images/image rm images/image-name => to remove any of the images/image, but first need to container using this images/image then only able to delete this images/image.
10. docker container rm containerID => to remove container.
docker rm containerid1  containerid2 container 3, can remove at one time only
11. docker kill containerId => to stop running container, but still data of that container will be there, whereas rm command will remove that container.


=> EntryPoint: every images/image has entrypoint, once you connect to images/image where to connect default entrypoint.
for ex: for ubuntu images/image default entrypoint is bash.
we can also do like, this 
docker run -it {images/imageName} {command} {args} => docker run [OPTIONS] images/image [COMMAND] [ARG...]
ex- docker run -it busybox ping google.com

=> To check default entrypoint:
docker images/image inspect {images/imageName}
response = {
    ..
    "Cmd:[
        "sh"
    ]
    ..
}

this kind of json will come which will should what will be the default command or entrypoint for a particular images/image



Creating and using a Dockerfile to containerize node.js app:
Dockerfile is basically a config file

after writing Dockerfile use below command:
docker build -t my-app .
![alt text](images/image.png)

![s](images/image-1.png)
![alt text](images/image-2.png)

this is inside our container
![alt text](images/image-3.png)

Server is running in container:
![alt text](images/image-4.png)

to optimize this dockerfile we are using node official images/image instead of using ubuntu and install nodejs which results in higher size of images/image

we can add default entry point when the user runs the images/image by using below command
-- this command get executed when container starts
CMD ["npm", "start"]


every commands is a layer, docker caches the layers, if we do change in 3rd command, then docker stores 1st and 2nd in cache, and rest of the command will again got executed.

if source code got changed, then this will do npm install again, this is bad, what we can do:
-- once working directly is set, no need to mention it explicitly in copy command
WORKDIR /home/app

COPY package-lock.json package-lock.json 
-- also we can use wildcard pattern for this.
COPY package.json package.json

-- doing installation in working directory
RUN npm install

COPY index.js index.js 

means it will cache above commands and only index.js

### Command to build an images/image:
`docker build -t my-app .`

### To run and images/image in container:
`docker run -it my-app`


### Port mapping:
- now if we run the docker images/image, it will run the project, but still that localhost url is not mapped to a port. this port number will be of container not of our(host) system, as these container is isolated we can't use this, without doing port mapping.

command for this:
docker run -it -p [host's port]:[container's port] images/image-name
docker run -it -p 8000:8000 my-app   # host machine = localhost:8000 
docker run -it -p 3000:8000 my-app   # host machine = localhost:3000 

![alt text](images/image-5.png)

we can also do multiple port mappings:
docker run -it -p 3000:8000 -p 3001:9000 -p 3002:8001 my-app


### Automatic port mapping:
Need to add below command in Dockerfile:
EXPOSE 8000

Use below command while building images/image:
docker run -it -P  my-app  

![alt text](images/image-6.png)

-- when we expose a port, and use -P in run command, then docker will randomly assign a port to exposed ports.

for multiple ports:
EXPOSE 8000 3000 4000

docker run -it -P  my-app

![alt text](images/image-7.png)

to expose ports in a range:
EXPOSE 8000-8009

### after stoping a container it will remain in docker engine, to remove such container when they are stopped use below command:
docker run -it -P --rm my-app


### detached mode: to use one terminal and docker run command is blocking from executing other commands on that single terminal, then use:
docker run -it my-app -d # -d for running container in background and it will print container id.


### To push images/image on docker hub
- create repository on docker hub
- do docker build with the same name
- do docker login
- do docker push (buildname)repository name
  ex - `docker push mbs07/node-application` 

if build is of different name then:
- docker tag {build name} {repositoryname}
  ex - `docker tag my-app mbs07/node-application`

to push to version specific thing:
ex- `docker tag my-app mbs07/node-application:v1`
    `docker push mbs07/node-application:v1`
![alt text](images/image-8.png)

- if wants to pull specific version then use: `docker pull mbs07/node-application:v1`

### Building Optimized Multi-Stage Docker images/images for Production Use:
- now when we build a typescript project dist folder got created containing all the source code files, then why we are Copying source code from src folder too, the reason is if i build the project on windows and copy only the build folder means (dist folder), the same build might not work on linux or mac systems. To solve this we can use multi stage builds

in Multi stage docker images/images:
- create 1st stage to build the code as build and in 2nd stage only taking the build folder into images/image

=> cmd to use dockerfile by filename:
`docker build -t ts-app-old -f Dockerfile.old .`

- look at the size difference of old and new images/images: old = 251 MB and new = 197 MB
![alt text](images/image-10.png)

- here if we run a container for new ts-app there is not source code folder:
![alt text](images/image-11.png)


EX => Project => stage 1 (will give 1 GB (binary-exe file))  do the installation, copy the source code,                                    build the source code => => stage 2 (will give binary-exe file and start binary file) - Real world will get this only binary file, which will be in smaller size => world will use stage 2 lightweight

in final stage, there will no languages related libraries, no source code, just binary executable file


### Security vurnalability:
- user who is starting the docker file has admin previliges he can delete the files can do anything, you should never run the final command as a admin, so you can actually create the users in docker images/image
use below lines before CMD : 

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nodejs

USER nodejs

- this will run as nodejs user which has no admin previliges, always run the final as a non root user, if you run as a root user there might be some security vurnalabilities.

### Adding env port:
EXPOSE 3000
ENV PORT=3000 # make sure this line is added in docker file while building images/image

- below command will assign enviroment port number to the server:
- inside code we have => 
`const PORT = process.env.PORT ? +process.env.PORT : 3000;` 
- this line will take port number from env, but as of now we don't have any port in env, so in docker command we can pass env port using below command
`docker run -it -p 8000:8000 -e PORT=8000 ts-app-new`

- We can also add multiple env variables:
`docker run -it -p 8000:8000 -e x=y -e w=v -e t=u images/image-name`

- if we have env file then we can use below command: this will load env variables
`docker run -it -p 3000:3000 --envfile=./.env images/image-name`