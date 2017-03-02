FROM ubuntu:16.04
USER root

## Setting default environment variables
ENV WEB_ROOT=/web_root
ENV INSTALL_DIR=/install
# Root project folder
ENV ARCHES_ROOT=${WEB_ROOT}/arches


## Install dependencies
WORKDIR ${INSTALL_DIR}/tmp
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
	python get-pip.py &&\
	pip install -U pip setuptools

	
## Install Mapnik
# Boost
# RUN apt-get -qq install -y libboost-dev libboost-filesystem-dev libboost-program-options-dev libboost-python-dev libboost-regex-dev libboost-system-dev libboost-thread-dev

# Mapnik dependencies
# RUN apt-get -qq install --yes  libsqlite3-dev libgdal-dev libcairo-dev python-cairo-dev postgresql-contrib 

# sudo apt-get install -y libmapnik2.2

RUN apt-get install -y libboost-all-dev \
	libicu-dev \
	libfreetype6-dev \
	libxml2-dev \
	libharfbuzz-dev \
	libtiff5-dev \
	libpng12-dev \
	libproj-dev
	
	
ENV MAPNIK_VERSION=v3.0.12
RUN git clone https://github.com/mapnik/mapnik.git mapnik &&\
	cd mapnik &&\
	git checkout ${MAPNIK_VERSION} &&\
	# git fetch --tags &&\
	# git checkout tags/${MAPNIK_VERSION} &&\
	git submodule update --init &&\
	# bash -c ". bootstrap.sh &&\
	# ./configure CUSTOM_CXXFLAGS='-D_GLIBCXX_USE_CXX11_ABI=0' &&\
	./configure &&\
	make &&\
	# make test &&\
	make install

	
## Install Postgresql client
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ trusty-pgdg main" >> /etc/apt/sources.list.d/pgdg.list &&\
	wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - &&\
	apt-get update -y &&\
	apt-get install -y postgresql-client-9.5


## Install virtualenv and Arches dependencies
# The latter is also done by the `python setup.py install` command, but running it here saves build time. 
# `docker build` uses a cache and only builds those steps in the Dockerfile that have changed since the last build. 
# Every time code is edited, `docker build` runs from the first COPY command below.
WORKDIR ${WEB_ROOT}
RUN pip install virtualenv==13.1.2 &&\
	virtualenv ENV &&\
	. ENV/bin/activate &&\
	pip install -U pip setuptools &&\
	pip install requests \
		'Django==1.9.2' \
		'elasticsearch>=2.0.0,<3.0.0' \
		'xlrd==0.9.4' \
		'Pillow==3.1.0' \
		rdflib \
		unicodecsv \
		pyyaml \
		'pyshp==1.2.3' \
		networkx \
		django-guardian \
		tilestache \
		shapely \
		python-memcached \
		'mapbox-vector-tile==0.5.0' \
		mapnik \
		python-dateutil


## Clean up obsolete folders and packages
RUN rm -rf /var/lib/apt/lists/*
RUN rm -rf ${INSTALL_DIR}/tmp


# Install the Arches application
COPY . ${ARCHES_ROOT}
WORKDIR ${ARCHES_ROOT}

RUN . ${WEB_ROOT}/ENV/bin/activate &&\
	bower --allow-root install &&\
	python setup.py install &&\
	python setup.py develop
		
		
# Add Docker-related files
COPY docker/entrypoint.sh ${INSTALL_DIR}/entrypoint.sh
COPY docker/init_arches.sh ${INSTALL_DIR}/init_arches.sh
COPY docker/settings_local.py ${ARCHES_ROOT}/arches/settings_local.py
RUN	chmod -R 700 ${INSTALL_DIR} &&\
	dos2unix ${INSTALL_DIR}/*

	
# Set entrypoint
CMD ${INSTALL_DIR}/entrypoint.sh


# Expose port 8000
EXPOSE 8000


# Set default workdir
WORKDIR ${WEB_ROOT}
