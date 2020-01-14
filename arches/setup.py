import sys
import os
import subprocess
import shutil
import urllib.request, urllib.error, urllib.parse
import zipfile
import datetime
import platform
import tarfile
from arches import settings

here = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(here)


def install():
    # CHECK PYTHON VERSION
    if not sys.version_info >= (3, 7):
        print("ERROR: Arches requires at least Python 3.7")
        sys.exit(101)
    else:
        pass

    return True


def unzip_file(file_name, unzip_location):
    try:
        # first assume you have a .tar.gz file
        tar = tarfile.open(file_name, "r:gz")
        tar.extractall(path=unzip_location)
        tar.close()
    except:
        # next assume you have a .zip file
        with zipfile.ZipFile(file_name, "r") as myzip:
            myzip.extractall(unzip_location)


def get_version(version=None):
    "Returns a PEP 440-compliant version number from VERSION."
    version = get_complete_version(version)

    # Now build the two parts of the version number:
    # major = X.Y[.Z]
    # sub = .devN - for pre-alpha releases
    #     | {a|b|rc}N - for alpha, beta and rc releases

    major = get_major_version(version)

    sub = ""
    if version[3] == "alpha" and version[4] == 0:
        changeset = get_changeset()
        if changeset:
            sub = ".dev%s" % changeset

    elif version[3] != "final":
        mapping = {"alpha": "a", "beta": "b", "rc": "rc"}
        sub = mapping[version[3]] + str(version[4])

    return str(major + sub)


def get_major_version(version=None):
    "Returns major version from VERSION."
    version = get_complete_version(version)
    parts = 2 if version[2] == 0 else 3
    major = ".".join(str(x) for x in version[:parts])
    return major


def get_complete_version(version=None):
    """Returns a tuple of the django version. If version argument is non-empty,
    then checks for correctness of the tuple provided.
    """
    if version is None:
        from arches import VERSION as version
    else:
        assert len(version) == 5
        assert version[3] in ("alpha", "beta", "rc", "final")

    return version


def get_changeset(path_to_file=None):
    import os
    import subprocess
    from io import StringIO
    from management.commands.utils import write_to_file

    sb = StringIO()
    if not path_to_file:
        path_to_file = os.path.abspath(os.path.dirname(__file__))

    ver = ""
    try:
        hg_archival = open(os.path.abspath(os.path.join(here, "..", ".hg_archival.txt")), "r")
        the_file = hg_archival.readlines()
        hg_archival.close()
        node = ""
        latesttag = ""
        date = ""
        for line in the_file:
            if line.startswith("node:"):
                node = line.split(":")[1].strip()[:12]
            if line.startswith("latesttag:"):
                latesttag = line.split(":")[1].strip()
            if line.startswith("date:"):
                date = line.split(":")[1].strip()

        sb.writelines(['__VERSION__="%s"' % latesttag])
        sb.writelines(['\n__BUILD__="%s"' % node])
        ver = "%s:%s" % (latesttag, node)
        ver = date
        # write_to_file(os.path.join(path_to_file,'version.py'), sb.getvalue(), 'w')
    except:
        try:
            ver = subprocess.check_output(["hg", "log", "-r", ".", "--template", "{latesttag}:{node|short}"])
            ver = subprocess.check_output(["hg", "log", "-r", ".", "--template", "{node|short}"])
            ver = subprocess.check_output(["hg", "log", "-r", ".", "--template", "{date}"])
            sb.writelines(['__VERSION__="%s"' % ver.split(":")[0]])
            sb.writelines(['\n__BUILD__="%s"' % ver.split(":")[1]])
            # write_to_file(os.path.join(path_to_file,'version.py'), sb.getvalue(), 'w')
        except:
            pass

    try:
        timestamp = datetime.datetime.utcfromtimestamp(float(ver))
    except ValueError:
        return None
    return timestamp.strftime("%Y%m%d%H%M%S")


if __name__ == "__main__":
    install()
