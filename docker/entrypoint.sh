#!/bin/bash

activate_virtualenv() {
	. ${WEB_ROOT}/ENV/bin/activate
}

init_arches() {
	if [[ "${FORCE_DB_INIT}" == "True" ]]; then
		echo ""
		echo "*** Warning: FORCE_DB_INIT = True ***"
		echo "" 
		run_arches_init_commands
	elif db_exists; then
		echo "Database ${PGDBNAME} already exists, skipping initialization."
	else
		run_arches_init_commands
	fi
}

run_arches_init_commands() {
	setup_arches
	import_graphs
	import_reference_data 'arches/db/schemes/arches_concept_scheme.rdf'
}

db_exists() {
	psql -lqt -h $PGHOST -U postgres | cut -d \| -f 1 | grep -qw ${PGDBNAME}
}

setup_arches() {
	# Setup Postgresql and Elasticsearch (this deletes your existing database)
	
	echo "" && echo "" 
	echo "*** Initializing database ***" 
	echo "" 
	echo "*** Any existing Arches database will be deleted ***"
	echo "" && echo "" 

	echo "5" && sleep 1 && echo "4" && sleep 1 && echo "3" && sleep 1 && echo "2" && sleep 1 &&	echo "1" &&	sleep 1 && echo "0" && echo "" 

	echo "Running: python ${ARCHES_ROOT}/manage.py packages -o setup"
	python ${ARCHES_ROOT}/manage.py packages -o setup
}

import_graphs() {
	# Import resource graphs from default folder (see RESOURCE_GRAPH_LOCATIONS in settings.py)
	echo "Running: python ${ARCHES_ROOT}/manage.py packages -o import_graphs"
	python ${ARCHES_ROOT}/manage.py packages -o import_graphs
}

import_reference_data() {
	# Import example concept schemes
	local rdf_file="$1"
	echo "Running: python ${ARCHES_ROOT}/manage.py packages -o import_reference_data -s \"${rdf_file}\""
	python ${ARCHES_ROOT}/manage.py packages -o import_reference_data -s "${rdf_file}"
}

set_dev_mode() {
	python ${ARCHES_ROOT}/setup.py develop
}

install_dev_requirements() {
	echo ""
	echo ""
	echo "----- DJANGO_MODE = DEV, so installing additional dev requirements... -----"
	echo ""
	pip install -r ${ARCHES_ROOT}/arches/install/requirements_dev.txt
}

run_tests() {
	echo ""
	echo ""
	echo "----- RUNNING ARCHES TESTS -----"
	echo ""
	cd ${ARCHES_ROOT}
	python manage.py test tests --pattern="*.py" --settings="tests.test_settings"
}

collect_static(){
	echo ""
	echo ""
	echo "----- Collecting Django static files -----"
	echo ""
	python ${ARCHES_ROOT}/manage.py collectstatic --noinput
}

run_django_server() {
	echo ""
	echo ""
	echo "----- *** Running Django server *** -----"
	echo ""
	exec python ${ARCHES_ROOT}/manage.py runserver 0.0.0.0:8000
}



### Starting point ### 
activate_virtualenv
init_arches
if [[ "${DJANGO_MODE}" == "DEV" ]]; then
	set_dev_mode
	install_dev_requirements
elif [[ "${DJANGO_MODE}" == "PROD" ]]; then
	collect_static
fi
run_tests
run_django_server