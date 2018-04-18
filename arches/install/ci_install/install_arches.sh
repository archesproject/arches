#!/usr/bin/env bash

# sudo rm -r /home/ubuntu/arches
# sudo rm -r /home/ubuntu/arches_dev
sudo rm -r /home/ubuntu/ENV
# sudo curl -XDELETE 'http://localhost:9200/_all'

# sudo apt-get install -y git
# sudo apt-get install -y python-pip
# sudo -H pip install virtualenv==13.1.2
# sudo npm install -g yarn

cd /home/ubuntu/arches
git pull

# git clone -b master https://github.com/archesproject/arches.git /home/ubuntu/arches

virtualenv /home/ubuntu/ENV
source /home/ubuntu/ENV/bin/activate

cd /home/ubuntu/arches
pip install -e . --no-binary :all:
pip install -r arches/install/requirements.txt

# cd /home/ubuntu
# arches-project create arches_dev
# cd /home/ubuntu/arches_dev/arches_dev
# yarn install
# cp /home/ubuntu/settings_local.py /home/ubuntu/arches_dev/arches_dev

sudo chown ubuntu:ubuntu /home/ubuntu/arches/arches/arches.log
sudo chown ubuntu:ubuntu /home/ubuntu/arches_dev/arches_dev/arches.log
sudo chown ubuntu:ubuntu /home/ubuntu/fileuploads/ -R

cd /home/ubuntu/arches_dev
# python manage.py packages -o load_package -s https://github.com/archesproject/arches4-example-pkg/archive/master.zip -db true

python manage.py collectstatic --noinput

sudo chown www-data:www-data /home/ubuntu/arches/arches/arches.log
sudo chown www-data:www-data /home/ubuntu/arches_dev/arches_dev/arches.log
sudo chown www-data:www-data /home/ubuntu/fileuploads/ -R

sudo service apache2 restart
