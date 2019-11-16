#!/usr/bin/env bash

sudo service elasticsearch stop

sudo -u postgres dropdb training

sudo -u postgres psql -d postgres -c "UPDATE pg_database SET datistemplate='false' WHERE datname='template_postgis'"
sudo -u postgres dropdb template_postgis