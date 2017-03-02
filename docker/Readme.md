# Arches in Docker

This readme describes how to run Arches inside a Docker container.  
Docker is the world’s leading software containerization platform: https://www.docker.com/  

Some advantages of Docker:  

    - Eliminates the installation process from the end-user side: one can simply download the Arches Docker image from hub.docker.com and run the container.  
    - Keeps your system clean and provides a stable environment that is the same wherever you run it.  
    - Enhances security: the container your app is running in is isolated from the host machine.  


This Docker image of Arches comes without Postgresql or Elasticsearch installed. 
However, the 'Docker-compose' section below describes how you can run those with Docker as well.



## Quick-start: docker-compose
The easiest way to get up and running is with the tool docker-compose (which comes with the regular Docker installation).

With this tool you can easilly orchestrate all required apps on one server. 
This is mostly useful for development environments, but can also be used on production setups with only one server.  

An example [docker-compose.yml](../docker-compose.yml) file is provided in the Arches Git repository.  
Be sure to set at least the PGPASSWORD and MAPBOX_API_KEY settings under the `arches` service, as well as the POSTGRES_PASSWORD setting under the `db` service (must be same as PGPASSWORD).

To run Arches, Nginx, Postgres, Elasticsearch and Letsencrypt (a free certificate tool) in Docker, navigate to the root of the repository and type the following command:
```
	docker-compose up
```

**Expect to see an error saying your database does not exist. See 'Initialize' below.**



## Run
To run Arches without docker-compose (see above):

(Assuming you have a Postgresql and Elasticsearch server already running.)
```
	docker run arches/arches:latest \
		PGPASSWORD=SecretPassword1@ \
        PGDBNAME=arches \
        PGHOST=your-postgres-server.com \
        PGPORT=5432 \
        ESHOST=your-elasticsearch-server.com \
        DJANGO_MODE=PROD \
        DJANGO_DEBUG=False \
        DOMAIN_NAMES=your-arches-domain.com \
		MAPBOX_API_KEY=<Your personal Mapbox api key> \
        TZ=EST
```

**Expect to see an error saying your database does not exist. See 'Initialize' below.**



## Initialize
**On first run** Arches needs to initialize the database and Elasticsearch. 

For your convenience, a script is provided in this Docker image that does the initialization for you: ```install/init_arches.sh```
(In the source code: [docker/init_arches.sh](/docker/init_arches.sh) )
This will run:
```
	python manage.py packages -o setup
	manage.py packages -o import_graphs
```
**Be aware that this script deletes any existing Arches database.** Only run this once. 

You can run this script using `docker-compose.yml` or in a `docker run` command (but be careful to remove it after first run):  

When using `docker-compose.yml` (see above), change this line:
`command: bash -c  "sleep 15 && /install/entrypoint.sh"`
into
`command: bash -c  "sleep 15 && /install/init_arches.sh && /install/entrypoint.sh"`

When using `docker run` (see below): 
```
	docker run arches/arches:latest \
		[rest of command] \
		/install/init_arches.sh
```

Alternatively, run this script or its commands manually from inside your Arches container while Postgresql and Elasticsearch are running.
(See paragraph 'Connect to your container' below).



## Settings
In order to make this Docker image portable, it is using environment variables.
This settings file complements the default settings.py and overrides the following settings:

The following settings are used in the example settings_local.py:

        - PGPASSWORD=<Postgresql database password>
        - PGDBNAME=<Postgresql database name>
        - PGHOST=<Postgresql database host address>
        - PGPORT=<Postgresql database host port>
        - ESHOST=<Elasticsearch host address>
        - DJANGO_MODE=<PROD or DEV, use PROD for production (=live) environments>
        - DJANGO_DEBUG=<True or False, use False for production environments>
        - DOMAIN_NAMES=<Domain names used to reach Arches, use localhost for development environments>
		- MAPBOX_API_KEY=<Your personal Mapbox api key>
        - TZ=<Optional: Time zone. Useful for logging the correct time. US Eastern = EST>

If you would like to add settings controlled through environment variables, create a settings_local.py and mount it into your container.
An example settings file can be found in the Arches Git repository: [docker/settings_local.py](/docker/settings_local.py). 	
Your customized settings file can be mounted into your container.

When using `docker-compose.yml` (see above), change this line:
```
volumes:
        - /path/to/settings_local.py:/web_root/arches/arches/settings_local.py
```
When using `docker run` (see below): 
```
	docker run arches/arches:latest \
		[rest of command] \
		-v /path/to/settings_local.py:/web_root/arches/arches/settings_local.py
```	

	
	
## Connect to your container
The general command to enter your running container from the command line is:
```docker exec -it <container id> bash```

To get the container id:
```docker ps```

For more information, see the [```docker exec``` command documentation](https://docs.docker.com/engine/reference/commandline/exec/)


	
## Development
For development environments, it is advisable to mount your source code into the container for instant code editing without rebuilding Docker image. 
Additionally, this will allow you to 'catch' the source code created with the `arches-project create` command. 

If your settings_local.py is not under /web_root/arches/arches/, be sure to also mount it to the right location in your container, otherwise it will not be picked up. In docker-compose.yml:
```
volumes:
        - ./:/web_root/arches/
        - ./docker/settings_local.py:/web_root/arches/arches/settings_local.py		
```

This will mount the root folder and your settings file into your container. 



## See also
docker-compose.yml uses a number of other Docker images.

Nginx: https://hub.docker.com/r/cvast/cvast-nginx/ 
LetsEncrypt: https://hub.docker.com/r/cvast/cvast-letsencrypt/
ElasticSearch: https://hub.docker.com/_/elasticsearch/
Postgresql & PostGIS: https://hub.docker.com/r/mdillon/postgis/
