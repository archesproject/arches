#!/usr/bin/env bash

sudo rm -r -y /home/ubuntu/arches
sudo rm -r -y /home/ubuntu/ENV

sudo apt-get install -y git
sudo apt-get install -y python-pip
sudo -H pip install virtualenv==13.1.2

git clone -b travis_ci_tests https://github.com/archesproject/arches.git /home/ubuntu/arches

virtualenv /home/ubuntu/ENV
source /home/ubuntu/ENV/bin/activate

cd /home/ubuntu/arches
python setup.py install

python manage.py packages -o setup

sudo chown ubuntu:ubuntu /home/ubuntu/arches/arches/arches.log
python manage.py collectstatic --noinput
sudo chown www-data:www-data /home/ubuntu/arches/arches/arches.log
sudo service apache2 restart