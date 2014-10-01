import sys
import os
import subprocess
import shutil
import urllib2
import zipfile

env_name = 'ENV'

here = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(here)
install_dir = os.path.join(here, 'install')


def install():
    if confirm_system_requirements():

        run_virtual_environment()

        # INSTALL DJANGO, RAWES, SPHINX AND OTHER DEPENDENCIES
        tmpinstalldir = '%s/tmp' % (here)
        os.system("pip install -b %s setuptools --no-use-wheel --upgrade" % (tmpinstalldir))
        os.system("pip install -b %s -r %s" % (tmpinstalldir, os.path.join(install_dir, 'requirements.txt')))
        shutil.rmtree(tmpinstalldir, True)

        #INSTALLING CUSTOM DJANGO EDITS/PATCHES
        if sys.platform == 'win32':
            shutil.copy2(os.path.join(install_dir, 'django_overrides', 'base.py'), os.path.join(sys.prefix, 'Lib', 'site-packages', 'django', 'db', 'backends', 'postgresql_psycopg2'))
            shutil.copy2(os.path.join(install_dir, 'django_overrides', 'creation.py'), os.path.join(sys.prefix, 'Lib', 'site-packages', 'django', 'db', 'backends', 'postgresql_psycopg2'))
            shutil.copy2(os.path.join(install_dir, 'django_overrides', 'inspectdb.py'), os.path.join(sys.prefix, 'Lib', 'site-packages', 'django', 'core', 'management', 'commands'))
            shutil.copy2(os.path.join(install_dir, 'django_overrides', 'admin.py'), os.path.join(sys.prefix, 'Lib', 'site-packages', 'django', 'contrib', 'auth'))
            shutil.copy2(os.path.join(install_dir, 'django_overrides', 'models.py'), os.path.join(sys.prefix, 'Lib', 'site-packages', 'django', 'contrib', 'auth'))
            shutil.copy2(os.path.join(install_dir, 'django_overrides', 'widgets.css'), os.path.join(sys.prefix, 'Lib', 'site-packages', 'django', 'contrib', 'admin', 'static', 'admin', 'css'))
        else:
            py_version = 'python%s.%s' % (sys.version_info[0], sys.version_info[1])
            shutil.copy2(os.path.join(install_dir, 'django_overrides', 'base.py'), os.path.join(sys.prefix, 'lib', py_version, 'site-packages', 'django', 'db', 'backends', 'postgresql_psycopg2'))
            shutil.copy2(os.path.join(install_dir, 'django_overrides', 'creation.py'), os.path.join(sys.prefix, 'lib', py_version, 'site-packages', 'django', 'db', 'backends', 'postgresql_psycopg2'))
            shutil.copy2(os.path.join(install_dir, 'django_overrides', 'inspectdb.py'), os.path.join(sys.prefix, 'lib', py_version, 'site-packages', 'django', 'core', 'management', 'commands'))
            shutil.copy2(os.path.join(install_dir, 'django_overrides', 'admin.py'), os.path.join(sys.prefix, 'lib', py_version, 'site-packages', 'django', 'contrib', 'auth'))
            shutil.copy2(os.path.join(install_dir, 'django_overrides', 'models.py'), os.path.join(sys.prefix, 'lib', py_version, 'site-packages', 'django', 'contrib', 'auth'))
            shutil.copy2(os.path.join(install_dir, 'django_overrides', 'widgets.css'), os.path.join(sys.prefix, 'lib', py_version, 'site-packages', 'django', 'contrib', 'admin', 'static', 'admin', 'css'))

        # INSTALL PSYCOPG2
        if sys.platform == 'win32':
            is_64bit_python = sys.maxsize > 2**32

            if os.path.exists('C:\Program Files (x86)') and is_64bit_python:
                os.system("easy_install http://www.stickpeople.com/projects/python/win-psycopg/psycopg2-2.4.5.win-amd64-py2.7-pg9.1.3-release.exe")
            else:
                os.system("easy_install http://www.stickpeople.com/projects/python/win-psycopg/psycopg2-2.4.5.win32-py2.7-pg9.1.3-release.exe")
        else:
            # SYSTEM IS ASSUMED LINUX/OSX ETC...
            # Install psycopg2 through pip - Works fine if the correct header files are present
            # See http://goshawknest.wordpress.com/2011/02/16/how-to-install-psycopg2-under-virtualenv/
            os.system("pip install psycopg2")
            pass

        download_elasticsearch()
        get_version()

def confirm_system_requirements():
    # CHECK PYTHON VERSION
    if sys.version_info < (2, 7) or sys.version_info >= (3, 0):
        print('ERROR: Arches requires Python 2.7.x')
        sys.exit(101)
    else:
        pass

    # CHECK POSTGRES VERSION
    try:
        postgres_version = subprocess.check_output(["psql", "--version"])
    except OSError:
        print('ERROR: Arches requires psql. Please install and then rerun this file again.')
        sys.exit(101)
    if postgres_version.find("9.") == -1:
        print('ERROR: Arches requires Postgres 9.0 or greater')
        print('Version detected: %s\n' % (postgres_version))
        postgres_override = raw_input('Would like to continue anyway?\nPress Y for Yes or N for No:')
        if(postgres_override == 'Y' or postgres_override == 'y'):
            pass
        else:
            sys.exit(101)
    else:
        pass

    return True

def run_virtual_environment(env='ENV'):
    # is the site running in a virtual environment?
    if hasattr(sys, 'real_prefix'):
        pass # we're running in a virtualenv
    else:
        # Are we a developer who has access to the included virtual env?
        # If so, then try to install and activate the virtual env
        virtualenv_root = os.path.join(root_dir, 'virtualenv')            
        if os.path.exists(os.path.join(virtualenv_root, 'virtualenv.py')):
            virtualenv_working_dir = os.path.join(virtualenv_root, env)
            os.system("python %s %s" % (os.path.join(virtualenv_root, 'virtualenv.py'), virtualenv_working_dir))

            # ACIVATE THE VIRTUAL ENV
            if sys.platform == 'win32':
                activate_this = os.path.join(virtualenv_working_dir, 'Scripts', 'activate_this.py')
            else:
                activate_this = os.path.join(virtualenv_working_dir, 'bin', 'activate_this.py')
            execfile(activate_this, dict(__file__=activate_this))
        else:
            os.system("pip install virtualenv")
            virtualenv_working_dir = os.path.join(here, 'virtualenv', env)
            os.system("virtualenv %s" % (virtualenv_working_dir))
            if os.path.exists(virtualenv_working_dir):
                # ACIVATE THE VIRTUAL ENV
                if sys.platform == 'win32':
                    activate_this = os.path.join(virtualenv_working_dir, 'Scripts', 'activate_this.py')
                else:
                    activate_this = os.path.join(virtualenv_working_dir, 'bin', 'activate_this.py')
                execfile(activate_this, dict(__file__=activate_this))
            else:
                raise Exception("""\n
            ----------------------------------------------------------------------------------------------------------------------
                ERROR: Arches has to be run within a virtual environment http://virtualenv.readthedocs.org/
            -----------------------------------------------------------------------------------------------------------------------\n""")

# INSTALL ELASTICSEARCH and HEAD plugin
def download_file(url, file_name):
    u = urllib2.urlopen(url)
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (file_name, file_size)

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print status,

    f.close()

def unzip_file(file_name, unzip_location):
    with zipfile.ZipFile(file_name, 'r') as myzip:
        print 'unzipping %s to: %s' % (file_name, unzip_location)
        myzip.extractall(unzip_location)

def download_elasticsearch():
    url = get_elasticsearch_download_url()
    file_name = url.split('/')[-1]
    if not os.path.isfile(os.path.join(install_dir, file_name)):
        download_file(url, os.path.join(install_dir, file_name))

def get_elasticsearch_download_url():
    with open(os.path.join(install_dir, "requirements.txt"), "r") as f:
        for line in f:
            if line.startswith('# https://'):
                return line.replace('# ', '').strip()
    raise Exception("""\n
------------------------------------------------------------------------------------------------------
    ERROR: There was an error getting the url for Elastic search from the requirements.txt file
    Make sure the requirements.txt file contains a line similar to the following line,\nincluding the pound symbol (#) but not the double quotes (") and where the x.x.x represent the version number:
        "# https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-x.x.x.zip"
----------------------------------------------------------------------------------------------------\n""") 

def get_version():
    import os
    import subprocess
    from StringIO import StringIO
    from management.commands.utils import write_to_file

    sb = StringIO()
    here = os.path.abspath(os.path.dirname(__file__))
    ver = ''
    try:
        hg_archival = open(os.path.abspath(os.path.join(here, '..', '.hg_archival.txt')),'r')
        the_file = hg_archival.readlines()
        hg_archival.close()
        node = ''
        latesttag = ''
        for line in the_file:
            if line.startswith('node:'):
                node = line.split(':')[1].strip()[:12]
            if line.startswith('latesttag:'):
                latesttag = line.split(':')[1].strip()
    
        sb.writelines(['__VERSION__="%s"' % latesttag])   
        sb.writelines(['\n__BUILD__="%s"' % node])  
        ver = '%s:%s' % (latesttag, node)
        write_to_file(os.path.join(here,'version.py'), sb.getvalue(), 'w')
    except:
        try:
            ver = subprocess.check_output(['hg', 'log', '-r', '.', '--template', '{latesttag}:{node|short}'])
            sb.writelines(['__VERSION__="%s"' % ver.split(':')[0]])
            sb.writelines(['\n__BUILD__="%s"' % ver.split(':')[1]]) 
            write_to_file(os.path.join(here,'version.py'), sb.getvalue(), 'w')
        except:
            pass
    return ver

if __name__ == "__main__":
    install()