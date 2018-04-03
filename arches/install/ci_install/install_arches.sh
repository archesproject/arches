#!/usr/bin/env bash

sudo rm -r /home/ubuntu/arches

sudo apt-get install -y git
sudo apt-get install -y python-pip
sudo -H pip install virtualenv==13.1.2
sudo npm install -g bower

git clone -b stable/4.1.x https://github.com/archesproject/arches.git /home/ubuntu/arches

virtualenv /home/ubuntu/ENV
source /home/ubuntu/ENV/bin/activate

cd /home/ubuntu/qa

python manage.py migrate

sudo service apache2 restart
