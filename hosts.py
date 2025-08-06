import re
from django_hosts import patterns, host

host_patterns = patterns(
    "",
    host(
        re.sub(r"_", r"-", r"arches_querysets"),
        "arches_querysets.arches_querysets_urls",
        name="arches_querysets",
    ),
)
