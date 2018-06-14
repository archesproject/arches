# Arches [![Build Status](https://travis-ci.org/archesproject/arches.svg?branch=master)](https://travis-ci.org/archesproject/arches) [![Coverage Status](https://coveralls.io/repos/github/archesproject/arches/badge.svg?branch=master)](https://coveralls.io/github/archesproject/arches?branch=master)

Arches is a web-based, geospatial information system for cultural heritage inventory and management. Arches is purpose-built for the international cultural heritage field, and designed to record all types of immovable heritage, including archaeological sites, buildings and other historic structures, landscapes, and heritage ensembles or districts. For more information and background on the Arches project, please visit [archesproject.org](http://archesproject.org/).

For general inquiries and to get technical support from the wider Arches community, visit our [Google groups forum](https://groups.google.com/forum/#!forum/archesproject).

For the official Arches documentation of the most recent stable release, visit [arches.readthedocs.io/en/stable](https://arches.readthedocs.io/en/stable).

For the documentation pertaining to the bleeding edge code (what is in the ``master`` branch), visit [arches.readthedocs.io/en/latest](https://arches.readthedocs.io/en/latest).

Note that we are trying to pare down the contents of [this repo's wiki](https://github.com/archesproject/arches/wiki) in order to consolidate content into readthedocs, but for the time being interested developers can still find relevant information there.

Issue reports are encouraged! [Please read this article](http://polite.technology/reportabug.html) before reporting issues.

[Version 4.1.1 release notes](https://github.com/archesproject/arches/blob/stable/4.1.x/releases/4.1.1.md)

#### Quick Install

Installation is fully documented in the official documentation, [arches.readthedocs.io/en/stable](https://arches.readthedocs.io/en/stable), but assuming you have all of the dependencies installed you should make a virtual environment, activate it, and then run

    pip install arches --no-binary :all:
    
then

    arches-project create myproject
    
enter the new `myproject` directory

    cd myproject

and run

    python manage.py packages -o setup_db
    python manage.py runserver
    
and visit `localhost:8000` in a browser (only Chrome is fully supported at this time).

If you run into problems, please review our the full [installation documentation](http://arches.readthedocs.io/en/stable/installation/)

#### Release Cycle

Our general release cycle will typically be a functional release (either major if there are backward incompatible changes or minor, if there are not) followed in 6-12 weeks by a bug release (patch). See [semver.org](https://semver.org/) for version numbering.

-   Functional releases will usually introduce new functionality to the application but could also include styling updates, enhancements to the UX, bug fixes, and general improvements.
-   Bug releases are really only concerned with fixing any bugs related to the previous release or any other issues not yet addressed

##### Support for previous releases

Functional releases will be supported until the next functional release. After that users are expected to upgrade to the latest release on [pypi.python.org](https://pypi.python.org/pypi/arches)


#### A test for a PR we're gonna throw away

As tempted as I am to cut up here, well, it's best to keep things professional. Alas. Anyway, this PR will be rejected if Legion GIS's fork is broken in the way we think it is. n ts n ts n ts
