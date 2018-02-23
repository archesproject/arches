#!/usr/bin/env bash

sudo rm -r /home/ubuntu/arches
sudo rm -r /home/ubuntu/ENV
sudo curl -XDELETE 'http://localhost:9200/_all'

sudo apt-get install -y git
sudo apt-get install -y python-pip
sudo -H pip install virtualenv==13.1.2
sudo npm install -g yarn

git clone -b master https://github.com/archesproject/arches.git /home/ubuntu/arches

virtualenv /home/ubuntu/ENV
source /home/ubuntu/ENV/bin/activate

pip install arches --no-binary :all:

arches-project create arches_dev
cd /home/ubuntu/arches_dev/arches_dev
yarn install
cd /home/ubuntu/arches_dev
cp /home/ubuntu/settings_local.py /home/ubuntu/arches_dev/arches_dev

sudo chown ubuntu:ubuntu /home/ubuntu/arches_dev/arches_dev/arches.log

python manage.py packages -o load_package -s https://github.com/archesproject/arches4-example-pkg/archive/master.zip -db true

python manage.py collectstatic --noinput
sudo chown www-data:www-data /home/ubuntu/arches/arches/arches.log
sudo service apache2 restart
