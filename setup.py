
from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding
from os import path
from setuptools.command.install import install
from arches.setup import import get_version

try:
    from arches.setup import install as arches_install
except ImportError:
    arches_install = lambda: None

class post_install(install):
    def run(self):
        install.run(self)
        arches_install()


execfile(path.join('arches', 'version.py'))

setup(
    name='arches',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # http://packaging.python.org/en/latest/tutorial.html#version
    version='3.0.16',

    description='Arches is a new, open-source, web-based, geospatial information system for cultural heritage inventory and management.',
    long_description=open('README.txt').read(),
    url='http://archesproject.org/',
    author='Farallon Geographics, Inc',
    author_email='dev@fargeo.com',
    license='GNU AGPL',

    cmdclass={'install': post_install},

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],

    # What does your project relate to?
    keywords='django arches cultural heritage',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=("packages",'tests',)),

    include_package_data = True,

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'arches_install=arches.setup:install',
        ],
    },

    setup_requires=["hgtools"],

    zip_safe=True,
)