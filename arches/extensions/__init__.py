"""Arches applications distributed with arches itself.

Each subpackage is a self-contained Django application with its own models,
migrations and URLs, and is enabled by adding it to INSTALLED_APPS. They ship
here rather than as separately released packages so that they version and
release with arches; see the 8.2.0 release notes.
"""

#: App label -> dotted module path, for every application bundled with arches.
#: Keyed by label because that is the identifier that survived the move into
#: this namespace: it names the database tables, the URL namespace and the
#: frontend path alias.
BUNDLED_APPLICATIONS = {
    "arches_querysets": "arches.extensions.querysets",
    "arches_vue_components": "arches.extensions.vue_components",
    "arches_controlled_lists": "arches.extensions.controlled_lists",
}
