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

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

class ArchesUserCreationForm(UserCreationForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """

    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    phone = forms.CharField(required=False)
    ts = forms.IntegerField(required=False)

    class Meta:
        model = User
        fields = ('email','username','first_name','last_name', 'ts')

    def clean(self):
        cleaned_data = super(ArchesUserCreationForm, self).clean()
        try:
            userobj = User.objects.get(email=cleaned_data['email'])
            self.add_error('email', forms.ValidationError(
                _('This email address has already been regisitered with the system. If you forgot your password, click the "exit" link below and go to the login page to reset your password.'),
                code='unique',
            ))
        except:
            pass
