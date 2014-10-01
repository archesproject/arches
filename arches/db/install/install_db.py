import inspect
import posixpath
import os
import glob
from django.template import Template
from django.conf import settings
from django.template import Context
from arches.management.commands import utils

def create_sqlfile(database_settings):
	db_directory = os.path.join(settings.ROOT_DIR,'db')

	context = Context(database_settings)
	# context['DB_TRUNCATE_FILE'] = os.path.join(cwd, "truncate_db.sql")
	# context['DB_INSTALL_FILE'] = os.path.join(cwd, "install_db.sql")

	def source(file):
	    return "\i \'" + file + "\'\n"

	# Generate a sql file that sources all necessary sql files into one file
	buffer = ''
	buffer = buffer + "\n-- Run all the sql scripts in the dependencies folder\n"
	for infile in glob.glob(posixpath.join(db_directory, 'install', 'dependencies', '*.sql') ):
		buffer = buffer + source(infile.replace("\\", posixpath.sep))
		    
	buffer = buffer + "\n-- Reload all managed schemas\n"
	for infile in glob.glob( posixpath.join(db_directory, 'ddl', '*.sql') ):
	    buffer = buffer + source(infile.replace("\\", posixpath.sep))

	buffer = buffer + "\n-- Add all the data in the dml folder\n"
	for infile in glob.glob( posixpath.join(db_directory, 'dml', '*.sql') ):
	    buffer = buffer + source(infile.replace("\\", posixpath.sep))
	        
	buffer = buffer + "\n-- Run all the sql in teh postdeployment folder\n"
	for infile in glob.glob( posixpath.join(db_directory, 'install', 'postdeployment', '*.sql') ):
	    buffer = buffer + source(infile.replace("\\", posixpath.sep))

	buffer = buffer + "\n-- Spring cleaning\n"
	buffer = buffer + "VACUUM ANALYZE;\n"

	utils.write_to_file(os.path.join(db_directory, 'install', 'install_db.sql'), buffer)


# #Write a caller for windows
# t = Template(
# ":: delete all managed schemas\n"
# "psql -h {{ HOST }} -p {{ PORT }} -U {{ USER }} -d postgres -f \"{{ DB_TRUNCATE_FILE }}\"\n"
# "\n"
# ":: recreate the database\n"
# "psql -h {{ HOST }} -p {{ PORT }} -U {{ USER }} -d {{ NAME }} -f \"{{ DB_INSTALL_FILE }}\"\n"
# )
# utils.write_to_file(os.path.join(cwd, "install_db.bat"), t.render(context));

# #Write a caller for nix
# t = Template(
# "#!/bin/bash\n"
# "# delete all managed schemas\n"
# "psql -h {{ HOST }} -p {{ PORT }} -U {{ USER }} -d postgres -f \"{{ DB_TRUNCATE_FILE }}\"\n"
# "\n"
# "# recreate the database\n"
# "psql -h {{ HOST }} -p {{ PORT }} -U {{ USER }} -d {{ NAME }} -f \"{{ DB_INSTALL_FILE }}\"\n"
# )
# utils.write_to_file(os.path.join(cwd, "install_db.sh"), t.render(context));
