#!/usr/bin/env bash

python manage.py runserver 0.0.0.0:80 &

sudo service elasticsearch start
sudo service apache2 start