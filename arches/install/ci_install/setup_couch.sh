#!/bin/bash

HOST="http://localhost:5984"
echo "couch version :"
curl -X GET $HOST
echo "adding admin :"
curl -X PUT $HOST/_config/admins/admin -d '"admin"'
echo "=_=_=_=_=_printing logs=_=_=_=_=_"
GET $HOST/_node/_local/_config HTTP/1.1
