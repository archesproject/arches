#!/bin/bash

HELP_TEXT="

Arguments:
	run_arches: Default. Run the Arches server
	run_tests: Run unit tests
	setup_arches: Delete any existing Arches database and set up a fresh one
	-h or help: Display help text
"

display_help() {
	echo "${HELP_TEXT}"
}



CUSTOM_SCRIPT_FOLDER=${CUSTOM_SCRIPT_FOLDER:-/docker/entrypoint}
if [[ -z ${ARCHES_PROJECT} ]]; then
	APP_FOLDER=${ARCHES_ROOT}
	PACKAGE_JSON_FOLDER=${ARCHES_ROOT}/arches/install
else
	APP_FOLDER=${WEB_ROOT}/${ARCHES_PROJECT}
	# due to https://github.com/archesproject/arches/issues/4841, changes were made to yarn install
	# and module deployment. Using the arches install directory for yarn.
	PACKAGE_JSON_FOLDER=${ARCHES_ROOT}/arches/install
fi

# Read modules folder from yarn config file
# Get string after '--install.modules-folder' -> get first word of the result 
# -> remove line endlings -> trim quotes -> trim leading ./
YARN_MODULES_FOLDER=${PACKAGE_JSON_FOLDER}/$(awk \
	-F '--install.modules-folder' '{print $2}' ${PACKAGE_JSON_FOLDER}/.yarnrc \
	| awk '{print $1}' \
	| tr -d $'\r' \
	| tr -d '"' \
	| sed -e "s/^\.\///g")

export DJANGO_PORT=${DJANGO_PORT:-8000}
COUCHDB_URL="http://$COUCHDB_USER:$COUCHDB_PASS@$COUCHDB_HOST:$COUCHDB_PORT"
STATIC_ROOT=${STATIC_ROOT:-/static_root}


cd_web_root() {
	cd ${WEB_ROOT}
	echo "Current work directory: ${WEB_ROOT}"
}

cd_arches_root() {
	cd ${ARCHES_ROOT}
	echo "Current work directory: ${ARCHES_ROOT}"
}

cd_app_folder() {
	cd ${APP_FOLDER}
	echo "Current work directory: ${APP_FOLDER}"
}

cd_yarn_folder() {
	cd ${PACKAGE_JSON_FOLDER}
	echo "Current work directory: ${PACKAGE_JSON_FOLDER}"
}

activate_virtualenv() {
	. ${WEB_ROOT}/ENV/bin/activate
}




#### Install

init_arches() {
	if db_exists; then
		echo "Database ${PGDBNAME} already exists, skipping initialization."
		echo ""
	else
		echo "Database ${PGDBNAME} does not exists yet, starting setup..."
		setup_arches
	fi

	init_arches_project
}


# Setup Postgresql and Elasticsearch
setup_arches() {
	cd_arches_root

	echo "" && echo ""
	echo "*** Initializing database ***"
	echo ""
	echo "*** Any existing Arches database will be deleted ***"
	echo "" && echo ""

	echo "5" && sleep 1 && echo "4" && sleep 1 && echo "3" && sleep 1 && echo "2" && sleep 1 &&	echo "1" &&	sleep 1 && echo "0" && echo ""

	echo "Running: python manage.py setup_db --force"
	python manage.py setup_db --force

    echo "Running: Creating couchdb system databases"
    curl -X PUT ${COUCHDB_URL}/_users
    curl -X PUT ${COUCHDB_URL}/_global_changes
    curl -X PUT ${COUCHDB_URL}/_replicator

	if [[ "${INSTALL_DEFAULT_GRAPHS}" == "True" ]]; then
		# Import graphs
		if ! graphs_exist; then
			echo "Running: python manage.py packages -o import_graphs"
			python manage.py packages -o import_graphs
		else
			echo "Graphs already exist in the database. Skipping 'import_graphs'."
		fi
	fi


	if [[ "${INSTALL_DEFAULT_CONCEPTS}" == "True" ]]; then
		# Import concepts
		if ! concepts_exist; then
			import_reference_data arches/db/schemes/arches_concept_scheme.rdf
		else
			echo "Concepts already exist in the database."
			echo "Skipping 'arches_concept_scheme.rdf'."
			echo "Skipping 'cvast_concept_scheme.rdf'."
		fi

		# Import collections
		if ! collections_exist; then
			import_reference_data arches/db/schemes/arches_concept_collections.rdf
		else
			echo "Collections already exist in the database."
			echo "Skipping 'import_reference_data arches_concept_collections.rdf'."
		fi
	fi

	run_migrations
}

wait_for_db() {
	echo "Testing if database server is up..."
	while [[ ! ${return_code} == 0 ]]
	do
        psql --host=${PGHOST} --port=${PGPORT} --user=${PGUSERNAME} --dbname=postgres -c "select 1" >&/dev/null
		return_code=$?
		sleep 1
	done
	echo "Database server is up"

    echo "Testing if Elasticsearch is up..."
    while [[ ! ${return_code} == 0 ]]
    do
        curl -s "http://${ESHOST}:${ESPORT}/_cluster/health?wait_for_status=green&timeout=60s" >&/dev/null
        return_code=$?
        sleep 1
    done
    echo "Elasticsearch is up"
}

db_exists() {
	echo "Checking if database "${PGDBNAME}" exists..."
	count=`psql --host=${PGHOST} --port=${PGPORT} --user=${PGUSERNAME} --dbname=postgres -Atc "SELECT COUNT(*) FROM pg_catalog.pg_database WHERE datname='${PGDBNAME}'"`

	# Check if returned value is a number and not some error message
	re='^[0-9]+$'
	if ! [[ ${count} =~ $re ]] ; then
	   echo "Error: Something went wrong when checking if database "${PGDBNAME}" exists..." >&2;
	   echo "Exiting..."
	   exit 1
	fi

	# Return 0 (= true) if database exists
	if [[ ${count} > 0 ]]; then
		return 0
	else
		return 1
	fi
}

set_dev_mode() {
	echo ""
	echo ""
	echo "----- SETTING DEV MODE -----"
	echo ""
	cd_arches_root
	python ${ARCHES_ROOT}/setup.py develop
}


# Yarn
init_yarn_components() {
	if [[ ! -d ${YARN_MODULES_FOLDER} ]] || [[ ! "$(ls ${YARN_MODULES_FOLDER})" ]]; then
		echo "Yarn modules do not exist, installing..."
		install_yarn_components
	fi
}

# This is also done in Dockerfile, but that does not include user's custom Arches app package.json
# Also, the packages folder may have been overlaid by a Docker volume.
install_yarn_components() {
	echo ""
	echo ""
	echo "----- INSTALLING YARN COMPONENTS -----"
	echo ""
	cd_yarn_folder
	yarn install
}


#### Misc

init_arches_project() {
	if [[ ! -z ${ARCHES_PROJECT} ]]; then
		echo "Checking if Arches project "${ARCHES_PROJECT}" exists..."
		if [[ ! -d ${APP_FOLDER} ]] || [[ ! "$(ls ${APP_FOLDER})" ]]; then
			echo ""
			echo "----- Custom Arches project '${ARCHES_PROJECT}' does not exist. -----"
			echo "----- Creating '${ARCHES_PROJECT}'... -----"
			echo ""

			cd_web_root
			[[ -d ${APP_FOLDER} ]] || mkdir ${APP_FOLDER}

			arches-project create ${ARCHES_PROJECT} --directory ${ARCHES_PROJECT}

			exit_code=$?
			if [[ ${exit_code} != 0 ]]; then
				echo "Something went wrong when creating your Arches project: ${ARCHES_PROJECT}."
				echo "Exiting..."
				exit ${exit_code}
			fi

			copy_settings_local
		else
			echo "Custom Arches project '${ARCHES_PROJECT}' already exists."
		fi
	fi
}


graphs_exist() {
	row_count=$(psql -h ${PGHOST} -p ${PGPORT} -U postgres -d ${PGDBNAME} -Atc "SELECT COUNT(*) FROM public.graphs")
	if [[ ${row_count} -le 3 ]]; then
		return 1
	else
		return 0
	fi
}

concepts_exist() {
	row_count=$(psql -h ${PGHOST} -p ${PGPORT} -U postgres -d ${PGDBNAME} -Atc "SELECT COUNT(*) FROM public.concepts WHERE nodetype = 'Concept'")
	if [[ ${row_count} -le 2 ]]; then
		return 1
	else
		return 0
	fi
}

collections_exist() {
	row_count=$(psql -h ${PGHOST} -p ${PGPORT} -U postgres -d ${PGDBNAME} -Atc "SELECT COUNT(*) FROM public.concepts WHERE nodetype = 'Collection'")
	if [[ ${row_count} -le 1 ]]; then
		return 1
	else
		return 0
	fi
}

import_reference_data() {
	# Import example concept schemes
	local rdf_file="$1"
	echo "Running: python manage.py packages -o import_reference_data -s \"${rdf_file}\""
	python manage.py packages -o import_reference_data -s "${rdf_file}"
}

copy_settings_local() {
	# The settings_local.py in ${ARCHES_ROOT}/arches/ gets ignored if running manage.py from a custom Arches project instead of Arches core app
	echo "Copying ${ARCHES_ROOT}/arches/settings_local.py to ${APP_FOLDER}/${ARCHES_PROJECT}/settings_local.py..."
	cp ${ARCHES_ROOT}/arches/settings_local.py ${APP_FOLDER}/${ARCHES_PROJECT}/settings_local.py
}

# Allows users to add scripts that are run on startup (after this entrypoint)
run_custom_scripts() {
	for file in ${CUSTOM_SCRIPT_FOLDER}/*; do
		if [[ -f ${file} ]]; then
			echo ""
			echo ""
			echo "----- RUNNING CUSTUM SCRIPT: ${file} -----"
			echo ""
			source ${file}
		fi
	done
}




#### Run

run_migrations() {
	echo ""
	echo ""
	echo "----- RUNNING DATABASE MIGRATIONS -----"
	echo ""
	cd_app_folder
	python manage.py migrate
}

collect_static(){
	echo ""
	echo ""
	echo "----- COLLECTING DJANGO STATIC FILES -----"
	echo ""
	cd_app_folder
	python manage.py collectstatic --noinput
}


run_django_server() {
	echo ""
	echo ""
	echo "----- *** RUNNING DJANGO DEVELOPMENT SERVER *** -----"
	echo ""
	cd_app_folder
	exec python manage.py runserver 0.0.0.0:${DJANGO_PORT}
}


run_gunicorn_server() {
	echo ""
	echo ""
	echo "----- *** RUNNING GUNICORN PRODUCTION SERVER *** -----"
	echo ""
	cd_app_folder
	
	if [[ ! -z ${ARCHES_PROJECT} ]]; then
        gunicorn arches.wsgi:application \
            --config ${ARCHES_ROOT}/gunicorn_config.py \
            --pythonpath ${ARCHES_PROJECT}
	else
        gunicorn arches.wsgi:application \
            --config ${ARCHES_ROOT}/gunicorn_config.py
    fi
}



#### Main commands
run_arches() {

	init_arches

	init_yarn_components

	if [[ "${DJANGO_MODE}" == "DEV" ]]; then
		set_dev_mode
	fi

	run_custom_scripts

	if [[ "${DJANGO_MODE}" == "DEV" ]]; then
		run_django_server
	elif [[ "${DJANGO_MODE}" == "PROD" ]]; then
		collect_static
		run_gunicorn_server
	fi
}


run_tests() {
	set_dev_mode
	echo ""
	echo ""
	echo "----- RUNNING ARCHES TESTS -----"
	echo ""
	cd_arches_root
	python manage.py test tests --pattern="*.py" --settings="tests.test_settings" --exe
	if [ $? -ne 0 ]; then
        echo "Error: Not all tests ran succesfully."
		echo "Exiting..."
        exit 1
	fi
}




### Starting point ###

activate_virtualenv

# Use -gt 1 to consume two arguments per pass in the loop (e.g. each
# argument has a corresponding value to go with it).
# Use -gt 0 to consume one or more arguments per pass in the loop (e.g.
# some arguments don't have a corresponding value to go with it, such as --help ).

# If no arguments are supplied, assume the server needs to be run
if [[ $#  -eq 0 ]]; then
	run_arches
fi

# Else, process arguments
echo "Full command: $@"
while [[ $# -gt 0 ]]
do
	key="$1"
	echo "Command: ${key}"

	case ${key} in
		run_arches)
			wait_for_db
			run_arches
		;;
		setup_arches)
			wait_for_db
			setup_arches
		;;
		run_tests)
			wait_for_db
			run_tests
		;;
		run_migrations)
			wait_for_db
			run_migrations
		;;
		install_yarn_components)
			install_yarn_components
		;;
		help|-h)
			display_help
		;;
		*)
            cd_app_folder
			"$@"
			exit 0
		;;
	esac
	shift # next argument or value
done
