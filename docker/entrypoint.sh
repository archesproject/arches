#!/bin/bash

activate_virtualenv() {
	. ${WEB_ROOT}/ENV/bin/activate
}

install_dev_requirements() {
	echo ""
	echo ""
	echo ----- DJANGO_MODE = DEV, so installing additional dev requirements... -----
	echo ""
	pip install -r ${ARCHES_ROOT}/arches/install/requirements_dev.txt
}

run_tests() {
	echo ""
	echo ""
	echo ----- RUNNING ARCHES TESTS -----
	echo ""
	cd ${ARCHES_ROOT}
	python manage.py test tests --pattern="*.py" --settings="tests.test_settings"
}

collect_static(){
	echo ""
	echo ""
	echo ----- Collecting Django static files -----
	echo ""
	python ${ARCHES_ROOT}/manage.py collectstatic --noinput
}

run_django_server() {
	echo ""
	echo ""
	echo ----- *** Running Django server *** -----
	echo ""
	exec python ${ARCHES_ROOT}/manage.py runserver 0.0.0.0:8000
}

### Starting point ### 
activate_virtualenv
if [[ "${DJANGO_MODE}" == "DEV" ]]; then
	install_dev_requirements
elif [[ "${DJANGO_MODE}" == "PROD" ]]; then
	collect_static
fi
run_tests
run_django_server