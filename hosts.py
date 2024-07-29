import re
from django_hosts import patterns, host

host_patterns = patterns(
    "",
    host(
        re.sub(r"_", r"-", r"arches_references"),
        "arches_references.urls",
        name="arches_references",
    ),
)
