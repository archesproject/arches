#!/usr/bin/env bash

sudo rm -r -y ~/arches
sudo rm -r -y ~/ENV

sudo apt-get install -y git
sudo apt-get install -y python-pip
sudo -H pip install virtualenv==13.1.2

cd ~
git clone -b travis_ci_tests https://github.com/archesproject/arches.git

virtualenv ~/ENV
source ~/ENV/bin/activate

cd arches
python setup.py install

python manage.py packages -o setup

python manage.py packages -o setup_elasticsearch
source ~/arches/arches/elasticsearch/elasticsearch-2.2.0/bin/elasticsearch >> ~/elasticsearch.log &

python manage.py runserver 0.0.0.0:80 &
