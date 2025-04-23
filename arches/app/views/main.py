"""
ARCHES - a program developed to inventory and manage immovable cultural heritage.
Copyright (C) 2013 J. Paul Getty Trust and World Monuments Fund

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import urllib.request, urllib.error, urllib.parse
from http import HTTPStatus
from urllib.parse import urlparse

from django.http import HttpResponseNotFound, HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext as _

from arches import __version__
from arches.app.models.system_settings import settings
from arches.app.utils.request import looks_like_api_call
from arches.app.utils.response import JSONErrorResponse


def index(request):
    return render(
        request,
        "index.htm",
        {
            "main_script": "index",
            "active_page": "Home",
            "app_title": settings.APP_TITLE,
            "copyright_text": settings.COPYRIGHT_TEXT,
            "copyright_year": settings.COPYRIGHT_YEAR,
            "app_version": settings.APP_VERSION,
            "version": __version__,
            "show_language_swtich": settings.SHOW_LANGUAGE_SWITCH,
        },
    )


def search(request):
    return render(request, "views/search.htm")


def widget(request, template="text"):
    return render(request, "views/components/widgets/%s.htm" % template)


def report_templates(request, template="text"):
    return render(request, "views/report-templates/%s.htm" % template)


def function_templates(request, template):
    return render(request, "views/functions/%s.htm" % template)


def templates(request, template):
    if not template:
        template = request.GET.get("template")
    return render(request, template)


def help_templates(request):
    template = request.GET.get("template")
    return render(request, "help/%s.htm" % template)


def feature_popup_content(request):
    url = request.POST.get("url", None)

    if url is not None:
        host = "{uri.hostname}".format(uri=urlparse(url))
        try:
            if host in settings.ALLOWED_POPUP_HOSTS:
                if url is not None:
                    f = urllib.request.urlopen(url)
                    return HttpResponse(f.read())
            else:
                raise Exception()
        except:
            return HttpResponseNotFound()
    else:
        return HttpResponseNotFound()


def custom_400(request, exception=None):
    status = HTTPStatus.BAD_REQUEST
    if looks_like_api_call(request):
        return JSONErrorResponse(_("Request Failed"), _("Bad Request"), status=status)
    return render(request, "errors/400.htm", status=status)


def custom_403(request, exception=None):
    status = HTTPStatus.FORBIDDEN
    if looks_like_api_call(request):
        return JSONErrorResponse(
            _("Request Failed"), _("Permission Denied"), status=status
        )
    return render(request, "errors/403.htm", status=status)


def custom_404(request, exception=None):
    status = HTTPStatus.NOT_FOUND
    if looks_like_api_call(request):
        return JSONErrorResponse(_("Request Failed"), _("Not Found"), status=status)
    return render(request, "errors/404.htm", status=status)


def custom_500(request, exception=None):
    status = HTTPStatus.INTERNAL_SERVER_ERROR
    if looks_like_api_call(request):
        return JSONErrorResponse(
            # Exclamation point matches translated string in template.
            _("Request Failed"),
            _("Internal Server Error!"),
            status=status,
        )
    return render(request, "errors/500.htm", status=status)
