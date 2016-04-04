#!/usr/bin/env bash



sudo -u postgres dropdb training

sudo -u postgres psql -d postgres -c "UPDATE pg_database SET datistemplate='false' WHERE datname='template_postgis_20'"
sudo -u postgres dropdb template_postgis_20
# sudo -u postgres psql -d postgres -c "UPDATE pg_database SET datistemplate='false' WHERE datname='template0'"
# sudo -u postgres dropdb template0
