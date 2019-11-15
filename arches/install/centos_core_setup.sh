#!/usr/bin/env bash

sudo yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
sudo yum check-update
sudo yum install -y libxml2-devel.x86_64
sudo yum install -y proj-devel.x86_64

sudo yum install -y json-c-devel.x86_64
sudo yum install -y libxslt.x86_64
sudo yum install -y docbook-style-xsl.noarch
sudo yum install -y gdal-devel.x86_64
sudo yum install -y libpqxx-devel.x86_64

sudo yum install -y http://yum.postgresql.org/9.3/redhat/rhel-7-x86_64/pgdg-centos93-9.3-1.noarch.rpm
sudo yum install -y postgresql93-devel postgresql93-server postgresql93-contrib postgresql93-libs postgis2_93
sudo /usr/pgsql-9.3/bin/postgresql93-setup initdb
sudo systemctl enable postgresql-9.3.service
sudo systemctl start postgresql-9.3.service 

sudo -u postgres psql -d postgres -c "ALTER USER postgres with encrypted password 'postgis';"
sudo echo "*:*:*:postgres:postgis" | sudo tee --append  ~/.pgpass
sudo chmod 600 ~/.pgpass

sudo systemctl stop postgresql-9.3.service

sudo chmod 666 /var/lib/pgsql/9.3/data/postgresql.conf
sudo chmod 666 /var/lib/pgsql/9.3/data/pg_hba.conf

echo 'CHANGED CONF FILE PERMISSIONS'
sudo echo "standard_conforming_strings = off" | sudo tee --append  /var/lib/pgsql/9.3/data/postgresql.conf
sudo echo "listen_addresses = '*'" | sudo tee --append  /var/lib/pgsql/9.3/data/postgresql.conf

sudo cp /var/lib/pgsql/9.3/data/pg_hba.conf /var/lib/pgsql/9.3/data/pg_hba.conf.backup
sudo truncate /var/lib/pgsql/9.3/data/pg_hba.conf --size 0

sudo echo "#TYPE   DATABASE  USER  CIDR-ADDRESS  METHOD" | sudo tee --append  /var/lib/pgsql/9.3/data/pg_hba.conf
sudo echo "local   all       all                 trust" | sudo tee --append  /var/lib/pgsql/9.3/data/pg_hba.conf
sudo echo "host    all       all   127.0.0.1/32  trust" | sudo tee --append  /var/lib/pgsql/9.3/data/pg_hba.conf
sudo echo "host    all       all   ::1/128       trust" | sudo tee --append  /var/lib/pgsql/9.3/data/pg_hba.conf
sudo echo "host    all       all   0.0.0.0/0     md5" | sudo tee --append  /var/lib/pgsql/9.3/data/pg_hba.conf

sudo systemctl start postgresql-9.3.service

sudo -u postgres psql -d postgres -c "CREATE EXTENSION postgis;"
sudo -u postgres createdb -E UTF8 -T template0 --locale=en_US.utf8 template_postgis
sudo -u postgres createlang -d template_postgis plpgsql

sudo -u postgres psql -d postgres -c "UPDATE pg_database SET datistemplate='true' WHERE datname='template_postgis'"
sudo -u postgres psql -d template_postgis -f /usr/pgsql-9.3/share/contrib/postgis-2.1/postgis.sql
sudo -u postgres psql -d template_postgis -f /usr/pgsql-9.3/share/contrib/postgis-2.1/spatial_ref_sys.sql
sudo -u postgres psql -d template_postgis -f /usr/pgsql-9.3/share/contrib/postgis-2.1/rtpostgis.sql
sudo -u postgres psql -d template_postgis -c "GRANT ALL ON geometry_columns TO PUBLIC;"
sudo -u postgres psql -d template_postgis -c "GRANT ALL ON geography_columns TO PUBLIC;"
sudo -u postgres psql -d template_postgis -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"
sudo -u postgres createdb training -T template_postgis

sudo yum install -y python-setuptools python-devel.x86_64
sudo yum install -y python-pip.noarch
