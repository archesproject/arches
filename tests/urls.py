"""Root URLconf for arches' own test suite.

tests/test_settings.py enables the bundled applications, so their URLs have to
be reachable for the tests that reverse them. Projects do the same thing in
their own urls.py; see the project template.
"""

from django.urls import include, path

urlpatterns = [
    path("", include("arches.extensions.querysets.urls")),
    path("", include("arches.extensions.vue_components.urls")),
    path("", include("arches.extensions.controlled_lists.urls")),
]

# Last, so that anything above supersedes the core routes.
urlpatterns.append(path("", include("arches.urls")))
