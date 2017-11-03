# Arches in Docker

## Before you begin
***Note: This readme describes how to run Arches inside a Docker container.  
It is specifically written for users wanting to implement their own customized version of Arches.
If you are only interested in using Docker for developing the core Arches source code, please scroll down to 'Development'.***

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



## Quick start
1. Create a new folder for your custom Arches code, preferably one managed by a version control system such as Git.

2. Copy [docker-compose.yml](../docker-compose.yml) from the root of the official Arches repository to the root of your project folder.

3. Download the latest Docker image of Arches. Navigate to the folder you placed `docker-compose.yml` in and type:
  `docker-compose pull`

4. Run Arches:  
  `docker-compose up`

Your Arches app can now be reached by going to `http://localhost` in your browser. 

To gracefully shut down, hit `ctrl + c` in the same terminal window and wait for the containers to stop.  
Alternatively, type this command in another terminal window: `docker-compose down`



## Setting up your own Arches project
1. Set the name of your Docker image. Edit your `docker-compose.yml`:  
	Under the 'arches' service, change:
	```
		image: archesproject/arches:latest
	```
	into
	```
		image: <docker hub user>/<your project name>:latest
	```
	*Optional: You can leave the `<docker hub user>/` part out for now. Click [here](https://docs.docker.com/docker-hub/repos/) For more information on Docker Hub.*  

2. Set the name of your Arches project. Edit your `docker-compose.yml`:  
	Add `ARCHES_PROJECT` to the '`environment:`' node under the `arches` service:
	```
		environment:
			- ARCHES_PROJECT=<your project name>
	```

	*Note: `<your project name>` cannot contain dashes (-).*

3. Create a copy of `docker-compose.yml` called `docker-compose-local.yml`.  
This will be used throughout your development process and does not need to be checked in to version control. Use the original `docker-compose.yml` in production environments.

4. For quick development, mount your source code from your development machine into the container. Edit your `docker-compose-local.yml`:  
	Add this line under the `volumes` node:
	```
		volumes:
			- ./<your project name>:/web_root/<your project name>
	```
	*Note: <your project name> must be the same as the value set in `ARCHES_PROJECT` in step 2.*  
	
	This will allow for instant code editing without rebuilding your Docker image.  

5. Set a couple of important Arches variables. Edit your `docker-compose-local.yml`:  
  Fill out the `PGPASSWORD` environment variables under the `arches` service:
	```
		environment:
			- PGPASSWORD=<your chosen Postgres password>
	```

6. Set the Postgresql password. Edit your `docker-compose-local.yml`:  

	Fill out the `POSTGRES_PASSWORD` environment variable under the `db` service:
	```
	    - POSTGRES_PASSWORD=<your chosen Postgres password>
	```
	*Note: Password must be the same as PGPASSWORD in step 5.*

	***Warning: do not check your `docker-compose-local.yml` in to source control, as it now contains passwords.***

7. Set up your own Docker image build. Create a new file in the root of your project called '`Dockerfile`' (no file extension) and add these lines:
	```
		FROM archesproject/arches:latest
		COPY . ${WEB_ROOT}
	```

8. Build your Docker image using your favorite command line tool (Powershell, CMD, Linux CLI, etc.).  
	Navigate to the root of your Arches project folder and type:
	```
		docker-compose -f .\docker-compose-local.yml build
	```

9. Run your Docker containers using:
	```
		docker-compose -f .\docker-compose-local.yml up
	```
	This command runs a couple of checks and then starts the Django server.
  The first time this will create your Arches project using the name specified in point 2.

	Once that is running (you will see `"RUNNING DJANGO SERVER"`), you can bring it down again with ctrl + c (in Windows).  

  *If you did not skip step 4 (mounting a volume), you will now have new files and folders on your development machine (under `./<your project name>`).  
  This is your very own Arches app. This is where you will change or edit code to adapt Arches to your needs.*

10. Optimize your Docker build. Open your Dockerfile and edit the `COPY` command, so that only your Arches project gets copied to the image, instead of the complete root folder:

	```
		COPY ./<your project name> ${WEB_ROOT}
	```
	*Note: `your project name` must be the same as the value set in `ARCHES_PROJECT` in step 2.*  
	
11. Build the latest version of your Docker image using:
	```
		docker-compose -f .\docker-compose-local.yml build
	```
	This latest version of your Docker image will include your custom project.

11. Optional: to run your Docker containers again:
	```
		docker-compose -f .\docker-compose-local.yml up
	```


*Note 1: Point 4 will mount your Arches project from your host machine into your container. This is a way for connecting your development machine to the Docker container. It is very useful during the development process, as it allows you to edit code without having to build your Docker image after each edit. Remove this line for production environments.*

*Note 2: with the tool `docker-compose` you can easilly orchestrate all required apps (in this case Arches, Postgres and Elasticsearch) on one server. This is mostly useful for development environments, as well as production setups with only one host server. The `docker-compose` program must be run from the root of your project folder.* 



## Commands
Any command you would normally run on the command line can be used with this Docker image of Arches.  
The basic format is: `docker-compose run arches <command>`   
E.g.: `docker-compose run arches python manage.py packages -o import_graphs [-s path_to_json_directory_or_file]`  

**Additionally**, the following shorthand commands can be used:

- `run_arches`: Default if no command is specified. Run the Arches server  
- `run_tests`: Run unit tests  
- `setup_arches`: Delete any existing Arches database and set up a fresh one  
- `run_migrations`: Run Django migrations  
- `-h` or `--help`: Display help text  

These commands can be chained, e.g.:  
`docker-compose run arches run_tests setup_db`

Or in your `docker-compose.yml` file:  
`command: run_tests run_server`



## Parameter overview
Your docker-compose.yml file expects the following Environment Variables:

- `ARCHES_PROJECT` = *Custom Arches project name*  
	-> **Used to set up your own Arches app**  
- `INSTALL_DEFAULT_GRAPHS` = True | False   
    -> **Used to fill the database with the default graphs that come with Arches**  
- `INSTALL_DEFAULT_CONCEPTS` = True | False  
    -> **Used to fill the database with the default concepts that come with Arches**
- `PGUSERNAME` = *Postgresql database username*
- `PGPASSWORD` = *Postgresql database password*
- `PGDBNAME` = *Postgresql database name*
- `PGHOST` = *Postgresql database host address*
- `PGPORT` = *Postgresql database host port*
- `ESHOST` = *Elasticsearch host address*
- `ESPORT` = *Elasticsearch port*
- `DJANGO_MODE` = PROD | DEV  
	-> **Use PROD for production (= live) environments**
- `DJANGO_DEBUG` = True | False  
	-> **Use False for production environments**  
- `DOMAIN_NAMES` = *list of your domain names*  
	-> **Space separated list of domain names used to reach Arches, use 'localhost' for development environments**  

Optional Environment Variables:  

- `DJANGO_PORT` = *Django server port*  
	-> **Runs your Django server on an alternative port. Default = 8000**
- `DJANGO_NORELOAD` = True | False  
	-> **Runs Django with options --noreload --nothreading. Useful for some debugging methods**
- `DJANGO_SECRET_KEY` = *50 character string*  
	-> **Used by Django for security. Use this environment variable only if you run Arches without custom project (i.e. the `ARCHES_PROJECT` environment variable is not set)**
- `TZ` = *Time Zone*  
	-> **Useful for logging the correct time. US Eastern = EST**



## Production vs Development
Please note that the [docker-compose.yml](../docker-compose.yml) file provided is written for a production environment. Therefore it includes an `Nginx` container that serves as a reverse proxy (for security). Additionally, it uses a `LetsEncrypt` container to download web certificates.

When running Arches in production, be sure to set your domain name in the DOMAIN_NAMES variable in all appropriate services (Arches, Nginx and Letsecrypt) in the `docker-compose.yml` file. Separate your domain names by spaces if you have multiple.

In order to enable https (`port 443`), scroll down to the `nginx` service in your `docker-compose.yml` and change this environment variable:  
- NGINX_PROTOCOL=http  
into  
- NGINX_PROTOCOL=strict-https  
  
If you would like search engines such as Google to index your Arches website, set the `Nginx` variable `PUBLIC_MODE` to `true`.

For development environments, the Nginx and LetsEncrypt services can be deleted or commented out from the `docker-compose.yml` file. In that case, your Arches instance will be available at `http://localhost:8000` (note the port). 



## Custom scripts on startup
On startup, you can run custom scripts before Arches is started up (called an entrypoint).
Any script placed in /docker/entrypoint in the Docker container is ran after the default actions, such as database initialization and the creation of a new custom Arches app.

You can mount your custom scripts into the container, e.g.:
```
      volumes:
        - ./docker/entrypoint/script.sh:/docker/entrypoint/script.sh
```



## Debugging
In order to enable remote debugging, see [this tutorial](https://gist.github.com/veuncent/1e7fcfe891883dfc52516443a008cfcb) for Visual Studio (Code).  
Point 4 is handled for you, all you need to do is set this environment variable:
- DJANGO_NORELOAD=True

For remote debugging Pycharm, see [this tutorial](https://gist.github.com/veuncent/1e7fcfe891883dfc52516443a008cfcb.)



## Troubleshoot
- Potentially ports `80` and/or `443` on your machine are already taken by another application. In this case, change the port number of your Nginx service in `docker-compose.yml`. Be sure to keep the second number of the `port:port` pairs unchanged:
```
      ports:
        - '81:80'
        - '444:443'
```

## See also
docker-compose.yml uses a number of other Docker images.

ElasticSearch: https://hub.docker.com/_/elasticsearch/  
Postgresql & PostGIS: https://hub.docker.com/r/mdillon/postgis/  
Nginx: https://github.com/cvast/cvast-nginx   
LetsEncrypt: https://github.com/cvast/cvast-letsencrypt  






&nbsp;  
&nbsp;  
&nbsp;  
&nbsp;  

# Misc / Good-to-Know



## Initialize
**On first run** Arches needs to initialize the database and Elasticsearch.

For your convenience, this initialization is done when you first run Arches.
(See [docker/entrypoint.sh](/docker/entrypoint.sh) in the official Arches source code)

The initialization can be forced using the `setup_arches` command.  
**Be aware that this command deletes any existing database with the name set in the PGDBNAME environment variable.**



## Settings
In order to make this Docker image portable, it is using environment variables.  
This is done through a settings_local.py file, which is copied into your new custom Arches project.  

This settings_local.py complements the default settings.py and overrides settings with the same name.  



## Housekeeping
A cleanup script is provided in the official Arches repository: [docker/cleanup.ps1](docker/cleanup.ps1).
This can be run on any OS and removes old Docker containers, unused images, etc.



## Useful environment variables
- APP_FOLDER = The folder in your custom Arches app where your manage.py file lives. This can be useful when writing deployment scripts. `/your_project_root/<your_project_name>`
- DJANGO_NORELOAD = Set this to "True" if you do not want Django to reload the server each time the python code is updated. Useful when using a remote debugger.



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



## Arches Core Development
As described in point 3 and 4 of the `Setting up` section above, for development environments it is advisable to mount your source code into the container for instant code editing without rebuilding your Docker image.  

The same can be done when developing the core Arches project itself, with some slight adjustments:

1. Create a copy of [docker-compose.yml](../docker-compose.yml) called `docker-compose-local.yml`.  
2. Add these lines to `docker-compose-local.yml` under `volumes`:  
```
	- ./:/web_root/arches/  
	- ./docker/settings_local.py:/web_root/arches/arches/settings_local.py	
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

The volume commands at *point 2* also mounts a settings_local.py into the container. This ensures some important settings, e.g. database and Elasticsearch endpoints, can still be set through environment variables. **This settings file may be overwritten by your own settings file, presuming you are including these settings as well.**