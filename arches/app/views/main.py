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

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

def index(request):
    return render_to_response('pages/index.htm', {
            'main_script': 'index',
            'active_page': 'Home'
        },
        context_instance=RequestContext(request))


def login_page(request):
    return render_to_response('pages/login.htm', {
        },
        context_instance=RequestContext(request))


def splash(request):
    #lang = request.GET.get('lang') if request.GET.get('lang') != '' and request.GET.get('lang') != None else settings.LANGUAGE_CODE
    if settings.DEBUG == False:
        return render_to_response('splash.htm', context_instance=RequestContext(request))
    else:
        return render_to_response('splash.htm', context_instance=RequestContext(request))

def search(request):
    return render_to_response('search.htm', context_instance=RequestContext(request))