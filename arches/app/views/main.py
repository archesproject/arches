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

from arches.app.models.system_settings import settings
from arches.app.utils.JSONResponse import JSONResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
import django.contrib.auth.password_validation as validation
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache


def index(request):
    return render(request, 'index.htm', {
        'main_script': 'index',
        'active_page': 'Home',
        'app_title': settings.APP_TITLE,
        'copyright_text': settings.COPYRIGHT_TEXT,
        'copyright_year': settings.COPYRIGHT_YEAR
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
                'app_name': settings.APP_NAME,
                'auth_failed': (auth_attempt_success is not None),
                'next': next
            })

@login_required
def change_password(request):
    messages = {'invalid_password': None, 'password_validations': None, 'success': None, 'other': None, 'mismatched':None}
    user = request.user
    if request.method == 'POST':
        try:
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            new_password2 = request.POST.get('new_password2')
            if user.check_password(old_password) == False:
                messages['invalid_password'] = _("Invalid password")
            if new_password != new_password2:
                messages['mismatched'] = _("New password and confirmation must match")
            try:
                validation.validate_password(new_password, user)
            except ValidationError as val_err:
                messages['password_validations'] = val_err.messages

            if messages["invalid_password"] == None and messages["password_validations"] == None and messages["mismatched"] == None:
                user.set_password(new_password)
                user.save()
                authenticated_user = authenticate(username=user.username, password=new_password)
                login(request, authenticated_user)
                messages['success'] = _('Password successfully updated')

        except Exception as err:
            print err
            messages['other'] = err

    return JSONResponse(messages)


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

def custom_404(request):
    request = None
    return render(request, 'errors/404.htm')

def custom_500(request):
    request = None
    return render(request, 'errors/500.htm')
