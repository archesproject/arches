# Arches [![Build Status](https://travis-ci.org/archesproject/arches.svg?branch=master)](https://travis-ci.org/archesproject/arches) [![Coverage Status](https://coveralls.io/repos/github/archesproject/arches/badge.svg?branch=master)](https://coveralls.io/github/archesproject/arches?branch=master)

Arches is a web-based, geospatial information system for cultural heritage inventory and management. Arches is purpose-built for the international cultural heritage field, and designed to record all types of immovable heritage, including archaeological sites, buildings and other historic structures, landscapes, and heritage ensembles or districts. For more information and background on the Arches project, please visit [archesproject.org](http://archesproject.org/).

For general inquiries and to get technical support from the wider Arches community, visit our [Google groups forum](https://groups.google.com/forum/#!forum/archesproject).

For general user installation and app documentation, visit [arches.readthedocs.io](https://arches.readthedocs.io).

For the documentation pertaining to the bleeding edge code (what is in the ``master`` branch), visit [arches.readthedocs.io/en/latest](https://arches.readthedocs.io/en/latest).  We welcome new contributors; please see [Contributing to Arches](CONTRIBUTING.md) for details.

Issue reports are encouraged! [Please read this article](http://polite.technology/reportabug.html) before reporting issues.
*   [Report a Bug](https://github.com/archesproject/arches/issues/new?template=bug.md)
*   [File a Feature Ticket](https://github.com/archesproject/arches/issues/new?template=feature.md)

[Version 5.1.4 release notes](https://github.com/archesproject/arches/blob/stable/5.1.x/releases/5.1.4.md)

#### Quick Install

Installation is fully documented in the official documentation, [arches.readthedocs.io/en/stable](https://arches.readthedocs.io/en/stable), but assuming you have all of the dependencies installed you should make a virtual environment, activate it, and then run

    pip install arches

then

    arches-project create myproject

enter the new `myproject` directory

    cd myproject

and run

    python manage.py setup_db
    python manage.py runserver

and visit `localhost:8000` in a browser (only Chrome is fully supported at this time).

If you run into problems, please review our the full [installation documentation](http://arches.readthedocs.io/en/stable/installation/)

#### Release Cycle

Our general release cycle will typically be a functional release (either major if there are backward incompatible changes or minor, if there are not) followed in 6-12 weeks by a bug release (patch). See [semver.org](https://semver.org/) for version numbering.

-   Functional releases will usually introduce new functionality to the application but could also include styling updates, enhancements to the UX, bug fixes, and general improvements.
-   Bug releases are really only concerned with fixing any bugs related to the previous release or any other issues not yet addressed

##### Support for previous releases

Functional releases will be supported until the next functional release. After that users are expected to upgrade to the latest release on [pypi.python.org](https://pypi.python.org/pypi/arches)
