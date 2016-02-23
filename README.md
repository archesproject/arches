# Arches [![Build Status](https://travis-ci.org/archesproject/arches.svg?branch=master)](https://travis-ci.org/archesproject/arches) [![Coverage Status](https://coveralls.io/repos/github/archesproject/arches/badge.svg?branch=master)](https://coveralls.io/github/archesproject/arches?branch=master)

A web-based, geospatial information system for cultural heritage inventory and management.

Arches is purpose-built for the international cultural heritage field, and it is designed to record all types of immovable heritage, including archaeological sites, buildings and other historic structures, landscapes, and heritage ensembles or districts.

Please see the [project page](http://archesproject.org/) for more information on the Arches project.

The Arches Installation Guide and Arches User Guide are available [here](http://archesproject.org/documentation/).

## System Requirements

Please note that Arches has been developed for modern browsers. It supports:

* Firefox
* Chrome
* Safari
* Opera
* Internet Explorer 10 or higher.

Minimum system requirements:

* At least 4GB of RAM for evaluation and testing, or 8 to 16GB for production.
* 10GB minimum to install the code base and test dataset, but disk space requirements will vary greatly depending on the size of your dataset

## Dependencies

* PostgreSQL relational database (version 9.3)
* PostGIS (version 2.x) spatial module for PostgreSQL
* Python (version 2.7.6 - there seem to be issues with later versions of python)
* GEOS

These instructions will provide some guidance on installing
the required dependencies and getting Arches up and running quickly:

http://arches3.readthedocs.org/en/latest/installing-dependencies-linux/

http://arches3.readthedocs.org/en/latest/installing-dependencies-windows/

## Installing Arches

For the installation process you will need **pip** installed on your system. If you don't already have it, you can find instructions to install it here: https://pip.pypa.io/en/latest/installing.html

If you have installed the dependencies, you're ready to install Arches.

1. Create the Arches Project folder:

    * Create a folder called 'Projects' (or some other meaningful name) on your system.  

2.  Install virtualenv:

    * Open a command prompt and type:

            $ pip install virtualenv==1.11.4

    * virtualenv creates a directory with it's own installation of Python and Python executables.

3. Create the ENV folder:

    Navigate to your Projects directory (or wherever you named the root Arches folder) and create your virtual environment with the following command:

        $ virtualenv ENV

4. Install Arches:

    * Activate your virtual environment with the following command:

        * On Linux (and other POSIX systems):

                $ source ENV/bin/activate

        * On Windows:

                \path to 'Projects'\ENV\Scripts\activate

    * You should see the name of your virtual environment in parentheses proceeding your command prompt like so `(ENV)`:

            (ENV)$

    Install Arches (your virtual environment must be activated):

            (ENV)$ pip install arches

That's it, you're done.  You should now have a folder structure that looks like this:

    /Projects
        /ENV

## Arches Applications

Generally arches applications are installed in a folder directly under the Arches root folder.  You can install as many Arches applications as you like, and they'll all use the same Arches framework and virtual environment.  A typical Arches application installation will therefore look something like this:

    /Projects
        /ENV (virtual environment where the Arches framework is installed)
        /my_arches_app
        /another_arches_app

**Note:**
    If you want to install an existing Arches application, such as the Heritage Inventory Package (HIP), you should stop here and go to: http://arches-hip.readthedocs.org/en/latest/getting-started/#installation.

## Contributing

Issue reports are encouraged.  [Please read this article](http://polite.technology/reportabug.html) before reporting issues.

Good guidelines on how to contribute can be found [here](https://egghead.io/series/how-to-contribute-to-an-open-source-project-on-github).
