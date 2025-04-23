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

import base64
import io

from arches.app.utils.external_oauth_backend import ExternalOauthAuthenticationBackend
import qrcode
import pyotp
import time
import requests
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.http.response import HttpResponseForbidden
from django.template.loader import render_to_string
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.debug import sensitive_post_parameters, sensitive_variables
from django.utils.html import strip_tags
from django.utils.translation import gettext as _
from django.utils.http import urlencode
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth import views as auth_views
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
import django.contrib.auth.password_validation as validation
from django_ratelimit.decorators import ratelimit
from arches import __version__
from arches.app.utils.response import JSONResponse, Http401Response
from arches.app.utils.forms import (
    ArchesUserCreationForm,
    ArchesPasswordResetForm,
    ArchesSetPasswordForm,
)
from arches.app.models import models
from arches.app.models.system_settings import settings
from arches.app.utils.arches_crypto import AESCipher
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.message_contexts import return_message_context
from arches.app.utils.permission_backend import user_is_resource_reviewer
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


class LoginView(View):
    def get(self, request):
        next = request.GET.get("next", reverse("home"))
        registration_success = request.GET.get("registration_success")

        if request.GET.get("logout", None) is not None:
            logout(request)
            # need to redirect to 'auth' so that the user is set to anonymous via the middleware
            return redirect("auth")
        else:
            return render(
                request,
                "login.htm",
                {
                    "auth_failed": False,
                    "next": next,
                    "registration_success": registration_success,
                    "user_signup_enabled": settings.ENABLE_USER_SIGNUP,
                },
            )

    @method_decorator(
        (
            sensitive_variables(),
            sensitive_post_parameters(),
            ratelimit(
                key="post:username",
                rate=(
                    (
                        "{}/{}".format(
                            int(settings.RATE_LIMIT.split("/")[0]) * 2,
                            settings.RATE_LIMIT.split("/")[1],
                        )
                    )
                    if isinstance(settings.RATE_LIMIT, str)
                    else settings.RATE_LIMIT
                ),
                block=False,
            ),
        )
    )
    def post(self, request):
        # POST request is taken to mean user is logging in
        next = request.POST.get("next", reverse("home"))

        if getattr(request, "limited", False):
            return render(
                request,
                "login.htm",
                {
                    "auth_failed": True,
                    "rate_limited": True,
                    "next": next,
                    "user_signup_enabled": settings.ENABLE_USER_SIGNUP,
                },
                status=429,
            )

        username = request.POST.get("username", None)
        password = request.POST.get("password", None)

        if username is not None and password is None:
            try:
                domain = username.split("@")[1]
                if domain in settings.EXTERNAL_OAUTH_CONFIGURATION["user_domains"]:
                    oauth_url = reverse("external_oauth_start")
                    redirect_url = f"{oauth_url}?username={username}"
                    return redirect(redirect_url)
            except:
                pass
            return render(
                request,
                "login.htm",
                {
                    "username": username,
                    "username_entered": True,
                    "next": next,
                    "user_signup_enabled": settings.ENABLE_USER_SIGNUP,
                },
            )

        user = authenticate(username=username, password=password)

        if user is not None and user.is_active:
            if (
                settings.FORCE_TWO_FACTOR_AUTHENTICATION
                or settings.ENABLE_TWO_FACTOR_AUTHENTICATION
            ):
                user_profile = models.UserProfile.objects.get(user=user)
                user_has_enabled_two_factor_authentication = bool(
                    user_profile.encrypted_mfa_hash
                )

                if (
                    settings.FORCE_TWO_FACTOR_AUTHENTICATION
                    or user_has_enabled_two_factor_authentication
                ):  # user has enabled two-factor authentication
                    return render(
                        request,
                        "two_factor_authentication_login.htm",
                        {
                            "username": username,
                            "password": password,
                            "next": next,
                            "email": user.email,
                            "user_has_enabled_two_factor_authentication": user_has_enabled_two_factor_authentication,
                        },
                    )
                else:
                    login(request, user)
                    user.password = ""

                    return redirect(next)
            else:
                login(request, user)
                user.password = ""

                return redirect(next)

        return render(
            request,
            "login.htm",
            {
                "auth_failed": True,
                "next": next,
                "user_signup_enabled": settings.ENABLE_USER_SIGNUP,
            },
            status=401,
        )


@method_decorator(never_cache, name="dispatch")
class SignupView(View):
    def get(self, request):
        form = ArchesUserCreationForm(enable_captcha=settings.ENABLE_CAPTCHA)
        postdata = {"first_name": "", "last_name": "", "email": ""}
        showform = True
        confirmation_message = ""

        if not settings.ENABLE_USER_SIGNUP:
            msg = _("User signup has been disabled. Please contact your administrator.")
            raise Exception(msg)

        return render(
            request,
            "signup.htm",
            {
                "enable_captcha": settings.ENABLE_CAPTCHA,
                "form": form,
                "postdata": postdata,
                "showform": showform,
                "confirmation_message": confirmation_message,
                "validation_help": validation.password_validators_help_texts(),
            },
        )

    @method_decorator(
        (
            sensitive_variables(),
            sensitive_post_parameters(),
        )
    )
    def post(self, request):
        showform = True
        confirmation_message = ""
        postdata = request.POST.copy()
        postdata["ts"] = int(time.time())
        form = ArchesUserCreationForm(postdata, enable_captcha=settings.ENABLE_CAPTCHA)

        if not settings.ENABLE_USER_SIGNUP:
            msg = _("User signup has been disabled. Please contact your administrator.")
            raise Exception(msg)

        if form.is_valid():
            AES = AESCipher(settings.SECRET_KEY)
            userinfo = JSONSerializer().serialize(form.cleaned_data)
            encrypted_userinfo = AES.encrypt(userinfo)
            url_encrypted_userinfo = urlencode({"link": encrypted_userinfo})
            confirmation_link = request.build_absolute_uri(
                reverse("confirm_signup") + "?" + url_encrypted_userinfo
            )

            if (
                not settings.FORCE_USER_SIGNUP_EMAIL_AUTHENTICATION
            ):  # bypasses email confirmation if setting is disabled
                return redirect(confirmation_link)

            admin_email = settings.ADMINS[0][1] if settings.ADMINS else ""
            email_context = return_message_context(
                greeting=_(
                    "Thanks for your interest in {}. Click on link below \
                    to confirm your email address! Use your email address to login."
                ).format(settings.APP_NAME),
                closing_text=_(
                    "This link expires in 24 hours.  If you can't get to it before then, \
                    don't worry, you can always try again with the same email address."
                ),
                additional_context={
                    "button_text": _("Signup for {}").format(settings.APP_NAME),
                    "link": confirmation_link,
                    "username": form.cleaned_data["username"],
                },
            )

            html_content = render_to_string(
                "email/general_notification.htm", email_context
            )  # ...
            text_content = strip_tags(
                html_content
            )  # this strips the html, so people will have the text as well.

            # create the email, and attach the HTML version as well.
            msg = EmailMultiAlternatives(
                _("Welcome to {}!").format(settings.APP_NAME),
                text_content,
                admin_email,
                [form.cleaned_data["email"]],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            confirmation_message = _(
                "An email has been sent to <br><strong>%s</strong><br> with a link to activate your account"
                % form.cleaned_data["email"]
            )
            showform = False

        return render(
            request,
            "signup.htm",
            {
                "enable_captcha": settings.ENABLE_CAPTCHA,
                "form": form,
                "postdata": postdata,
                "showform": showform,
                "confirmation_message": confirmation_message,
                "validation_help": validation.password_validators_help_texts(),
            },
        )


@method_decorator(never_cache, name="dispatch")
class ConfirmSignupView(View):
    def get(self, request):
        if not settings.ENABLE_USER_SIGNUP:
            msg = _("User signup has been disabled. Please contact your administrator.")
            raise Exception(msg)

        link = request.GET.get("link", None)
        AES = AESCipher(settings.SECRET_KEY)
        userinfo = JSONDeserializer().deserialize(AES.decrypt(link))
        form = ArchesUserCreationForm(userinfo)
        if datetime.fromtimestamp(userinfo["ts"]) + timedelta(
            days=1
        ) >= datetime.fromtimestamp(int(time.time())):
            if form.is_valid():
                user = form.save()
                crowdsource_editor_group = Group.objects.get(
                    name=settings.USER_SIGNUP_GROUP
                )
                user.groups.add(crowdsource_editor_group)
                return redirect(reverse("auth") + "?registration_success=true")
            else:
                try:
                    for error in form.errors.as_data()["username"]:
                        if error.code == "unique":
                            return redirect("auth")
                except:
                    pass
        else:
            form.errors["ts"] = [
                _("The signup link has expired, please try signing up again.  Thanks!")
            ]

        return render(
            request,
            "signup.htm",
            {
                "form": form,
                "showform": True,
                "postdata": userinfo,
                "validation_help": validation.password_validators_help_texts(),
            },
        )


@method_decorator(login_required, name="dispatch")
class ChangePasswordView(View):
    def get(self, request):
        messages = {
            "invalid_password": None,
            "password_validations": None,
            "success": None,
            "other": None,
            "mismatched": None,
        }
        return JSONResponse(messages)

    @method_decorator(
        (
            sensitive_variables(),
            sensitive_post_parameters(),
            ratelimit(key="user", rate=settings.RATE_LIMIT, block=False),
        )
    )
    def post(self, request):
        messages = {
            "invalid_password": None,
            "password_validations": None,
            "success": None,
            "other": None,
            "mismatched": None,
        }

        if getattr(request, "limited", False):
            messages["invalid_password"] = _("Too many requests")
            return JSONResponse(messages)
        try:
            user = request.user
            old_password = request.POST.get("old_password")
            new_password = request.POST.get("new_password")
            new_password2 = request.POST.get("new_password2")
            if user.check_password(old_password) == False:
                messages["invalid_password"] = _("Invalid password")
            if new_password != new_password2:
                messages["mismatched"] = _("New password and confirmation must match")
            try:
                validation.validate_password(new_password, user)
            except ValidationError as val_err:
                messages["password_validations"] = val_err.messages

            if (
                messages["invalid_password"] is None
                and messages["password_validations"] is None
                and messages["mismatched"] is None
            ):
                user.set_password(new_password)
                user.save()
                authenticated_user = authenticate(
                    username=user.username, password=new_password
                )
                login(request, authenticated_user)
                messages["success"] = _("Password successfully updated")

        except Exception as err:
            messages["other"] = err

        return JSONResponse(messages)


class PasswordResetView(auth_views.PasswordResetView):
    form_class = ArchesPasswordResetForm


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    form_class = ArchesSetPasswordForm


@method_decorator(csrf_exempt, name="dispatch")
class UserProfileView(View):
    @method_decorator(
        (
            sensitive_variables(),
            sensitive_post_parameters(),
            ratelimit(key="post:username", rate=settings.RATE_LIMIT),
        )
    )
    def post(self, request):
        username = request.POST.get("username", None)
        password = request.POST.get("password", None)
        user = authenticate(username=username, password=password)
        if user:
            userDict = JSONSerializer().serializeToPython(user)
            userDict["password"] = None
            userDict["is_reviewer"] = user_is_resource_reviewer(user)
            userDict["viewable_nodegroups"] = user.userprofile.viewable_nodegroups
            userDict["editable_nodegroups"] = user.userprofile.editable_nodegroups
            userDict["deletable_nodegroups"] = user.userprofile.deletable_nodegroups
            response = JSONResponse(userDict)
        else:
            response = Http401Response()

        return response


@method_decorator(csrf_exempt, name="dispatch")
class GetClientIdView(View):
    @method_decorator(
        (
            sensitive_variables(),
            sensitive_post_parameters(),
            ratelimit(key="post:username", rate=settings.RATE_LIMIT),
        )
    )
    def post(self, request):
        if settings.OAUTH_CLIENT_ID == "":
            message = _("Make sure to set your OAUTH_CLIENT_ID in settings.py")
            response = HttpResponse(message, status=500)
            logger.warning(message)
        else:
            username = request.POST.get("username", None)
            password = request.POST.get("password", None)
            user = authenticate(username=username, password=password)
            if user:
                response = JSONResponse({"clientid": settings.OAUTH_CLIENT_ID})
            else:
                response = Http401Response()
        return response


@method_decorator(csrf_exempt, name="dispatch")
class ServerSettingView(View):
    @method_decorator(
        (
            sensitive_variables(),
            sensitive_post_parameters(),
            ratelimit(key="post:username", rate=settings.RATE_LIMIT),
        )
    )
    def post(self, request):
        if settings.OAUTH_CLIENT_ID == "":
            message = _("Make sure to set your OAUTH_CLIENT_ID in settings.py")
            logger.warning(message)

        username = request.POST.get("username", None)
        password = request.POST.get("password", None)
        user = authenticate(username=username, password=password)
        if user:
            server_settings = {
                "version": __version__,
                "clientid": settings.OAUTH_CLIENT_ID,
            }
            response = JSONResponse(server_settings)
        else:
            response = Http401Response()

        return response


@method_decorator(never_cache, name="dispatch")
class TwoFactorAuthenticationResetView(View):
    def get(self, request):
        queried_email_address = request.GET.get("queried_email_address")
        return render(
            request,
            "two_factor_authentication_reset.htm",
            {
                "queried_email_address": queried_email_address,
            },
        )

    def post(self, request):
        email = request.POST.get("email")
        user = None

        if email:
            try:
                user = models.User.objects.get(email=email)
            except Exception:
                pass

        if user:
            try:
                AES = AESCipher(settings.SECRET_KEY)

                serialized_data = JSONSerializer().serialize(
                    {"ts": int(time.time()), "user": user}
                )
                encrypted_url = urlencode({"link": AES.encrypt(serialized_data)})

                admin_email = settings.ADMINS[0][1] if settings.ADMINS else ""

                email_context = return_message_context(
                    greeting=_(
                        "Click on link below to update your two-factor authentication settings."
                    ),
                    closing_text=_(
                        "This link expires in 15 minutes. If you did not request this change, \
                        contact your Administrator immediately."
                    ),
                    additional_context={
                        "button_text": _("Update Two-Factor Authentication Settings"),
                        "link": request.build_absolute_uri(
                            reverse("two-factor-authentication-settings")
                            + "?"
                            + encrypted_url
                        ),
                        "username": user.username,
                    },
                )

                html_content = render_to_string(
                    "email/general_notification.htm", email_context
                )  # ...
                text_content = strip_tags(
                    html_content
                )  # this strips the html, so people will have the text as well.

                # create the email, and attach the HTML version as well.
                msg = EmailMultiAlternatives(
                    _("Arches Two-Factor Authentication"),
                    text_content,
                    admin_email,
                    [user.email],
                )
                msg.attach_alternative(html_content, "text/html")

                msg.send()
            except:
                raise Exception(
                    _(
                        "There has been error sending an email to this address. Please contact your system administrator."
                    )
                )

        return render(
            request,
            "two_factor_authentication_reset.htm",
            {
                "queried_email_address": email,
            },
        )


@method_decorator(never_cache, name="dispatch")
class TwoFactorAuthenticationLoginView(View):
    @method_decorator((sensitive_variables(), sensitive_post_parameters()))
    def post(self, request):
        username = request.POST.get("username", None)
        password = request.POST.get("password", None)
        user = authenticate(username=username, password=password)

        next = request.POST.get("next", reverse("home"))
        user_has_enabled_two_factor_authentication = request.POST.get(
            "user-has-enabled-two-factor-authentication", None
        )
        two_factor_authentication_string = request.POST.get(
            "two-factor-authentication", None
        )

        if (
            user is not None
            and user.is_active
            and user_has_enabled_two_factor_authentication
        ):
            user_profile = models.UserProfile.objects.get(user_id=user.pk)

            if user_profile.encrypted_mfa_hash:
                AES = AESCipher(settings.SECRET_KEY)
                encrypted_mfa_hash = user_profile.encrypted_mfa_hash[
                    1 : len(user_profile.encrypted_mfa_hash)
                ]  # removes outer string values
                decrypted_mfa_hash = AES.decrypt(encrypted_mfa_hash)

                totp = pyotp.TOTP(decrypted_mfa_hash)

                if totp.verify(two_factor_authentication_string):
                    login(request, user)
                    user.password = ""

                    return redirect(next)

        return render(
            request,
            "two_factor_authentication_login.htm",
            {
                "auth_failed": True,
                "next": next,
                "username": username,
                "password": password,
                "email": user.email,
                "user_has_enabled_two_factor_authentication": user_has_enabled_two_factor_authentication,
            },
            status=401,
        )


@method_decorator(never_cache, name="dispatch")
class TwoFactorAuthenticationSettingsView(View):
    def get(self, request):
        link = request.GET.get("link", None)
        AES = AESCipher(settings.SECRET_KEY)

        decrypted_data = JSONDeserializer().deserialize(AES.decrypt(link))

        if datetime.fromtimestamp(decrypted_data["ts"]) + timedelta(
            minutes=15
        ) >= datetime.fromtimestamp(
            int(time.time())
        ):  # if before email expiry
            user_id = decrypted_data["user"]["id"]
            user_profile = models.UserProfile.objects.get(user_id=user_id)

            context = {
                "ENABLE_TWO_FACTOR_AUTHENTICATION": settings.ENABLE_TWO_FACTOR_AUTHENTICATION,
                "FORCE_TWO_FACTOR_AUTHENTICATION": settings.FORCE_TWO_FACTOR_AUTHENTICATION,
                "user_has_enabled_two_factor_authentication": bool(
                    user_profile.encrypted_mfa_hash
                ),
                "user_id": user_id,
            }

        else:
            raise Exception("Link Expired")

        return render(request, "two_factor_authentication_settings.htm", context)

    def post(self, request):
        user_id = request.POST.get("user-id")
        user = models.User.objects.get(pk=int(user_id))
        user_profile = models.UserProfile.objects.get(user_id=user_id)

        generate_qr_code = request.POST.get("generate-qr-code-button")
        generate_manual_key = request.POST.get("generate-manual-key-button")
        delete_mfa_hash = request.POST.get("delete-mfa-hash-button")

        new_mfa_hash_qr_code = None
        new_mfa_hash_manual_entry_data = None

        if generate_qr_code or generate_manual_key or delete_mfa_hash:
            AES = AESCipher(settings.SECRET_KEY)

            if generate_qr_code or generate_manual_key:
                mfa_hash = pyotp.random_base32()
                encrypted_mfa_hash = AES.encrypt(mfa_hash)
                user_profile.encrypted_mfa_hash = encrypted_mfa_hash

                if generate_qr_code:
                    uri = pyotp.totp.TOTP(mfa_hash).provisioning_uri(
                        user.email, issuer_name=settings.APP_TITLE
                    )
                    uri_qrcode = qrcode.make(uri)

                    buffer = io.BytesIO()
                    uri_qrcode.save(buffer)

                    base64_encoded_result_bytes = base64.b64encode(buffer.getvalue())
                    new_mfa_hash_qr_code = base64_encoded_result_bytes.decode("ascii")

                    buffer.close()
                elif generate_manual_key:
                    new_mfa_hash_manual_entry_data = {
                        "new_mfa_hash": mfa_hash,
                        "name": user.email,
                        "issuer_name": settings.APP_TITLE,
                    }

            elif delete_mfa_hash and not settings.FORCE_TWO_FACTOR_AUTHENTICATION:
                user_profile.encrypted_mfa_hash = None

            user_profile.save()

            for session in Session.objects.all():  # logs user out of all sessions
                if str(session.get_decoded().get("_auth_user_id")) == str(user.id):
                    session.delete()

        context = {
            "ENABLE_TWO_FACTOR_AUTHENTICATION": settings.ENABLE_TWO_FACTOR_AUTHENTICATION,
            "FORCE_TWO_FACTOR_AUTHENTICATION": settings.FORCE_TWO_FACTOR_AUTHENTICATION,
            "user_has_enabled_two_factor_authentication": bool(
                user_profile.encrypted_mfa_hash
            ),
            "new_mfa_hash_qr_code": new_mfa_hash_qr_code,
            "new_mfa_hash_manual_entry_data": new_mfa_hash_manual_entry_data,
            "user_id": user_id,
        }

        return render(request, "two_factor_authentication_settings.htm", context)


@method_decorator(csrf_exempt, name="dispatch")
class Token(View):
    @method_decorator(sensitive_variables())
    def get(self, request):
        if settings.DEBUG:
            data = {
                "username": request.GET.get("username", None),
                "password": request.GET.get("password", None),
                "client_id": settings.OAUTH_CLIENT_ID,
                "grant_type": "password",
            }
            url = request.get_raw_uri().replace(request.path, "").split("?")[
                0
            ] + reverse("oauth2:token")
            r = requests.post(url, data=data)
            return JSONResponse(r.json(), indent=4)
        return HttpResponseForbidden()


class ExternalOauth(View):
    def start(request):
        next = request.GET.get("next", reverse("home"))
        username = request.GET.get("username", None)

        token, user = ExternalOauthAuthenticationBackend.get_token_for_username(
            username
        )
        if token is not None and token.access_token_expiration > datetime.now():
            return ExternalOauth.log_user_in(request, user, next)

        authorization_url, state = (
            ExternalOauthAuthenticationBackend.get_authorization_url(request)
        )
        request.session["oauth_state"] = state
        request.session["next"] = next
        request.session["user"] = username
        return redirect(authorization_url)

    @method_decorator(
        csrf_exempt, name="dispatch"
    )  # exempt; returned from other oauth2 authorization server, handled by 'oauth_state' in session
    def callback(request):
        next_url = (
            request.session["next"] if "next" in request.session else reverse("home")
        )
        user = authenticate(
            request, username=request.session["user"], sso_authentication=True
        )
        return ExternalOauth.log_user_in(request, user, next_url)

    def log_user_in(request, user, next_url):
        if user is not None:
            login(
                request,
                user,
                backend="arches.app.utils.external_oauth_backend.ExternalOauthAuthenticationBackend",
            )
            return redirect(next_url)
        else:
            return redirect("auth")
