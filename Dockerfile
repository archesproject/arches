FROM ubuntu:16.04
USER root

## Setting default environment variables
ENV WEB_ROOT=/web_root
ENV DOCKER_DIR=/docker
# Root project folder
ENV ARCHES_ROOT=${WEB_ROOT}/arches


## Install dependencies
WORKDIR /tmp
RUN apt-get update -y &&\
	apt-get upgrade -y &&\
	apt-get install -y wget \
		build-essential \
		libxml2-dev \
		libjson0-dev \
		libproj-dev \
		xsltproc docbook-xsl \
		docbook-mathml \
		libgdal1-dev \
		python-setuptools \
		python-dev \
		python-software-properties \
		dos2unix \
		curl \
		libpq-dev \
		libgeos-3.5.0 \
		openjdk-8-jre-headless \
		git-all \
		zlib1g-dev \
        clang \
        make \
        pkg-config &&\
	curl -sL https://deb.nodesource.com/setup_6.x | bash - &&\
	apt-get install nodejs &&\
	npm install -g bower &&\
	wget https://bootstrap.pypa.io/get-pip.py &&\
	python get-pip.py

	
## Install virtualenv
WORKDIR ${WEB_ROOT}
RUN pip install virtualenv==15.1.0 &&\
	virtualenv ENV &&\
	. ENV/bin/activate &&\
	pip install -U pip \
	setuptools &&\
	pip install requests \
		SPARQLWrapper
	
	
## Install Postgresql client
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ trusty-pgdg main" >> /etc/apt/sources.list.d/pgdg.list &&\
	wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - &&\
	apt-get update -y &&\
	apt-get install -y postgresql-client-9.6

	
## Clean up obsolete folders and packages
RUN rm -rf /var/lib/apt/lists/*
RUN rm -rf /tmp/*


# Install the Arches application
COPY . ${ARCHES_ROOT}
WORKDIR ${ARCHES_ROOT}

RUN . ${WEB_ROOT}/ENV/bin/activate &&\
	bower --allow-root install &&\
	python setup.py install
		
		
# Add Docker-related files
COPY docker/entrypoint.sh ${DOCKER_DIR}/entrypoint.sh
COPY docker/settings_local.py ${ARCHES_ROOT}/arches/settings_local.py
RUN	chmod -R 700 ${DOCKER_DIR} &&\
	dos2unix ${DOCKER_DIR}/*

	
# Set entrypoint
CMD ${DOCKER_DIR}/entrypoint.sh


# Expose port 8000
EXPOSE 8000


# Set default workdir
WORKDIR ${ARCHES_ROOT}
