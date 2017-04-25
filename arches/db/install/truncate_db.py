import os
import inspect
import subprocess
from django.template import Template
from django.template import Context
from arches.management.commands import utils

def create_sqlfile(database_settings, path_to_file):
	context = Context(database_settings)

	postgres_version = subprocess.check_output(["psql", "--version"])
	if int(postgres_version.split('.')[1]) >= 2:
		context['PID'] = "pid"
	else:
		context['PID'] = "procpid"

	t = Template(
	"SELECT pg_terminate_backend({{ PID }}) from pg_stat_activity where datname='{{ NAME }}';\n"
	"\n"

	"DROP DATABASE IF EXISTS {{ NAME }};\n"
	"\n"

	"CREATE DATABASE {{ NAME }}\n"
	"  WITH ENCODING='UTF8'\n"
	"       OWNER={{ USER }}\n"
	"       CONNECTION LIMIT=-1;\n"
	"\n"
	)

	utils.write_to_file(path_to_file, t.render(context));



