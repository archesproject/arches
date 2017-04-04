# Arches in Docker

## Before you begin
***Note: This readme describes how to run Arches inside a Docker container.  
It is specifically written for users wanting to implement their own customized version of Arches.
If you are only interested in using Docker for developing the core Arches source code. please scroll down to 'Development'.***

Docker is the world’s leading software containerization platform: [docker.com](https://www.docker.com/)  

Some advantages of Docker:  

    - Eliminates the installation process from the end-user side: one can simply download the Arches Docker image from hub.docker.com and run the container.  
    - Keeps your system clean and provides a stable environment that is the same wherever you run it.  
    - Enhances security: the container your app is running in is isolated from the host machine.  


This Docker image of Arches comes without Postgresql or Elasticsearch installed. 
However, the tool 'docker-compose' (described below) will run these services for you.



## Requirements
- Docker installed on your machine: [docker.com/get-docker](https://www.docker.com/get-docker)

It also helps to read up on Docker: [docker.com/engine/getstarted](https://docs.docker.com/engine/getstarted/)



## Getting Started
1. Create your new project folder, preferably one managed by a version control system such as Git.

2. Copy [docker-compose.yml](../docker-compose.yml) from the root of the official Arches repository to the root of your project folder.

3. Edit your `docker-compose.yml`  
	Under the 'arches' service, change: 
	```
		image: arches/arches:latest
	```
	into 
	```
		image: <docker hub user>/<your project name>:latest
	```
	*Optional: You can leave `<docker hub user>/` out for now. Click [here](https://docs.docker.com/docker-hub/repos/) For more information on Docker Hub.*  

	Add `ARCHES_PROJECT` to the '`environment:`' node under the `arches` service:
	```
		environment:
			- ARCHES_PROJECT=<your project name>
	```

	*Note: `<your project name>` cannot contain dashes (-).*

4. Create a copy of `docker-compose.yml` called `docker-compose-local.yml`.  
This will be used throughout your development process and does not need to be checked in to version control. 

5. Edit your `docker-compose-local.yml`  
	Add this line under the `volumes` node:
	```
		volumes:
			- ./<your project name>:/web_root/arches/<your project name>
	```
	*Note: `<your project name>` cannot contain dashes (-). Must be the same as the value set in `ARCHES_PROJECT` above.*  
 
	Fill out the `PGPASSWORD` and `MAPBOX_API_KEY` environment variables under the `arches` service:
	```
		environment:
			- PGPASSWORD=<your chosen Postgres password>
			- MAPBOX_API_KEY=<your Mapbox API key>
	```
	Get your Mapbox API key here: [mapbox.com](https://www.mapbox.com/)

	Fill out the `POSTGRES_PASSWORD` environment variable under the `db` service:
	```
	    - POSTGRES_PASSWORD=<your chosen Postgres password>
	```
	(must be the same as PGPASSWORD.)
	
	***Warning: do not check your `docker-compose-local.yml` in to source control, as it now contains passwords.***

6. Create a new file in the root of your project called '`Dockerfile`' (no file extension) and add these lines:
	```
		FROM arches/arches:latest
		COPY . ${ARCHES_ROOT}
	```

7. Build your Docker image using your favorite command line tool (Powershell, CMD, Linux CLI, etc.).  
	Navigate to the root of your Arches project folder and type:
	```
		docker-compose -f .\docker-compose-local.yml build
	```

8. Run your Docker containers using:
	```
		docker-compose -f .\docker-compose-local.yml up
	```
	This will create your Arches project and start the web server.  
	Once that is running (you will see `"RUNNING DJANGO SERVER"`), you can bring it down again with ctrl + c (in Windows).  
 
9. Build the latest version of your Docker image using:
	```
		docker-compose -f .\docker-compose-local.yml build
	```
	This latest version of your Docker image will include your custom project.

10. Optional: to run your Docker containers again:
	```
		docker-compose -f .\docker-compose-local.yml up
	```
  
    
*Note 1: Point 6 will mount your Arches project from your host machine into your container. This is a way for connecting your development machine to the Docker container. It is very useful during the development process, as it allows you to edit code without having to build your Docker image after each edit. Remove this line for production environments.*

*Note 2: On startup your Docker container will create an Arches project using the name specified in point 4. This will only be done if it does not already exist.*  

*Note 3: with the tool `docker-compose` you can easilly orchestrate all required apps (in this case Arches, Postgres and Elasticsearch) on one server. This is mostly useful for development environments, as well as production setups with only one server. It must be run from the root of your project folder.*



## Parameter overview
Your docker-compose.yml file expects the following Environment Variables:

	- ARCHES_PROJECT=<Custom Arches project name> Used to set up your own Arches app 
	- FORCE_DB_INIT=<True or False> Optional: force the initialization of Postgresql and Elasticsearch on startup
	- PGPASSWORD=<Postgresql database password>
	- PGDBNAME=<Postgresql database name>
	- PGHOST=<Postgresql database host address>
	- PGPORT=<Postgresql database host port>
	- ESHOST=<Elasticsearch host address>
	- ESPORT=<Elasticsearch port>
	- DJANGO_MODE=<PROD or DEV> Use PROD for production (= live) environments
	- DJANGO_DEBUG=<True or False> Use False for production environments
	- DOMAIN_NAMES=<list of your domain names> Space separated list of domain names used to reach Arches, use 'localhost' for development environments
	- MAPBOX_API_KEY=<Your personal Mapbox api key>
	- TZ=<Time Zone> Optional: Useful for logging the correct time. US Eastern = EST


## Initialize
**On first run** Arches needs to initialize the database and Elasticsearch. 

For your convenience, this initialization is done when you first run Arches.
(See [docker/entrypoint.sh](/docker/entrypoint.sh) in the official Arches source code)

The initialization can be forced by setting the environment variable FORCE_DB_INIT before starting the Arches container.

**Be aware that this script deletes any existing database with the name set in the PGDBNAME environment variable.** 



## Settings
In order to make this Docker image portable, it is using environment variables.  
This is done through a settings_local.py file, which is copied into your new custom Arches project.  

This settings_local.py complements the default settings.py and overrides settings with the same name.  
You can expand it for any other settings that differ between environments.



## Custom scipts on startup
On startup, you can run custom scripts before Arches is started up (called an entrypoint). 
Any script placed in /docker/entrypoint in the Docker container is ran after the default actions, such as database initialization and the creation of a new custom Arches app. 

You can mount your custom scripts into the container, e.g.:
```
      volumes:
        - ./docker/entrypoint/script.sh:/docker/entrypoint/script.sh
```

Useful environment variables:
	- APP_FOLDER = The folder in your custom Arches app where your manage.py file lives. `/your_project_root/<your_project_name>`



## Connect to your container
The general command to enter your running container from the command line is: 
```
	docker exec -it <container id> bash
```
To get the container id:
```
	docker ps
```

For more information, see the [```docker exec``` command documentation](https://docs.docker.com/engine/reference/commandline/exec/)



## Housekeeping
A cleanup script is provided in the official Arches repository: [docker/cleanup.ps1](docker/cleanup.ps1).
This can be run on any OS and removes old Docker containers, unused images, etc.



## Development
**These steps are relevant for Arches core development:**  
For development environments, it is advisable to mount your source code into the container for instant code editing without rebuilding your Docker image.  

1. Create a copy of [docker-compose.yml](../docker-compose.yml) called `docker-compose-local.yml`.  
2. Add this line to `docker-compose-local.yml` under `volumes`:
```
	- ./:/web_root/arches/
```
3. Build your Docker containers using:
```
	docker-compose -f .\docker-compose-local.yml build
```
4. Run your Docker containers using:
```
	docker-compose -f .\docker-compose-local.yml up
```

This will mount the root Arches folder into your container. This allows you to edit code on your development machine, which is directly linked to the code in your Docker container.  
  


## See also
docker-compose.yml uses a number of other Docker images.

ElasticSearch: https://hub.docker.com/_/elasticsearch/  
Postgresql & PostGIS: https://hub.docker.com/r/mdillon/postgis/
