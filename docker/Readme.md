# Arches in Docker

*   [Quick start](#quick-start)
    *   [Parameter overview](#parameter-overview)
    *   [Commands](#commands)
    *   [Running Docker in Production](#running-docker-in-production)
    *   [Troubleshoot](#troubleshoot)
*   [Developing](#developing)
    *   [Setting up your own Arches project](#setting-up-your-own-arches-project)
    *   [Running in DEV mode](#running-in-dev-mode)
    *   [Arches Core Development](#arches-core-development)
    *   [Arches Core Development Troubleshoot](#arches-core-development-troubleshoot)
*   [Additional Information](#additional-information)
    *   [Initialize](#initialize)
    *   [Settings](#settings)
    *   [Custom scripts on startup](#custom-scripts-on-startup)
    *   [Connect to your container](#connect-to-your-container)
    *   [Remote Debugging](#remote-debugging)
    *   [Housekeeping](#housekeeping) 




## Quick start
1.  Install [Docker](https://www.docker.com/get-docker) on your Machine.  

2.  Create a new folder for your custom Arches code, preferably one managed by a version control system such as Git.

3.  Copy [docker-compose.yml](../docker-compose.yml) from the root of the official Arches repository to the root of your project folder.

4.  Edit the [docker-compose.yml](../docker-compose.yml) file locally, filling in the appropriate variables, including project, PGPASSWORD and TZ.

5.  To download the latest Docker images of Arches, PostGIS, ElasticSearch, and NGINX, navigate to the folder you placed [docker-compose.yml](../docker-compose.yml) in and run the following command:  
  `docker-compose pull`

6.  Run Arches:  
`docker-compose up`

Your Arches app can now be reached by going to `http://localhost` in your browser. 

To gracefully shut down, hit `ctrl + c` in the same terminal window and wait for the containers to stop.  
Alternatively, type this command in another terminal window: `docker-compose down`



### Parameter overview
Your docker-compose.yml file expects the following Environment Variables:

-   `ARCHES_PROJECT` = *Custom Arches project name*  
	-> **Used to set up your own Arches app. Project names should not contain spaces.**  
-   `INSTALL_DEFAULT_GRAPHS` = True | False  
    -> **Used to fill the database with the default graphs that come with Arches**  
-   `INSTALL_DEFAULT_CONCEPTS` = True | False  
    -> **Used to fill the database with the default concepts that come with Arches**
-   `PGUSERNAME` = *PostgreSQL database username*
-   `PGPASSWORD` = *PostgreSQL database password*
-   `PGDBNAME` = *PostgreSQL database name*  
	-> **This should match the `ARCHES_PROJECT` variable, if set.**
-   `PGHOST` = *PostgreSQL database host address*
-   `PGPORT` = *PostgreSQL database host port*
-   `ESHOST` = *Elasticsearch host address*
-   `ESPORT` = *Elasticsearch port*
-   `DJANGO_MODE` = PROD | DEV  
	-> **Use PROD for production (= live) environments**
-   `DJANGO_DEBUG` = True | False  
	-> **Use False for production environments**  
-   `DOMAIN_NAMES` = *list of your domain names*  
	-> **Space separated list of domain names used to reach Arches, use 'localhost' for development environments**  

Optional Environment Variables:  
-   `ELASTICSEARCH_PREFIX` = *Prefix for ElasticSearch Tables*  
	-> **Allows you to run multiple projects in one ElasticSearch instance. It should be the same as `ARCHES_PROJECT`**
-   `DJANGO_PORT` = *Django server port*  
	-> **Runs your Django server on an alternative port. Default = 8000**
-   `DJANGO_SECRET_KEY` = *50 character string*  
	-> **Used by Django for security. Use this environment variable only if you run Arches without custom project (i.e. the `ARCHES_PROJECT` environment variable is not set)**
-   `TZ` = *Time Zone*  
	-> **Useful for logging the correct time. US Pacific = PST**



### Commands
Any command you would normally run on the command line can be used with this Docker image of Arches.  
The basic format is: `docker-compose run arches <command>`  
E.g.: `docker-compose run arches python manage.py packages -o import_graphs [-s path_to_json_directory_or_file]`  

**Additionally**, the following shorthand commands can be used:

-   `run_arches`: Default if no command is specified. Run the Arches server  
-   `run_tests`: Run unit tests  
-   `setup_arches`: Delete any existing Arches database and set up a fresh one  
-   `run_migrations`: Run Django migrations, useful for upgrade between versions of Arches.  
-   `-h` or `--help`: Display help text  

These commands can be chained, e.g.:  
`docker-compose run arches run_tests setup_db`

Or in your `docker-compose.yml` file:  
`command: run_tests run_server`



### Running Docker in Production
When running Arches in production, be sure to set your domain name in the DOMAIN_NAMES variable in all appropriate services (Arches, Nginx and LetsEcrypt) in the `docker-compose.yml` file. Separate your domain names by spaces if you have multiple. You should also ensure your docker-compose.yml sets PRODUCTION_MODE=True as the default False setting will not issue verifyable certificates and cause your https: connections to be marked as insecure. Documentation for the letsencrypt setup can be found at https://hub.docker.com/r/cvast/cvast-letsencrypt/ an example production config appears below:
```
    letsencrypt:
      container_name: letsencrypt
      image: cvast/cvast-letsencrypt:1.1
      volumes:
        - letsencrypt-acme-challenge:/var/www
        - letsencrypt:/etc/letsencrypt
        - letsencrypt-log:/var/log/letsencrypt
      command: get_certificate
      environment:
        - MODE=regular
        - FORCE_RENEWAL=False
        - LETSENCRYPT_EMAIL=YOUR_EMAIL
        - DOMAIN_NAMES=YOUR_DOMAIN_NAMES
        - PRODUCTION_MODE=True
        - PERSISTENT_MODE=True
        - TZ=GMT
        - FORCE_NON_ELB=True
        - AWS_DEFAULT_REGION=YOUR_REGION - eg eu_west
```


In order to enable https (`port 443`), scroll down to the `nginx` service in your `docker-compose.yml` and change this environment variable:  
`NGINX_PROTOCOL=http`  
into  
`NGINX_PROTOCOL=strict-https`  
  
If you would like search engines such as Google to index your Arches website, set the `Nginx` variable `PUBLIC_MODE` to `true`.

#### Gunicorn
When running in production mode, traffic to and from the user is handled by Gunicorn.  
This is all set up for you in the Arches docker image and no further action is required.

Optionally, most settings can be overriden with environment variables.  
Settings of interest may be `GUNICORN_WORKERS` and `GUNICORN_WORKER_TIMEOUT`.  

- `GUNICORN_WORKERS` sets the amount of Gunicorn workers that are created to handle user requests. Rule of thumb is: 2 * amount of CPUs + 1 [(more info)](http://docs.gunicorn.org/en/stable/design.html#how-many-workers).  
- `GUNICORN_WORKER_TIMEOUT` sets the timeout in seconds for requests handled by Gunicorn. Default is 30; set this to a higher value if you expect to upload large files.



### Troubleshoot
- Potentially ports `80` and/or `443` on your machine are already taken by another application. In this case, change the port number of your Nginx service in `docker-compose.yml`. Be sure to keep the second number of the `port:port` pairs unchanged:
    ```
        ports:
            - '81:80'
            - '444:443'
    ```


- When you try to load Arches in your browser and all you see is a white page with black text (and many 404 errors in your browser console), check out [Running in DEV mode](#running-in-dev-mode)





## Developing 



### Setting up your own Arches project
1.  Set the name of your Docker image. Edit your `docker-compose.yml`:  
	Under the 'arches' service, change:  
	`image: archesproject/arches:latest`  
	into  
	`image: <docker hub user>/<your project name>:latest`  
	*Optional: You can leave the `<docker hub user>/` part out for now. Click [here](https://docs.docker.com/docker-hub/repos/) For more information on Docker Hub.*  

2.  Set the name of your Arches project. Edit your `docker-compose.yml`:  
	Add `ARCHES_PROJECT` to the '`environment:`' node under the `arches` service:  
    ```
        environment:
            - ARCHES_PROJECT=<your project name>                    # <-- Add this line
    ```
    
    *Note: `<your project name>` cannot contain dashes (-) or spaces.*

3.  Create a copy of `docker-compose.yml` called `docker-compose-local.yml`.  
This will be used throughout your development process and does not need to be checked in to version control. Use the original `docker-compose.yml` in production environments.

4.  For quick development, mount your source code from your development machine into the container. Edit your `docker-compose-local.yml`:  
	Add this line under the `volumes` node:
	```
        volumes:
            - ./<your project name>:/web_root/<your project name>   # <-- Add this line
    ```

    *Note: <your project name> must be the same as the value set in `ARCHES_PROJECT` in step 2.*  
	
    This will allow for instant code editing without rebuilding your Docker image.  

5.  Set a couple of important Arches variables. Edit your `docker-compose-local.yml`:  
  Fill out the `PGPASSWORD` environment variables under the `arches` service:  
	```
        environment:
            - PGPASSWORD=<your chosen Postgres password>            # <-- Add this line
    ```

6.  Set the PostgreSQL password. Edit your `docker-compose-local.yml`:  

    Fill out the `POSTGRES_PASSWORD` environment variable under the `db` service:  
    ```
        environment:
	        - POSTGRES_PASSWORD=<your chosen Postgres password>     # <-- Add this line
    ```
	*Note: Password must be the same as `PGPASSWORD` in step 5.*


7.  Set up your own Docker image build. Create a new file in the root of your project called '`Dockerfile`' (no file extension) and add these lines:  
    ```
        FROM archesproject/arches:latest  
        COPY . ${WEB_ROOT}  
        WORKDIR ${WEB_ROOT}/${ARCHES_PROJECT}/${ARCHES_PROJECT}  
        RUN yarn install  
    ```

8.  Build your Docker image using your favorite command line tool (Powershell, CMD, Linux CLI, etc.).  
	Navigate to the root of your Arches project folder and type:  
	`docker-compose -f .\docker-compose-local.yml build`  

9.  Run your Docker containers using:  
	`docker-compose -f .\docker-compose-local.yml up`  
    
    This command runs a couple of checks and then starts the Django server. The first time this will create your Arches project using the name specified in point 2.

    Once that is running (you will see `"RUNNING DJANGO SERVER"`), you can bring it down again with ctrl + c (in Windows).  

    *If you did not skip step 4 (mounting a volume), you will now have new files and folders on your development machine (under `./<your project name>`).  
    
    This is your very own Arches app. This is where you will change or edit code to adapt Arches to your needs.*

10. Optimize your Docker build. Open your Dockerfile and edit the `COPY` command, so that only your Arches project gets copied to the image, instead of the complete root folder:  
    ```
	COPY ./<your project name> ${WEB_ROOT}
    ```
    *Note: `your project name` must be the same as the value set in `ARCHES_PROJECT` in step 2.*  
	
11. Build the latest version of your Docker image using:  
		`docker-compose -f .\docker-compose-local.yml build`  
        
    This latest version of your Docker image will include your custom project.

11. Optional: to run your Docker containers again:  
	`docker-compose -f .\docker-compose-local.yml up`  

*Note 1: Point 4 will mount your Arches project from your host machine into your container. This is a way for connecting your development machine to the Docker container. It is very useful during the development process, as it allows you to edit code without having to build your Docker image after each edit. Remove this line for production environments.*

*Note 2: with the tool `docker-compose` you can easilly orchestrate all required apps (in this case Arches, Postgres and Elasticsearch) on one server. This is mostly useful for development environments, as well as production setups with only one host server. The `docker-compose` program must be run from the root of your project folder.* 



### Running in DEV mode
The `docker-compose.yml` file provided for you in the Arches git repository is configured to run in production.  
Specific settings of interest are:

- Environment variables in the `Arches` service: 
    - `DJANGO_MODE=PROD`: When set to PROD, prepares your static files (css, js, etc) to be served through the Nginx web server
    - `DJANGO_DEBUG=False`: Among other things, `True` will display exception pages in the browser (more info [here](https://docs.djangoproject.com/en/1.11/ref/settings/#debug))
- The `Nginx` service, which is a web server that sits between the user (you) and the Arches service

When developing, use `DJANGO_MODE=DEV` and `DJANGO_DEBUG=True`. This will effectively bypass your Nginx service, so contact your Arches service directly on port 8000:
http://localhost:8000

For convenience you can map port 80 from your host machine to port 8000 in your Arches container. In your `docker-compose(-local).yml` under your Arches  service:
```
    ports:
        - '8000:8000'
        - '80:8000'             # <-- Add this line
```
Now you can access your Arches service through http://localhost



### Arches Core Development
To develop on Arches Core, ensure you are not already running PostgreSQL and it is advisable to mount your source code into the container for instant code editing without rebuilding your Docker image.  

1. Checkout your fork of the Arches repository. See [here](https://github.com/archesproject/arches/wiki#-contributing-code) for more information. 

2. In your Arches Root Directory, create a copy of [docker-compose.yml](../docker-compose.yml) called `docker-compose-local.yml`.  

3.  Adjust the `image` for the `arches` container to be:  
    `image: archesproject/arches:master`

4.  Add these lines to `docker-compose-local.yml` under the `arches` container under `volumes`:  
    ```
    volumes:
        - ./:/web_root/arches/                                                  # <-- Add this line
        - ./docker/settings_local.py:/web_root/arches/arches/settings_local.py  # <-- Add this line
    ```
    This will mount the root Arches folder into your container, which allows you to edit code on your development machine, which is directly linked to the code in your Docker container.

5.  Build your Docker containers using:  
	`docker-compose -f .\docker-compose-local.yml build`  
    
6.  Ensure any other instances of PostgreSQL, ElasticSearch and Arches are turned off, to ensure your ports do not clash.

7.  Run your Docker containers using:  
	`docker-compose -f .\docker-compose-local.yml up`  

8. See [Running in DEV mode](#running-in-dev-mode) to get exception messages in the browser and to bypass Nginx.  


##### Dependencies
Any time you change Arches Dependancies, you will need to re-build your Docker Container.  
The `docker-compose -f .\docker-compose-local.yml build` command will re-build the container for you based upon the `Dockerfile`.  
*Tip: If your new or updated dependency does not install correctly, you may need to build without cache:  
`docker-compose -f .\docker-compose-local.yml build --no-cache`*

##### settings_local.py
The volume section at **point 4** also mounts a `settings_local.py` into the container.  
This ensures some important settings, e.g. database and Elasticsearch endpoints, can still be set through environment variables.  
**This settings file may be overwritten by your own settings file, presuming you are including these settings as well.**

##### Yarn components
Because your volume from `step 4` is laid over the files in your container, files generated during image `build` are hidden.  
In order to install newly added static file packages, run the following command:  
    `docker-compose -f .\docker-compose-local.yml run arches install_yarn_components`

##### docker-compose-local.yml
Here is a link to a working [docker-compose-local.yml](https://gist.github.com/jmunowitch/c63fa39be4651b9bf2f0b1abc69f7479) file




### Arches Core Development Troubleshoot
Errors during setting up the Arches container for Development that you may encounter:
-   `The 'arches==4.0.2b0' distribution was not found and is required by the application`  
-> **You will need to re-build the Docker container, possibly without Cache. .**  

Potentially ports `80` and/or `443` on your machine are already taken by another application. In this case, change the port number of your Nginx service in `docker-compose.yml`. Be sure to keep the second number of the `port:port` pairs unchanged:
```
    ports:
        - '81:80'
        - '444:443'
```





## Additional Information




### Initialize
**On first run** Arches needs to initialize the PostgreSQL database and ElasticSearch.

For your convenience, this initialization is done when you first run Arches.
(See [docker/entrypoint.sh](/docker/entrypoint.sh) in the official Arches source code)

The initialization can be forced using the `setup_arches` command.  
**Be aware that this command deletes any existing database with the name set in the PGDBNAME environment variable.**



### Settings
In order to make this Docker image portable, it is using environment variables.  
This is done through a settings_local.py file, which is copied into your new custom Arches project.  

This settings_local.py complements the default settings.py and overrides settings with the same name.  



### Custom scripts on startup
On startup, you can run custom scripts before Arches is started up (called an entrypoint).
Any script placed in /docker/entrypoint in the Docker container is ran after the default actions, such as database initialization and the creation of a new custom Arches app.

You can mount your custom scripts into the container, e.g.:
```
    volumes:
        - ./docker/entrypoint/script.sh:/docker/entrypoint/script.sh    # <-- Add this line
```



### Connect to your container
The general command to enter your running container from the command line is:  
`docker exec -it <container id> bash`  
To get the container id:  
`docker ps`  

For more information, see the [```docker exec``` command documentation](https://docs.docker.com/engine/reference/commandline/exec/)



### Remote Debugging
In order to enable remote debugging for Visual Studio (Code), see [this tutorial](https://gist.github.com/veuncent/1e7fcfe891883dfc52516443a008cfcb).  


### Housekeeping
A cleanup script is provided in the official Arches repository: [docker/cleanup.ps1](docker/cleanup.ps1).
This can be run on any OS and removes old Docker containers, unused images, etc.


