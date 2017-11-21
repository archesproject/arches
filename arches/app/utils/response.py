from io import StringIO
from django.http import HttpResponse
from arches.app.utils.betterJSONSerializer import JSONSerializer

class JSONResponse(HttpResponse):

    def __init__(self, content=b'', *args, **kwargs):
    	kwargs['content_type'] = 'text/json'

    	ensure_ascii = kwargs.pop("ensure_ascii", True)
        stream = kwargs.pop("stream", None)
        indent = kwargs.pop("indent", None)
        selected_fields = kwargs.pop("fields", None)
        use_natural_keys = kwargs.pop("use_natural_keys", None)
        geom_format = kwargs.pop("geom_format", None)

        super(HttpResponse, self).__init__(*args, **kwargs)  

        options = {}
        if ensure_ascii != None:
        	options['ensure_ascii'] = ensure_ascii
        if stream != None:
        	options['stream'] = stream
    	if indent != None:
        	options['indent'] = indent
    	if selected_fields != None:
        	options['selected_fields'] = selected_fields
    	if use_natural_keys != None:
        	options['use_natural_keys'] = use_natural_keys
        if geom_format != None:
        	options['geom_format'] = geom_format

        # Content is a bytestring. See the `content` property methods.
        self.content = JSONSerializer().serialize(content, **options)