import sys
import os
import subprocess
import shutil
import urllib2
import zipfile
import datetime
from arches import settings

here = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(here)

def install():
    if confirm_system_requirements():

        run_virtual_environment()

        install_dir = os.path.join(site_packages_dir(), 'arches', 'install')
        django_install_location = os.path.join(site_packages_dir(), 'django')

        # INSTALL DJANGO, RAWES, SPHINX AND OTHER DEPENDENCIES
        tmpinstalldir = os.path.join(site_packages_dir(), 'arches', 'tmp')
        os.system("pip install -b %s setuptools --upgrade" % (tmpinstalldir))
        os.system("pip install -b %s -r %s" % (tmpinstalldir, os.path.join(install_dir, 'requirements.txt')))
        if settings.MODE == 'DEV':
            os.system("pip install -b %s -r %s" % (tmpinstalldir, os.path.join(install_dir, 'requirements_dev.txt')))
        shutil.rmtree(tmpinstalldir, True)

def site_packages_dir():
    if sys.platform == 'win32':
        return os.path.join(sys.prefix, 'Lib', 'site-packages')
    else:
        py_version = 'python%s.%s' % (sys.version_info[0], sys.version_info[1])
        return os.path.join(sys.prefix, 'lib', py_version, 'site-packages')

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
            activate_env(virtualenv_working_dir)
        else:
            os.system("pip install virtualenv")
            virtualenv_working_dir = os.path.join(here, 'virtualenv', env)
            os.system("virtualenv %s" % (virtualenv_working_dir))
            if os.path.exists(virtualenv_working_dir):
                activate_env(virtualenv_working_dir)
            else:
                raise Exception("""\n
            ----------------------------------------------------------------------------------------------------------------------
                ERROR: Arches has to be run within a virtual environment http://virtualenv.readthedocs.org/
            -----------------------------------------------------------------------------------------------------------------------\n""")

def activate_env(path_to_virtual_env):
    # ACIVATE THE VIRTUAL ENV
    if sys.platform == 'win32':
        activate_this = os.path.join(path_to_virtual_env, 'Scripts', 'activate_this.py')
    else:
        activate_this = os.path.join(path_to_virtual_env, 'bin', 'activate_this.py')
    execfile(activate_this, dict(__file__=activate_this))

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

def download_elasticsearch(install_dir):
    url = get_elasticsearch_download_url(install_dir)
    file_name = url.split('/')[-1]
    if not os.path.isfile(os.path.join(install_dir, file_name)):
        download_file(url, os.path.join(install_dir, file_name))

def get_elasticsearch_download_url(install_dir):
    with open(os.path.join(install_dir, "requirements.txt"), "r") as f:
        for line in f:
            if line.startswith('# https://'):
                return line.replace('# ', '').strip()
    raise Exception("""\n
------------------------------------------------------------------------------------------------------
    ERROR: There was an error getting the url for Elastic search from the requirements.txt file
    Make sure the requirements.txt file contains a line similar to the following line,\nincluding the pound symbol (#) but not the double quotes (") and where the x.x.x represent the version number:
        "# https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-x.x.x.zip"
----------------------------------------------------------------------------------------------------\n""")

def get_version(version=None):
    "Returns a PEP 440-compliant version number from VERSION."
    version = get_complete_version(version)

    # Now build the two parts of the version number:
    # major = X.Y[.Z]
    # sub = .devN - for pre-alpha releases
    #     | {a|b|rc}N - for alpha, beta and rc releases

    major = get_major_version(version)

    sub = ''
    if version[3] == 'alpha' and version[4] == 0:
        changeset = get_changeset()
        if changeset:
            sub = '.dev%s' % changeset

    elif version[3] != 'final':
        mapping = {'alpha': 'a', 'beta': 'b', 'rc': 'rc'}
        sub = mapping[version[3]] + str(version[4])

    return str(major + sub)


def get_major_version(version=None):
    "Returns major version from VERSION."
    version = get_complete_version(version)
    parts = 2 if version[2] == 0 else 3
    major = '.'.join(str(x) for x in version[:parts])
    return major


def get_complete_version(version=None):
    """Returns a tuple of the django version. If version argument is non-empty,
    then checks for correctness of the tuple provided.
    """
    if version is None:
        from arches import VERSION as version
    else:
        assert len(version) == 5
        assert version[3] in ('alpha', 'beta', 'rc', 'final')

    return version

def get_changeset(path_to_file=None):
    import os
    import subprocess
    from StringIO import StringIO
    from management.commands.utils import write_to_file

    sb = StringIO()
    if not path_to_file:
        path_to_file =os.path.abspath(os.path.dirname(__file__))

    ver = ''
    try:
        hg_archival = open(os.path.abspath(os.path.join(here, '..', '.hg_archival.txt')),'r')
        the_file = hg_archival.readlines()
        hg_archival.close()
        node = ''
        latesttag = ''
        date = ''
        for line in the_file:
            if line.startswith('node:'):
                node = line.split(':')[1].strip()[:12]
            if line.startswith('latesttag:'):
                latesttag = line.split(':')[1].strip()
            if line.startswith('date:'):
                date = line.split(':')[1].strip()

        sb.writelines(['__VERSION__="%s"' % latesttag])
        sb.writelines(['\n__BUILD__="%s"' % node])
        ver = '%s:%s' % (latesttag, node)
        ver = date
        #write_to_file(os.path.join(path_to_file,'version.py'), sb.getvalue(), 'w')
    except:
        try:
            ver = subprocess.check_output(['hg', 'log', '-r', '.', '--template', '{latesttag}:{node|short}'])
            ver = subprocess.check_output(['hg', 'log', '-r', '.', '--template', '{node|short}'])
            ver = subprocess.check_output(['hg', 'log', '-r', '.', '--template', '{date}'])
            sb.writelines(['__VERSION__="%s"' % ver.split(':')[0]])
            sb.writelines(['\n__BUILD__="%s"' % ver.split(':')[1]])
            #write_to_file(os.path.join(path_to_file,'version.py'), sb.getvalue(), 'w')
        except:
            pass

    try:
        timestamp = datetime.datetime.utcfromtimestamp(float(ver))
    except ValueError:
        return None
    return timestamp.strftime('%Y%m%d%H%M%S')

if __name__ == "__main__":
    install()
