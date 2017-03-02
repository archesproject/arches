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

from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse

def index(request):
    return render(request, 'index.htm', {
        'main_script': 'index',
        'active_page': 'Home',
    })

@never_cache
def auth(request):
    auth_attempt_success = None
    # POST request is taken to mean user is logging in
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            user.password = ''
            auth_attempt_success = True
        else:
            auth_attempt_success = False

    next = request.GET.get('next', reverse('home'))
    if auth_attempt_success:
        return redirect(next)
    else:
        if request.GET.get('logout', None) is not None:
            logout(request)
            # need to redirect to 'auth' so that the user is set to anonymous via the middleware
            return redirect('auth')
        else:
            return render(request, 'login.htm', {
                'auth_failed': (auth_attempt_success is not None),
                'next': next
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
