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

import base64
import hashlib
from datetime import datetime
from django import forms
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.translation import ugettext as _
from django.utils.http import urlencode
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from django.core.urlresolvers import reverse
from django.core.mail import send_mail, EmailMultiAlternatives
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from Crypto.Cipher import AES
from Crypto import Random

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

@never_cache
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, _('Your password has been updated'))
            return redirect('change_password')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.htm', {
        'form': form
    })

@never_cache
def signup(request):
    
    import ipdb
    postdata = {
        'firstname': '',
        'lastname': '',
        'email': ''
    }

    if request.method == 'POST':
        postdata = request.POST.copy()
        #postdata['username'] = postdata['email']
        form = ArchesUserCreationForm(request.POST)
        if form.is_valid():
            
            obj = AESCipher(settings.SECRET_KEY)
            message = JSONSerializer().serialize({'email': form.cleaned_data['email'], 'password': form.cleaned_data['password1'], 'date': datetime.now()})
            ciphertext = obj.encrypt(message)
            ciphertext = urlencode({'query':ciphertext})
            print 'ciphertext'
            print ciphertext



            html_content = render_to_string('email/signup_link.htm', {'url':reverse('confirm_signup') + '?link=' + ciphertext}) # ...
            text_content = strip_tags(html_content) # this strips the html, so people will have the text as well.

            # create the email, and attach the HTML version as well.
            msg = EmailMultiAlternatives(_('Welcome to Arches!'), text_content, 'from@example.com', ['apeters@fargeo.com'])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            # obj2 = AES.new('This is a key123', AES.MODE_CBC, 'This is an IV456')
            # obj2.decrypt(ciphertext)
            # send_mail(
            #     'Subject here',
            #     ciphertext,
            #     'from@example.com',
            #     ['apeters@fargeo.com'],
            #     fail_silently=False,
            # )
            #user = form.save()
            # user = authenticate(username=user.username, password=str(form.cleaned_data['password1']))
            # if user is not None and user.is_active:
            #     login(request, user)
            messages.success(request, _('An email has been sent with a link'))
            #return redirect('signup')
    else:
        form = ArchesUserCreationForm()

    return render(request, 'signup.htm', {
        'form': form,
        'postdata': postdata
    })

def confirm_signup(request):
    if request.method == 'GET':
        link_text = request.GET.get('link', None)
        #link_text = base64.b64decode(link_text)
        obj = ARC4.new('This is a key123')
        obj = AESCipher(settings.SECRET_KEY)
        message = obj.decrypt(link_text)
        #message = JSONDeserializer().deserialize({"username": form.cleaned_data['username'], "password": form.cleaned_data['password1'], "date": "lakd"})
       
        #user = form.save()
        # import ipdb
        # ipdb.set_trace()
        # user = authenticate(username=user.username, password=str(form.cleaned_data['password1']))
        # if user is not None and user.is_active:
        #     login(request, user)
        print message
        #return redirect('home')

    return render(request, 'signup.htm', {
        'form': ArchesUserCreationForm()
    })

class ArchesUserCreationForm(UserCreationForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """

    # error_messages = {
    #     'password_mismatch': _("The two password fields didn't match."),
    # }

    firstname = forms.CharField()
    lastname = forms.CharField()
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ("email",)

  


    # def clean_password2(self):
    #     password1 = self.cleaned_data.get("password1")
    #     password2 = self.cleaned_data.get("password2")
    #     if password1 and password2 and password1 != password2:
    #         raise forms.ValidationError(
    #             self.error_messages['password_mismatch'],
    #             code='password_mismatch',
    #         )
    #     self.instance.username = self.cleaned_data.get('username')
    #     password_validation.validate_password(self.cleaned_data.get('password2'), self.instance)
    #     return password2

    # def save(self, commit=True):
    #     user = super(UserCreationForm, self).save(commit=False)
    #     user.set_password(self.cleaned_data["password1"])
    #     if commit:
    #         user.save()
    #     return user

class AESCipher(object):

    def __init__(self, key): 
        self.bs = AES.block_size
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]

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
