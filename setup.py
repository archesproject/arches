from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding
from os import path
from setuptools.command.install import install


class post_install(install):
    def run(self):
        from arches.setup import install as arches_install

        install.run(self)
        arches_install()


with open("arches/install/requirements.txt") as f:
    requirements = f.read().splitlines()

# Dynamically calculate the version based on arches.VERSION.
version = __import__("arches").__version__

setup(
    name="arches",
    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # http://packaging.python.org/en/latest/tutorial.html#version
    version=version,
    description="Arches is an open-source, web-based, geospatial information system for cultural heritage inventory and management.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="http://archesproject.org/",
    author="Farallon Geographics, Inc",
    author_email="dev@fargeo.com",
    license="GNU AGPL3",
    scripts=["arches/install/arches-project"],
    cmdclass={"install": post_install},
    install_requires=requirements,
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Information Technology",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Framework :: Django :: 1.11",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    # What does your project relate to?
    keywords="django arches cultural heritage",
    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    zip_safe=False,
    test_suite="tests.run_tests.run_all",
)
