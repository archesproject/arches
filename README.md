# Arches [![Build Status](https://travis-ci.org/archesproject/arches.svg?branch=master)](https://travis-ci.org/archesproject/arches) [![Coverage Status](https://coveralls.io/repos/github/archesproject/arches/badge.svg?branch=master)](https://coveralls.io/github/archesproject/arches?branch=master)

Arches is a web-based, geospatial information system for cultural heritage inventory and management.

Arches is purpose-built for the international cultural heritage field, and designed to record all types of immovable heritage, including archaeological sites, buildings and other historic structures, landscapes, and heritage ensembles or districts.

For more information and background on the Arches project, please visit [archesproject.org](http://archesproject.org/).

For general inquiries and to get technical support from the wider Arches community, visit our [Google groups forum](https://groups.google.com/forum/#!forum/archesproject).

For general user installation and app documentation, visit [arches4.readthedocs.io](https://arches4.readthedocs.io/en/latest).

For developers interested in installing Arches or in more technical, visit [this repo's wiki](https://github.com/archesproject/arches/wiki). You will also find info on how to contribute to the repo.

Issue reports are encouraged.  [Please read this article](http://polite.technology/reportabug.html) before reporting issues.

#### Quick Install

Installation is fully documented in the wiki, but assuming you have all of the dependencies installed you should make a virtual environment, activate it, and then run

    pip install arches
    
then

    arches-project create myproject
    
enter the new `myproject` directory

    cd myproject
    
and run

    python manage.py runserver
    
and visit `localhost:8000` in a browser (only Chrome is fully supported at this time).

If you run into problems, please review the full installation documentation [here in the wiki](https://github.com/archesproject/arches/wiki/Developer-Installation)
