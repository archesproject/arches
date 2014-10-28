from django.conf import settings

def livereload(request):
	return {
		'livereload_port': settings.LIVERELOAD_PORT
	}
