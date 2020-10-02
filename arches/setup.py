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
    if version[3] != "final":
        mapping = {"alpha": "a", "beta": "b", "rc": "rc"}
        sub = mapping[version[3]] + str(version[4])

    return str(major + sub)


def get_major_version(version=None):
    "Returns major version from VERSION."
    version = get_complete_version(version)
    parts = 3
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


if __name__ == "__main__":
    install()
