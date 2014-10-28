from django.conf import settings
from django.template import RequestContext

def livereload(request):
	return {
		'livereload_port': settings.LIVERELOAD_PORT
	}
