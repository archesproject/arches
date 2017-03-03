#!/bin/bash

echo "" 
echo "" 
echo "*** Initializing database ***" 
echo "" 
echo "*** Any existing Arches database will be deleted ***"
echo "" 
echo "" 

echo "5"
sleep 1
echo "4"
sleep 1
echo "3"
sleep 1
echo "2"
sleep 1
echo "1"
sleep 1
echo "0"

# Activate the virtual environment
echo "Activating virtual env..."
. /web_root/ENV/bin/activate

# Setup Postgresql and Elasticsearch (this deletes your existing database)
echo "Running `python ${ARCHES_ROOT}/manage.py packages -o setup`"
python ${ARCHES_ROOT}/manage.py packages -o setup

# Import resource graphs from default folder (see RESOURCE_GRAPH_LOCATIONS in settings.py)
echo "Running `python ${ARCHES_ROOT}/manage.py packages -o import_graphs`"
python ${ARCHES_ROOT}/manage.py packages -o import_graphs