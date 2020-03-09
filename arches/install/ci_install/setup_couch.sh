#!/bin/bash

HOST="http://localhost:5984"
echo "couch version :"
curl -X GET $HOST
sudo chmod o+rwx /etc/couchdb/local.d/erlang_query_server.ini
service couchdb restart
echo "adding admin :"
curl -X PUT $HOST/_config/admins/admin -d '"admin"'
# sudo cat /var/log/couchdb/couch.log
