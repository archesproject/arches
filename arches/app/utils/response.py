from io import StringIO
import logging
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from arches.app.utils.betterJSONSerializer import JSONSerializer

logger = logging.getLogger(__name__)


class JSONResponse(HttpResponse):
    def __init__(self, content=b"", *args, **kwargs):
        kwargs["content_type"] = "application/json"
        ensure_ascii = kwargs.pop("ensure_ascii", True)
        stream = kwargs.pop("stream", None)
        indent = kwargs.pop("indent", None)
        selected_fields = kwargs.pop("fields", None)
        use_natural_keys = kwargs.pop("use_natural_keys", None)
        geom_format = kwargs.pop("geom_format", None)

        super(HttpResponse, self).__init__(*args, **kwargs)

        options = {}
        if ensure_ascii is not None:
            options["ensure_ascii"] = ensure_ascii
        if stream is not None:
            options["stream"] = stream
        if indent is not None:
            options["indent"] = indent
        if selected_fields is not None:
            options["selected_fields"] = selected_fields
        if use_natural_keys is not None:
            options["use_natural_keys"] = use_natural_keys
        if geom_format is not None:
            options["geom_format"] = geom_format

        # Content is a bytestring. See the `content` property methods.
        self.content = JSONSerializer().serialize(content, **options)


class JSONErrorResponse(JSONResponse):
    def __init__(self, title=None, message=None, content={}, status=500, *args, **kwargs):
        try:
            content["status"] = content.get("status", "false")
            content["success"] = content.get("success", False)
            content["title"] = content.get("title", title)
            content["message"] = content.get("message", message)
        except AttributeError as e:
            logger.exception(_("Could not return JSON Response"))

        super(JSONErrorResponse, self).__init__(content=content, status=status, *args, **kwargs)


class Http401Response(HttpResponse):
    status_code = 401

    def __init__(self, *args, **kwargs):
        www_auth_header = kwargs.pop("www_auth_header", "Basic")
        super(Http401Response, self).__init__(*args, **kwargs)
        self["WWW-Authenticate"] = www_auth_header
