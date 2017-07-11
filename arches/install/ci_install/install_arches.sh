#!/usr/bin/env bash

sudo rm -r /home/ubuntu/arches
sudo rm -r /home/ubuntu/ENV
sudo curl -XDELETE 'http://localhost:9200/_all'

sudo apt-get install -y git
sudo apt-get install -y python-pip
sudo -H pip install virtualenv==13.1.2
sudo npm install -g bower

git clone -b master https://github.com/archesproject/arches.git /home/ubuntu/arches

virtualenv /home/ubuntu/ENV
source /home/ubuntu/ENV/bin/activate

cd /home/ubuntu/arches
python setup.py install
bower install

python manage.py packages -o setup

cp /home/ubuntu/settings_local.py /home/ubuntu/arches/arches

sudo chown ubuntu:ubuntu /home/ubuntu/arches/arches/arches.log

python manage.py packages -o setup_db
python manage.py packages -o import_reference_data -s arches/db/schemes/arches_concept_scheme.rdf -ow overwrite -st keep
python manage.py packages -o import_reference_data -s arches/db/schemes/arches_concept_collections.rdf -ow overwrite -st keep
python manage.py packages -o import_graphs
python manage.py packages -o import_business_data -s /home/ubuntu/arches/tests/fixtures/data/csv/heritage_resource_model.csv -ow overwrite
python manage.py packages -o import_business_data_relations -s /home/ubuntu/arches/tests/fixtures/data/csv/heritage_resource_model.relations
python manage.py packages -o add_tileserver_layer -m arches/tileserver/hillshade.xml -n hillshade
python manage.py packages -o add_tileserver_layer -m arches/tileserver/world.xml -n world

python manage.py collectstatic --noinput
sudo chown www-data:www-data /home/ubuntu/arches/arches/arches.log
sudo service apache2 restart
