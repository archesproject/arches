#!/bin/bash

HOST="http://localhost:5984"
echo "couch version :"
curl -X GET $HOST
echo "adding admin :"
sudo curl -X PUT $HOST/_config/admins/admin -d '"admin"'
sudo cat /var/log/couchdb/couch.log
