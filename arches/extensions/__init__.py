"""Arches applications distributed with arches itself.

Each subpackage is a self-contained Django application with its own models,
migrations and URLs, and is enabled by adding it to INSTALLED_APPS. They ship
here rather than as separately released packages so that they version and
release with arches; see the 8.2.0 release notes.
"""
