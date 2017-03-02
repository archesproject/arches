#!/bin/bash

echo "" 
echo "" 
echo "*** Initializing database ***" 
echo "" 
echo "*** Any existing Arches database will be deleted ***"
echo "" 
echo "" 

# Activate the virtual environment
. /web_root/ENV/bin/activate

# Setup Postgresql and Elasticsearch (this deletes your existing database)
python ${ARCHES_ROOT}/manage.py packages -o setup

# Import resource graphs from default folder (see RESOURCE_GRAPH_LOCATIONS in settings.py)
python ${ARCHES_ROOT}/manage.py packages -o import_graphs