from fabric.api import lcd, local
import os, shutil, sys

VIRTUALENV_PATH = os.path.abspath(os.path.join(os.getcwd(), '..', 'virtualenv', 'ENV'))

# SET THE PYTHON.EXE LOCATION
if sys.platform == 'win32':
    PYTHON = os.path.join(VIRTUALENV_PATH, 'Scripts', 'python')
else:
    PYTHON = os.path.join(VIRTUALENV_PATH, 'bin', 'python')

def get_latest():
    """
    Gets the latest code and updates your system

    """

    os.system('hg pull')
    os.system('hg update')

def virtualenv(task='install'):
    with lcd('arches'):
        if task == 'truncate' or task == 'recreate':
            shutil.rmtree(VIRTUALENV_PATH)
        if task == 'install' or task == 'recreate':
            os.system('python setup.py')

def setup_package(package=''):
    """
    Installs Elasticsearch into the package directory and 
    installs the database into postgres as "arches_<package_name>"

    """

    package_opt = '' if package == '' else '--package %s' % package
    os.system('%s manage.py packages --operation setup %s' % (PYTHON, package_opt))

def install_package(package=''):
    """
    Runs the setup.py file found in the package root

    """

    package_opt = '' if package == '' else '--package %s' % package
    os.system('%s manage.py packages --operation install %s' % (PYTHON, package_opt))

def start_es(package=''):
    """
    Start Elasticsearch. Open another window to run more tasks.
    NOTE: this will block all subsequent python calls.  
    You will need to re-run this file to run more tasks

    """

    package_opt = '' if package == '' else '--package %s' % package
    os.system('%s manage.py packages --operation start_elasticsearch %s' % (PYTHON, package_opt))

def setup(package='', virtualenv_task=None):
    """
    Installs Elasticsearch into the package directory and 
    installs the database into postgres as "arches_<package_name>"
    Starts Elasticsearch.
    Runs the setup.py file found in the package root

    """

    if virtualenv_task:
        virtualenv(virtualenv_task)
    setup_package(package=package)
    start_es(package=package)
    install_package(package=package)

def runserver(package='', port=8000):
    """
    Starts the Django web server on a specific port

    """

    os.system('%s manage.py runserver %s -p %s' % (PYTHON, port, package))

def deploy(virtualenv_task='install'):
    """
    Sets up and installs the package from the latest code available

    """

    if virtualenv_task == 'truncate':
        print 'Cannot truncate virtualenv on deploy without recreating -- switching virtualenv_task to "recreate"'
        virtualenv_task = 'recreate'
    get_latest()
    setup(virtualenv_task)

def dev_setup():
    local('python setup.py')
    with lcd('..'):
        local('%s setup.py develop' % (PYTHON))
