FROM ubuntu:16.04 as base 
USER root

## Setting default environment variables
ENV WEB_ROOT=/web_root
# Root project folder
ENV ARCHES_ROOT=${WEB_ROOT}/arches
ENV WHEELS=/wheels
ENV PYTHONUNBUFFERED=1

FROM base as wheelbuilder

WORKDIR ${WHEELS}

# Install pip requirements files
COPY ./arches/install/requirements.txt ${WHEELS}/requirements.txt
COPY ./arches/install/requirements_dev.txt ${WHEELS}/requirements_dev.txt

# Install packages required to build the python libs, then remove them
RUN set -ex \
    && BUILD_DEPS=" \
        build-essential \
        libpcre3-dev \
        libxml2-dev \
        libjson0-dev \
        libproj-dev \
        libgdal1-dev \
        python-dev \
        python-software-properties \
        libpq-dev \
        zlib1g-dev \
        clang \
        make \
        pkg-config \
        xsltproc \
        docbook-xsl \
        mime-support \
        docbook-mathml \
        curl \
        python-setuptools \
        dos2unix \
        libgeos-3.5.0 \
        nodejs \
        nodejs-legacy \
        npm \
        libldap2-dev \
        libsasl2-dev \
    " \
    && apt-get update && apt-get install -y --no-install-recommends $BUILD_DEPS \
    && curl -O https://bootstrap.pypa.io/get-pip.py \
    && python get-pip.py \
    && rm -rf /var/lib/apt/lists/* get-pip.py \
    && pip install --no-cache-dir -U pip setuptools \
    && pip wheel --no-cache-dir -b /tmp requests \
    && pip wheel --no-cache-dir -b /tmp -r ${WHEELS}/requirements.txt  \
    && pip wheel --no-cache-dir -b /tmp -r ${WHEELS}/requirements_dev.txt  \
    && pip wheel --no-cache-dir -b /tmp 'gunicorn==19.7.1' \
    && pip wheel --no-cache-dir -b /tmp django-auth-ldap

# Add Docker-related files
COPY docker/entrypoint.sh ${WHEELS}/entrypoint.sh
RUN chmod -R 700 ${WHEELS} &&\
  dos2unix ${WHEELS}/*.sh

FROM base 

# Get the pre-built python wheels from the build environment
RUN mkdir ${WEB_ROOT}

COPY --from=wheelbuilder ${WHEELS} /wheels

# Install packages required to run Arches
# Note that the ubuntu/debian package for libgdal1-dev pulls in libgdal1i, which is built
# with everything enabled, and so, it has a huge amount of dependancies (everything that GDAL
# support, directly and indirectly pulling in mysql-common, odbc, jp2, perl! ... )
# a minimised build of GDAL could remove several hundred MB from the container layer.
RUN set -ex \
    && RUN_DEPS=" \
        mime-support \
        curl \
        python-setuptools \
        libgdal1-dev \
        libgeos-3.5.0 \
        nodejs \
        nodejs-legacy \
        npm \
    " \
    && apt-get update && apt-get install -y --no-install-recommends $RUN_DEPS \
    && curl -sL https://deb.nodesource.com/setup_6.x | bash - \
    && apt-get install -y nodejs \
    && curl -sL https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - \
    && echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list \
    && apt-get update \
    && apt-get install yarn \
    && curl -O https://bootstrap.pypa.io/get-pip.py \
    && python get-pip.py \
    && rm -rf /var/lib/apt/lists/* get-pip.py

## Install Postgresql client
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ xenial-pgdg main" >> /etc/apt/sources.list.d/pgdg.list &&\
  curl https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - &&\
  apt-get update -y &&\
  apt-get install -y postgresql-client-9.6

## Install virtualenv
WORKDIR ${WEB_ROOT}

# Install the Arches application
# FIXME: ADD from github repository instead?
COPY . ${ARCHES_ROOT}

RUN mv ${WHEELS}/entrypoint.sh entrypoint.sh

RUN pip install virtualenv==15.1.0 \
    && virtualenv ENV \
    && . ENV/bin/activate \
    && pip install -U pip setuptools \
    && pip install requests \
    && pip install -r ${WHEELS}/requirements.txt \
                   -f ${WHEELS} \
    && pip install -r ${WHEELS}/requirements_dev.txt \
                   -f ${WHEELS} \
    && rm -rf ${WHEELS} \
    && rm -rf /root/.cache/pip/*

# From here, run commands from ARCHES_ROOT
WORKDIR ${ARCHES_ROOT}

RUN . ../ENV/bin/activate \
    && pip install -e . --no-binary :all:

# Install Yarn components
COPY ./package.json ${ARCHES_ROOT}/package.json
RUN yarn install

COPY docker/gunicorn_config.py ${ARCHES_ROOT}/gunicorn_config.py
COPY docker/settings_local.py ${ARCHES_ROOT}/arches/settings_local.py

# Set entrypoint
ENTRYPOINT ["../entrypoint.sh"]
CMD ["run_arches"]

# Expose port 8000
EXPOSE 8000

# Set default workdir
WORKDIR ${ARCHES_ROOT}
