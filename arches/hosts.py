from django_hosts import patterns, host

host_patterns = patterns('',
    host(r'arches', 'arches.urls', name='arches'),
)