import re
from django_hosts import patterns, host

host_patterns = patterns(
    "",
    host(
        re.sub(r"_", r"-", r"arches_controlled_lists"),
        "arches_controlled_lists.urls",
        name="arches_controlled_lists",
    ),
)
