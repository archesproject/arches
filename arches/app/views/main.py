'''
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
'''

import urllib2
from urlparse import urlparse
from django.shortcuts import render
from arches.app.models.system_settings import settings
from django.http import HttpResponseNotFound, HttpResponse

def index(request):
    return render(request, 'index.htm', {
        'main_script': 'index',
        'active_page': 'Home',
        'app_title': settings.APP_TITLE,
        'copyright_text': settings.COPYRIGHT_TEXT,
        'copyright_year': settings.COPYRIGHT_YEAR
    })

def search(request):
    return render(request, 'views/search.htm')

def widget(request, template="text"):
    return render(request, 'views/components/widgets/%s.htm' % template)

def report_templates(request, template="text"):
    return render(request, 'views/report-templates/%s.htm' % template)

def function_templates(request, template):
    return render(request, 'views/functions/%s.htm' % template)

def templates(request, template):
    return render(request, template)

def help_templates(request):
    template = request.GET.get('template')
    return render(request, 'help/%s.htm' % template)

def feature_popup_content(request):
    url = request.POST.get('url', None)

    if url is not None:
        host = '{uri.hostname}'.format(uri=urlparse(url))
        try:
            if host in settings.ALLOWED_POPUP_HOSTS:
                if url is not None:
                    f = urllib2.urlopen(url)
                    return HttpResponse(f.read())
            else:
                raise Exception()
        except:
            return HttpResponseNotFound()
    else:
        return HttpResponseNotFound()

def custom_404(request):
    request = None
    return render(request, 'errors/404.htm')

def custom_500(request):
    request = None
    return render(request, 'errors/500.htm')
