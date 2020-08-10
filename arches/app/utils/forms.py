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

from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django.db import transaction
from django.forms.widgets import PasswordInput, TextInput
from django.utils.translation import ugettext as _
from arches.app.models import models
from captcha.fields import ReCaptchaField
import logging


class ArchesUserCreationForm(UserCreationForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """

    def __init__(self, *args, **kwargs):
        self.enable_captcha = kwargs.pop("enable_captcha", False)
        super(ArchesUserCreationForm, self).__init__(*args, **kwargs)
        attrs = {"theme": "clean"}
        if self.enable_captcha is True:
            try:
                self.fields["captcha"] = ReCaptchaField(attrs)
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.warn(e)

    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    ts = forms.IntegerField(required=False)

    class Meta:
        model = User
        fields = ("email", "username", "first_name", "last_name", "ts")

    def clean(self):
        cleaned_data = super(ArchesUserCreationForm, self).clean()
        if "email" in cleaned_data:
            if User.objects.filter(email=cleaned_data["email"]).count() > 0:
                self.add_error(
                    "email",
                    forms.ValidationError(
                        _(
                            "This email address has already been regisitered with the system. \
                            If you forgot your password, click the 'exit' link below and go to the login page to reset your password."
                        ),
                        code="unique",
                    ),
                )


class ArchesUserProfileForm(ArchesUserCreationForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """

    id = forms.IntegerField()
    username = forms.CharField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    phone = forms.CharField(required=False)
    password1 = forms.CharField(required=False)
    password2 = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ("email", "username", "first_name", "last_name", "id")

    def clean(self):
        pass

    def save(self):
        user = User.objects.get(username=self.instance.username)
        with transaction.atomic():
            user.first_name = self.cleaned_data["first_name"]
            user.last_name = self.cleaned_data["last_name"]
            user.email = self.cleaned_data["email"]
            if models.UserProfile.objects.filter(user=user).count() == 0:
                models.UserProfile.objects.create(user=user)
            user.userprofile.phone = self.cleaned_data["phone"]
            user.userprofile.save()
            user.save()
        return user


class ArchesPasswordResetForm(PasswordResetForm):
    email = forms.CharField(widget=forms.EmailInput(attrs={"placeholder": _("Email"), "class": "form-control input-lg"}))


class ArchesSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": _("New password"), "class": "form-control input-lg"}))
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": _("Re-enter new password"), "class": "form-control input-lg"})
    )
