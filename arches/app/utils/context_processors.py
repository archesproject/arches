from django.conf import settings
from arches.app.models.resource import Resource

def livereload(request):
	return {
		'livereload_port': settings.LIVERELOAD_PORT
	}

def resource_types(request):
    return {
        'resource_types': Resource().get_resource_types()
    }
