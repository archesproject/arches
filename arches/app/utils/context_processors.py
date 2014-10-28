from django.conf import settings
from django.template import RequestContext

def livereload(request):
    "A context processor that provides the livereload port from settings."
    return {
        'livereload_port': settings.LIVERELOAD_PORT
    }