#!/usr/bin/env bash
sudo apt-get update -y
sudo apt-get install -y make python-software-properties
sudo add-apt-repository -y ppa:ubuntugis/ubuntugis-unstable
sudo apt-get update -y

sudo apt-get install -y build-essential
sudo apt-get install -y postgresql-9.3
sudo apt-get install -y postgresql-server-dev-9.3
sudo apt-get install -y libxml2-dev
sudo apt-get install -y libproj-dev
sudo apt-get install -y libjson0-dev
sudo apt-get install -y xsltproc
sudo apt-get install -y docbook-xsl
sudo apt-get install -y docbook-mathml
sudo apt-get install -y libgdal1-dev
sudo apt-get install -y postgresql-contrib-9.3
sudo apt-get install -y postgresql-server-dev-9.3
sudo apt-get install -y libpq-dev

sudo -u postgres psql -d postgres -c "ALTER USER postgres with encrypted password 'postgis';"
sudo echo "*:*:*:postgres:postgis" >> ~/.pgpass
sudo chmod 600 ~/.pgpass
sudo chmod 666 /etc/postgresql/9.3/main/postgresql.conf
sudo chmod 666 /etc/postgresql/9.3/main/pg_hba.conf
sudo echo "standard_conforming_strings = off" >> /etc/postgresql/9.3/main/postgresql.conf
sudo echo "listen_addresses = '*'" >> /etc/postgresql/9.3/main/postgresql.conf
sudo echo "#TYPE   DATABASE  USER  CIDR-ADDRESS  METHOD" > /etc/postgresql/9.3/main/pg_hba.conf
sudo echo "local   all       all                 trust" >> /etc/postgresql/9.3/main/pg_hba.conf
sudo echo "host    all       all   127.0.0.1/32  trust" >> /etc/postgresql/9.3/main/pg_hba.conf
sudo echo "host    all       all   ::1/128       trust" >> /etc/postgresql/9.3/main/pg_hba.conf
sudo echo "host    all       all   0.0.0.0/0     md5" >> /etc/postgresql/9.3/main/pg_hba.conf
sudo service postgresql restart

sudo wget http://download.osgeo.org/geos/geos-3.4.2.tar.bz2
sudo tar xvfj geos-3.4.2.tar.bz2
cd geos-3.4.2
./configure
make
sudo make install
cd ..

sudo wget http://download.osgeo.org/postgis/source/postgis-2.1.3.tar.gz
sudo tar xfvz postgis-2.1.3.tar.gz
cd postgis-2.1.3
./configure
make
sudo make install
sudo ldconfig
sudo make comments-install
sudo ln -sf /usr/share/postgresql-common/pg_wrapper /usr/local/bin/shp2pgsql
sudo ln -sf /usr/share/postgresql-common/pg_wrapper /usr/local/bin/pgsql2shp
sudo ln -sf /usr/share/postgresql-common/pg_wrapper /usr/local/bin/raster2pgsql
cd ..

sudo -u postgres psql -d postgres -c "CREATE EXTENSION postgis;"
sudo -u postgres createdb -E UTF8 -T template0 --locale=en_US.utf8 template_postgis_20
sudo -u postgres createlang -d template_postgis_20 plpgsql
sudo -u postgres psql -d postgres -c "UPDATE pg_database SET datistemplate='true' WHERE datname='template_postgis_20'"
sudo -u postgres psql -d template_postgis_20 -f /usr/share/postgresql/9.3/contrib/postgis-2.1/postgis.sql
sudo -u postgres psql -d template_postgis_20 -f /usr/share/postgresql/9.3/contrib/postgis-2.1/spatial_ref_sys.sql
sudo -u postgres psql -d template_postgis_20 -f /usr/share/postgresql/9.3/contrib/postgis-2.1/rtpostgis.sql
sudo -u postgres psql -d template_postgis_20 -c "GRANT ALL ON geometry_columns TO PUBLIC;"
sudo -u postgres psql -d template_postgis_20 -c "GRANT ALL ON geography_columns TO PUBLIC;"
sudo -u postgres psql -d template_postgis_20 -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"
sudo -u postgres createdb training -T template_postgis_20

sudo apt-get install -y openjdk-7-jdk python-setuptools python-dev

sudo -u postgres createdb -E UTF8 -T template_postgis_20 --locale=en_US.utf8 arches

