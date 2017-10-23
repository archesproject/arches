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

import time
from datetime import datetime, timedelta
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.translation import ugettext as _
from django.utils.http import urlencode
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from django.core.urlresolvers import reverse
from django.core.mail import EmailMultiAlternatives
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import django.contrib.auth.password_validation as validation
from arches.app.models.system_settings import settings
from arches.app.utils.JSONResponse import JSONResponse
from arches.app.utils.forms import ArchesUserCreationForm
from arches.app.utils.crypto import AESCipher
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer

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
        if user is None:
            try:
                userobj = User.objects.get(email=username)
                user = authenticate(username=userobj.username, password=password)
            except:
                auth_attempt_success = False
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


@never_cache
def signup(request):

    postdata = {
        'first_name': '',
        'last_name': '',
        'email': ''
    }
    showform = True
    confirmation_message = ''

    if request.method == 'POST':
        postdata = request.POST.copy()
        postdata['ts'] = int(time.time())
        form = ArchesUserCreationForm(postdata)
        if form.is_valid():
            AES = AESCipher(settings.SECRET_KEY)
            userinfo = JSONSerializer().serialize(form.cleaned_data)
            encrypted_userinfo = AES.encrypt(userinfo)
            url_encrypted_userinfo = urlencode({'link':encrypted_userinfo})

            email_context = {
                'host': request.get_host(),
                'link':request.build_absolute_uri(reverse('confirm_signup') + '?' + url_encrypted_userinfo,),
                'greeting': _('Thanks for your interest in Arches. Click on link below to confirm your email address! Use your email address to login.'),
                'closing': _('This link expires in 24 hours.  If you can\'t get to it before then, don\'t worry, you can always try again with the same email address.'),
            }

            html_content = render_to_string('email/signup_link.htm', email_context) # ...
            text_content = strip_tags(html_content) # this strips the html, so people will have the text as well.

            # create the email, and attach the HTML version as well.
            msg = EmailMultiAlternatives(_('Welcome to Arches!'), text_content, 'from@example.com', [form.cleaned_data['email']])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            confirmation_message = _('An email has been sent to <br><strong>%s</strong><br> with a link to activate your account' % form.cleaned_data['email'])
            showform = False
    else:
        form = ArchesUserCreationForm()

    return render(request, 'signup.htm', {
        'form': form,
        'postdata': postdata,
        'showform': showform,
        'confirmation_message': confirmation_message,
        'validation_help': validation.password_validators_help_texts()
    })

def confirm_signup(request):
    if request.method == 'GET':
        link = request.GET.get('link', None)
        AES = AESCipher(settings.SECRET_KEY)
        userinfo = JSONDeserializer().deserialize(AES.decrypt(link))
        form = ArchesUserCreationForm(userinfo)
        if datetime.fromtimestamp(userinfo['ts']) + timedelta(days=1) >= datetime.fromtimestamp(int(time.time())):
            if form.is_valid():
                user = form.save()
                return redirect('auth')
            else:
                try:
                    for error in form.errors.as_data()['username']:
                        if error.code == 'unique':
                            return redirect('auth')
                except:
                    pass
        else:
            form.errors['ts'] = [_('The signup link has expired, please try signing up again.  Thanks!')]

        return render(request, 'signup.htm', {
            'form': form,
            'showform': True,
            'postdata': userinfo,
            'validation_help': validation.password_validators_help_texts()
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

def custom_404(request):
    request = None
    return render(request, 'errors/404.htm')

def custom_500(request):
    request = None
    return render(request, 'errors/500.htm')
