#!/usr/bin/env bash

# this has been successfully tested on an AWS Centos 6.5 image
# this script was run by the root user, from the root ~ directory

sudo yum install -y http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-2.noarch.rpm
sudo yum check-update
sudo yum install -y libxml2-devel.x86_64
sudo yum install -y proj-devel.x86_64

sudo yum install -y json-c-devel.x86_64
sudo yum install -y libxslt.x86_64
sudo yum install -y docbook-style-xsl.noarch
sudo yum install -y gdal-devel.x86_64
sudo yum install -y libpqxx-devel.x86_64

sudo yum install -y wget
sudo yum install -y nano

# get jdk
sudo yum install -y java-1.7.0-openjdk-devel

# exclude current postgres packages from yum repos
if [ "$(grep -c exclude=postgresql* /etc/yum.repos.d/CentOS-Base.repo)" -eq 0 ]; then
    sudo sed -i '19i\exclude=postgresql*\' /etc/yum.repos.d/CentOS-Base.repo
    sudo sed -i '28i\exclude=postgresql*\' /etc/yum.repos.d/CentOS-Base.repo
fi

# install postgres 9.3
cd ~ && curl -O http://yum.postgresql.org/9.3/redhat/rhel-6-x86_64/pgdg-centos93-9.3-1.noarch.rpm
sudo rpm -ivh pgdg*
sudo yum install -y postgresql93-server
sudo yum install -y postgresql-contrib

# add postgres bin to $PATH (necessary for psycopg2 installation)
echo 'pathmunge /usr/pgsql-9.3/bin' > /etc/profile.d/ree.sh
chmod +x /etc/profile.d/ree.sh
. /etc/profile

# initialze and start db
sudo service postgresql-9.3 initdb
sudo chkconfig postgresql-9.3 on
sudo service postgresql-9.3 start

# install postgis
sudo rpm -ivh http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
sudo yum install -y postgis2_93

# configure postgres and postgis
sudo -u postgres psql -d postgres -c "ALTER USER postgres with encrypted password 'postgis';"
sudo echo "*:*:*:postgres:postgis" | sudo tee --append  ~/.pgpass
sudo chmod 600 ~/.pgpass

sudo service postgresql-9.3 stop

sudo chmod 666 /var/lib/pgsql/9.3/data/postgresql.conf
sudo chmod 666 /var/lib/pgsql/9.3/data/pg_hba.conf

echo 'CHANGED CONF FILE PERMISSIONS'
sudo echo "standard_conforming_strings = off" | sudo tee --append  /var/lib/pgsql/9.3/data/postgresql.conf
sudo echo "listen_addresses = '*'" | sudo tee --append  /var/lib/pgsql/9.3/data/postgresql.conf

sudo cp /var/lib/pgsql/9.3/data/pg_hba.conf var/lib/pgsql/9.3/data/pg_hba.conf.backup
sudo truncate /var/lib/pgsql/9.3/data/pg_hba.conf --size 0

sudo echo "#TYPE   DATABASE  USER  CIDR-ADDRESS  METHOD" | sudo tee --append  /var/lib/pgsql/9.3/data/pg_hba.conf
sudo echo "local   all       all                 trust" | sudo tee --append  /var/lib/pgsql/9.3/data/pg_hba.conf
sudo echo "host    all       all   127.0.0.1/32  trust" | sudo tee --append  /var/lib/pgsql/9.3/data/pg_hba.conf
sudo echo "host    all       all   ::1/128       trust" | sudo tee --append  /var/lib/pgsql/9.3/data/pg_hba.conf
sudo echo "host    all       all   0.0.0.0/0     md5" | sudo tee --append  /var/lib/pgsql/9.3/data/pg_hba.conf

sudo service postgresql-9.3 restart

sudo -u postgres psql -d postgres -c "CREATE EXTENSION postgis;"
sudo -u postgres createdb -E UTF8 -T template0 --locale=en_US.utf8 template_postgis_20
sudo -u postgres createlang -d template_postgis_20 plpgsql

sudo -u postgres psql -d postgres -c "UPDATE pg_database SET datistemplate='true' WHERE datname='template_postgis_20'"
sudo -u postgres psql -d template_postgis_20 -f /usr/pgsql-9.3/share/contrib/postgis-2.1/postgis.sql
sudo -u postgres psql -d template_postgis_20 -f /usr/pgsql-9.3/share/contrib/postgis-2.1/spatial_ref_sys.sql
sudo -u postgres psql -d template_postgis_20 -f /usr/pgsql-9.3/share/contrib/postgis-2.1/rtpostgis.sql
sudo -u postgres psql -d template_postgis_20 -c "GRANT ALL ON geometry_columns TO PUBLIC;"
sudo -u postgres psql -d template_postgis_20 -c "GRANT ALL ON geography_columns TO PUBLIC;"
sudo -u postgres psql -d template_postgis_20 -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"
sudo -u postgres createdb training -T template_postgis_20

# get geos
cd ~ && sudo wget http://download.osgeo.org/geos/geos-3.4.2.tar.bz2
sudo tar xvfj geos-3.4.2.tar.bz2 && cd geos-3.4.2
sudo ./configure && make && make install

# get python
sudo yum groupinstall -y 'development tools'
sudo yum install -y python-setuptools python-devel.x86_64
sudo yum install -y python-pip.noarch
sudo yum install -y xz-libs zlib-devel openssl-devel python-argparse python-tools python-setuptools

cd ~ && sudo wget https://www.python.org/ftp/python/2.7.6/Python-2.7.6.tgz
sudo tar xvf Python-2.7.6.tgz && cd Python-2.7.6
sudo ./configure && sudo make && make altinstall

# get virtualenv
cd ~ && sudo wget --no-check-certificate https://pypi.python.org/packages/source/s/setuptools/setuptools-1.4.2.tar.gz
sudo tar -xvf setuptools-1.4.2.tar.gz && cd setuptools-1.4.2
python2.7 setup.py install
curl https://bootstrap.pypa.io/get-pip.py | python2.7
pip install virtualenv
cd ~