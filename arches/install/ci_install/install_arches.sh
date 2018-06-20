#!/usr/bin/env bash

sudo rm -r /home/ubuntu/arches
sudo rm -r /home/ubuntu/ENV
sudo curl -XDELETE 'http://localhost:9200/_all'

sudo apt-get install -y git
sudo apt-get install -y python-pip
sudo -H pip install virtualenv==13.1.2
sudo npm install -g yarn

git clone -b stable/4.2.x https://github.com/archesproject/arches.git /home/ubuntu/arches

virtualenv /home/ubuntu/ENV
source /home/ubuntu/ENV/bin/activate

cd /home/ubuntu/arches
python setup.py install
yarn install

cp /home/ubuntu/settings_local.py /home/ubuntu/qa/qa

sudo chown ubuntu:ubuntu /home/ubuntu/qa/qa/arches.log

cd /home/ubuntu/qa

python manage.py migrate

python manage.py collectstatic --noinput
sudo chown www-data:www-data /home/ubuntu/qa/qa/arches.log
sudo service apache2 restart
