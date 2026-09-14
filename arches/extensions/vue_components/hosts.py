import re
from django_hosts import patterns, host

host_patterns = patterns(
    "",
    host(
        re.sub(r"_", r"-", r"arches_vue_components"),
        "arches_vue_components.arches_vue_components_urls",
        name="arches_vue_components",
    ),
)
