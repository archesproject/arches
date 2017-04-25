import subprocess
from arches.app.models.system_settings import settings

def execute_sql_file(pathtofile, database='default'):
	database = settings.DATABASES[database]
	proc = subprocess.Popen(["psql", "-h", database['HOST'], "-p", database['PORT'], "-U", database['USER'], "-d", database['NAME'], "-f", pathtofile],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
	output, errors = proc.communicate()
	return output