import re
import subprocess
from django.template import Template
from django.template import Context
from arches.management.commands import utils

postgres_version = subprocess.check_output(["psql", "--version"])
pattern = re.compile(r'\s\d+.\d*.\d*')
matches = pattern.findall(postgres_version)
psqlversionmatch = matches[0]
split = (psqlversionmatch.split('.'))  # major[9].minor[2].patch[0]

# add "0" place holders
if len(split) < 2:  # e.g 9 > 9.0
    split.append(0)
if len(split) < 3:  # e.g 9.1 > 9.1.0
    split.append(0)


def create_sqlfile(database_settings, path_to_file):
    context = Context(database_settings)
    if (split[0] >= 9) & (split[1] >= 2) & (split[2] >= 0):  # 9.2.0 or above
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
        "       CONNECTION LIMIT=-1;\n"
    )
    utils.write_to_file(path_to_file, t.render(context))
