"""Host configuration for arches' own test suite.

django_hosts sets request.urlconf from the matched host, which overrides
ROOT_URLCONF for the duration of the request. arches/hosts.py names
arches.urls, so without this the test client would resolve against core's
routes alone and every bundled-application endpoint would 404 -- while
reverse(), which follows ROOT_URLCONF, produced the correct path.

Projects ship their own hosts.py for the same reason; see the project template.
"""

import re

from django_hosts import host, patterns

host_patterns = patterns(
    "",
    host(re.sub(r"_", r"-", r"arches"), "tests.urls", name="arches"),
)
