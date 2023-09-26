#!/usr/bin/env bash

# For Ubuntu 18.04+

# Use the yes command if you would like to install postgres/postgis,
# node/yarn, and elasticsearch.
# Example:
# yes | sudo ./ubuntu_setup.sh

function install_postgres {
  sudo add-apt-repository "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -sc)-pgdg main"
  wget --quiet -O - http://apt.postgresql.org/pub/repos/apt/ACCC4CF8.asc | sudo apt-key add -
  sudo apt-get update
  sudo apt-get install postgresql-14 postgresql-contrib-14 -y
  sudo apt-get install postgresql-14-postgis-3 -y
  PGPASS=$(openssl rand -base64 14)
  sudo -u postgres psql -d postgres -c "ALTER USER postgres with encrypted password '$PGPASS';"
  sudo echo "*:*:*:postgres:$PGPASS" >> ~/.pgpass
  sudo chmod 600 ~/.pgpass
  sudo chmod 666 /etc/postgresql/14/main/postgresql.conf
  sudo chmod 666 /etc/postgresql/14/main/pg_hba.conf
  sudo echo "standard_conforming_strings = off" >> /etc/postgresql/14/main/postgresql.conf
  sudo echo "listen_addresses = '*'" >> /etc/postgresql/14/main/postgresql.conf
  sudo echo "#TYPE   DATABASE  USER  CIDR-ADDRESS  METHOD" > /etc/postgresql/14/main/pg_hba.conf
  sudo echo "local   all       all                 trust" >> /etc/postgresql/14/main/pg_hba.conf
  sudo echo "host    all       all   127.0.0.1/32  trust" >> /etc/postgresql/14/main/pg_hba.conf
  sudo echo "host    all       all   ::1/128       trust" >> /etc/postgresql/14/main/pg_hba.conf
  sudo echo "host    all       all   0.0.0.0/0     md5" >> /etc/postgresql/14/main/pg_hba.conf
  sudo chmod 664 /etc/postgresql/14/main/postgresql.conf
  sudo chmod 664 /etc/postgresql/14/main/pg_hba.conf
  sudo service postgresql restart

  sudo -u postgres createdb -E UTF8 -T template0 --locale=en_US.utf8 template_postgis
  sudo -u postgres psql -d postgres -c "UPDATE pg_database SET datistemplate='true' WHERE datname='template_postgis'"
  sudo -u postgres psql -d template_postgis -c "CREATE EXTENSION postgis;"
  sudo -u postgres psql -d template_postgis -c "CREATE EXTENSION \"uuid-ossp\";"
  sudo -u postgres psql -d template_postgis -c "GRANT ALL ON geometry_columns TO PUBLIC;"
  sudo -u postgres psql -d template_postgis -c "GRANT ALL ON geography_columns TO PUBLIC;"
  sudo -u postgres psql -d template_postgis -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"
}

function install_yarn {
  wget --quiet -O - https://deb.nodesource.com/setup_16.x | sudo -E bash -
  sudo apt-get update
  sudo apt-get install -y nodejs
  sudo apt install curl
  curl -sL https://dl.yarnpkg.com/debian/pubkey.gpg | gpg --dearmor | sudo tee /usr/share/keyrings/yarnkey.gpg >/dev/null
  echo "deb [signed-by=/usr/share/keyrings/yarnkey.gpg] https://dl.yarnpkg.com/debian stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
  sudo apt update
  sudo apt install yarn
}

function install_elasticsearch {
  sudo apt-get install apt-transport-https
  wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
  sudo sh -c 'echo "deb https://artifacts.elastic.co/packages/8.x/apt stable main" > /etc/apt/sources.list.d/elastic-8.x.list'
  sudo apt-get update
  sudo apt-get install elasticsearch
  sudo /bin/systemctl enable elasticsearch.service
  sudo systemctl enable elasticsearch.service
  sudo systemctl start elasticsearch.service

  printf "y\nE1asticSearchforArche5\nE1asticSearchforArche5" | sudo /usr/share/elasticsearch/bin/elasticsearch-reset-password -i -u elastic
}

function main {
  sudo add-apt-repository "deb http://archive.ubuntu.com/ubuntu $(lsb_release -sc) universe"
  sudo apt-get update -y
  sudo apt-get install -y make software-properties-common
  #sudo add-apt-repository -y ppa:ubuntugis/ubuntugis-unstable

  sudo apt-get install -y build-essential
  sudo apt-get install -y libxml2-dev
  sudo apt-get install -y libproj-dev
  sudo apt-get install -y libjson-c-dev
  sudo apt-get install -y xsltproc
  sudo apt-get install -y docbook-xsl
  sudo apt-get install -y docbook-mathml
  sudo apt-get install -y libgdal-dev
  sudo apt-get install -y libpq-dev

  sudo apt-get install -y python3-dev
  sudo apt-get install -y python3-venv

  echo -n "Would you like to install elasticsearch? (y/N)? "
  read answer
  if echo "$answer" | grep -iq "^y" ;then
    echo Yes, installing Elasticsearch
    install_elasticsearch
  else
    echo Skipping Elasticsearch installation
  fi

  echo -n "Would you like to install and configure postgres/postgis? (y/N)? "
  read answer
  if echo "$answer" | grep -iq "^y" ;then
    echo Yes, Installing Postgres/PostGIS
    install_postgres
  else
    echo Skipping Postgres/PostGIS installation
  fi

  echo -n "Would you like to install and nodejs/npm/and yarn (y/N)? "
  read answer
  if echo "$answer" | grep -iq "^y" ;then
    echo Yes, installing Node/Yarn
    install_yarn
  else
    echo Skipping Node/Yarn installation
  fi
}

main
