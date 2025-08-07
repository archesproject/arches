import re
from django_hosts import patterns, host

host_patterns = patterns(
    "",
    host(
        re.sub(r"_", r"-", r"arches_component_lab"),
        "arches_component_lab.arches_component_lab_urls",
        name="arches_component_lab",
    ),
)
