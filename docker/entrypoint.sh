#!/bin/bash

if [[ ! -z ${ARCHES_PROJECT} ]]; then
	PROJECT_ROOT=${ARCHES_ROOT}/${ARCHES_PROJECT}
else
	PROJECT_ROOT=${ARCHES_ROOT}
fi

cd_arches_root() {
	cd ${ARCHES_ROOT}
}

cd_project_root() {
	cd ${PROJECT_ROOT}/${ARCHES_PROJECT}
}

activate_virtualenv() {
	. ${WEB_ROOT}/ENV/bin/activate
}

init_arches() {
	if [[ "${FORCE_DB_INIT}" == "True" ]]; then
		echo ""
		echo "*** Warning: FORCE_DB_INIT = True ***"
		echo "" 
		run_db_init_commands
	elif db_exists; then
		echo "Database ${PGDBNAME} already exists, skipping initialization."
		echo ""
	else
		run_db_init_commands
	fi

	init_arches_projects
}

run_db_init_commands() {
	setup_arches
}

db_exists() {
	echo "Checking if database "${PGDBNAME}" exists..."
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

init_arches_projects() { 
	if [[ ! -z ${ARCHES_PROJECT} ]]; then
		echo "Checking if Arches project "${ARCHES_PROJECT}" exists..."
		if [[ ! -d ${PROJECT_ROOT} ]] || [[ ! "$(ls -A ${PROJECT_ROOT})" ]]; then
			echo "" 
			echo "----- Custom Arches project '${ARCHES_PROJECT}' does not exist. -----"
			echo "----- Creating '${ARCHES_PROJECT}'... -----"
			echo "" 
			
			arches-project create ${ARCHES_PROJECT} --directory ${ARCHES_PROJECT}

			exit_code=$?
			if [[ ${exit_code} != 0 ]]; then
				echo "Something went wrong when creating your Arches project: ${ARCHES_PROJECT}."
				echo "Exiting..."
				exit ${exit_code}
			fi

			move_settings_local
		else
			echo "Custom Arches project '${ARCHES_PROJECT}' already exists."
		fi
	fi
}

move_settings_local() {
	# The settings_local.py in ${ARCHES_ROOT}/arches/ gets ignored if running manage.py from a custom Arches project instead of Arches core app
	if [[ ! -f ${PROJECT_ROOT}/${ARCHES_PROJECT}/settings_local.py ]]; then
		mv ${ARCHES_ROOT}/arches/settings_local.py ${PROJECT_ROOT}/${ARCHES_PROJECT}/settings_local.py
	fi
}

set_dev_mode() {
	python ${ARCHES_ROOT}/setup.py develop
}

install_dev_requirements() {
	echo ""
	echo ""
	echo "----- DJANGO_MODE = DEV, INSTALLING DEV REQUIREMENTS -----"
	echo ""
	pip install -r ${ARCHES_ROOT}/arches/install/requirements_dev.txt
}

run_tests() {
	echo ""
	echo ""
	echo "----- RUNNING ARCHES TESTS -----"
	echo ""
	python manage.py test tests --pattern="*.py" --settings="tests.test_settings"
}

collect_static(){
	echo ""
	echo ""
	echo "----- COLLECTING DJANGO STATIC FILES -----"
	echo ""
	python ${PROJECT_ROOT}/manage.py collectstatic --noinput
}

run_django_server() {
	echo ""
	echo ""
	echo "----- *** RUNNING DJANGO SERVER *** -----"
	echo ""
	exec python ${PROJECT_ROOT}/manage.py runserver 0.0.0.0:8000
}



### Starting point ### 

# Run first commands from ${ARCHES_ROOT}
cd_arches_root
activate_virtualenv
init_arches

if [[ "${DJANGO_MODE}" == "DEV" ]]; then
	set_dev_mode
	install_dev_requirements
fi

run_tests

# From here on, run from ${PROJECT_ROOT}
cd_project_root
if [[ "${DJANGO_MODE}" == "PROD" ]]; then
	collect_static
fi
run_django_server