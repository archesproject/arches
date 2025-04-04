# Arches

Arches is a web-based, geospatial information system for cultural heritage inventory and management. Arches is purpose-built for the international cultural heritage field, and designed to record all types of immovable heritage, including archaeological sites, buildings and other historic structures, landscapes, and heritage ensembles or districts. For more information and background on the Arches project, please visit [archesproject.org](http://archesproject.org/).

For general inquiries and to get technical support from the wider Arches community, visit our [Community Forum](https://community.archesproject.org/).

For general user installation and app documentation, visit [arches.readthedocs.io](https://arches.readthedocs.io).

For the documentation pertaining to the bleeding edge code (what is in the ``master`` branch), visit [arches.readthedocs.io/en/latest](https://arches.readthedocs.io/en/latest).  We welcome new contributors; please see [Contributing to Arches](CONTRIBUTING.md) for details.

Issue reports are encouraged! [Please read this article](http://polite.technology/reportabug.html) before reporting issues.
*   [Report a Bug](https://github.com/archesproject/arches/issues/new?template=bug.md)
*   [File a Feature Ticket](https://github.com/archesproject/arches/issues/new?template=feature.md)

[Version 7.6.9 release notes](https://github.com/archesproject/arches/blob/dev/7.6.x/releases/7.6.9.md)

#### Quick Install

Installation is fully documented in the official documentation, [arches.readthedocs.io/en/stable](https://arches.readthedocs.io/en/stable), but assuming you have all of the dependencies installed you should make a virtual environment, activate it, and then run
```
    pip install arches
```
then
```
    arches-project create myproject
```
enter the new `myproject` directory
```
    cd myproject
```
and run
```
    python manage.py setup_db
    python manage.py runserver
```
in a separate terminal, activate your virtual environment and navigate to the root directory of the project ( you should be on the same level as `package.json`) 
```
    cd myproject/myproject
```
and run
```   
    npm run build_development
```
to create a frontend asset bundle. This process should complete in less than 2 minutes.

Finally, visit `localhost:8000` in a browser (only Chrome is fully supported at this time).

If you run into problems, please review our full [installation documentation](http://arches.readthedocs.io/en/stable/installation/)

#### Release Cycle

Our general release cycle will typically be a functional release (either major if there are backward incompatible changes or minor, if there are not) every 9 months. Each functional release will typically be followed by one or more patch releases. See [semver.org](https://semver.org/) for version numbering.

-   Functional releases will usually introduce new functionality to the application, but could also include styling updates, enhancements to the UX, bug fixes, and performance improvements.
-   Patch releases are really only concerned with fixing any bugs related to the previous release or any other issues not yet addressed

#### Support for previous releases

- LTS (Long Term Support) releases will be maintained with patch releases for at least 27 months. Typically an LTS release will be the second minor release following a major release. 
- Feature releases (with the exception of stable releases) will be supported only until the next feature release. After that users are expected to upgrade to the latest release on [pypi.python.org](https://pypi.python.org/pypi/arches)

#### Feature roadmap

The following a general plan for the Arches project. Be aware this plan is tentative and subject to change.

## 8.0 - Release date: June 15, 2025
- Activity stream enhancements
- Support for editing and publishing graphs without having to remove resource instances
- Support for viewing and restoring previous graph publications
- Support for configuring currently published graphs
- Support for search through resource relationships
- Persistent uris for resource instance and tile data
- Implementation resource lifecycles
- Bulk Data Manager CLI interface
- Migration to MapLibre
- Django 5.2 support
- Python 3.11 becomes minimum Python version

## 8.0 - Supported Applications
- Arches References
- Arches Lingo

## 9.0 - Release date: Sept 15, 2027
- Full migration to Vue
- Deprecation of the RDM
- Deprecation of the following datatypes:
    - concept
    - concept-list
    - domain
    - domain-list datatypes