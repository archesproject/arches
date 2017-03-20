#!/usr/bin/env bash
sudo apt-get update -y
sudo apt-get install -y make python-software-properties
sudo add-apt-repository -y ppa:ubuntugis/ubuntugis-unstable
sudo apt-get update -y
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" >> /etc/apt/sources.list.d/pgdg.list'
wget -q https://www.postgresql.org/media/keys/ACCC4CF8.asc -O - | sudo apt-key add -
sudo sh -c 'echo "deb https://artifacts.elastic.co/packages/5.x/apt stable main" >> /etc/apt/sources.list.d/elastic-5.x.list'
wget -qO - https://packages.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
sudo apt-get update -y

sudo apt-get install -y postgresql postgresql-contrib
sudo apt-get install -y build-essential
sudo apt-get install -y libxml2-dev
sudo apt-get install -y libproj-dev
sudo apt-get install -y libjson0-dev
sudo apt-get install -y xsltproc
sudo apt-get install -y docbook-xsl
sudo apt-get install -y docbook-mathml
sudo apt-get install -y libgdal1-dev
sudo apt-get install -y libpq-dev
sudo apt-get install -y libgeos-3.4.2
sudo apt-get install -y openjdk-7-jdk elasticsearch=2.2.0
sudo apt-get install -y libmapnik2.2

sudo -u postgres psql -d postgres -c "ALTER USER postgres with encrypted password 'postgis';"
sudo echo "*:*:*:postgres:postgis" >> ~/.pgpass
sudo chmod 600 ~/.pgpass
sudo chmod 666 /etc/postgresql/9.5/main/postgresql.conf
sudo chmod 666 /etc/postgresql/9.5/main/pg_hba.conf
sudo echo "standard_conforming_strings = off" >> /etc/postgresql/9.5/main/postgresql.conf
sudo echo "listen_addresses = '*'" >> /etc/postgresql/9.5/main/postgresql.conf
sudo echo "#TYPE   DATABASE  USER  CIDR-ADDRESS  METHOD" > /etc/postgresql/9.5/main/pg_hba.conf
sudo echo "local   all       all                 trust" >> /etc/postgresql/9.5/main/pg_hba.conf
sudo echo "host    all       all   127.0.0.1/32  trust" >> /etc/postgresql/9.5/main/pg_hba.conf
sudo echo "host    all       all   ::1/128       trust" >> /etc/postgresql/9.5/main/pg_hba.conf
sudo echo "host    all       all   0.0.0.0/0     md5" >> /etc/postgresql/9.5/main/pg_hba.conf
sudo service postgresql restart

sudo apt-get install -y postgis

sudo -u postgres psql -d postgres -c "CREATE EXTENSION postgis;"
sudo -u postgres createdb -E UTF8 -T template0 --locale=en_US.utf8 template_postgis_20
sudo -u postgres psql -d postgres -c "UPDATE pg_database SET datistemplate='true' WHERE datname='template_postgis_20'"
sudo -u postgres psql -d template_postgis_20 -c "CREATE EXTENSION postgis;"
sudo -u postgres psql -d template_postgis_20 -c "GRANT ALL ON geometry_columns TO PUBLIC;"
sudo -u postgres psql -d template_postgis_20 -c "GRANT ALL ON geography_columns TO PUBLIC;"
sudo -u postgres psql -d template_postgis_20 -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"
sudo -u postgres createdb training -T template_postgis_20


# sudo -u postgres createdb -E UTF8 -T template_postgis_20 --locale=en_US.utf8 arches
