from django.contrib.auth.models import User, Group
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import check_password
from arches.app.models.system_settings import settings
from arches.app.models.models import ExternalOauthToken
from datetime import datetime, timedelta


class ExternalOauthAuthenticationBackend(ModelBackend):
    def authenticate(self, request, username=None, sso_authentication=False, expires_in=1200, id_token=None, access_token=None, refresh_token=None, **kwargs):
        try:
            if sso_authentication:
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    user = None

                if user is None and "default_user_groups" in settings.EXTERNAL_OAUTH_CONFIGURATION:
                    user = User.objects.create_user(username, username)
                    for group in settings.EXTERNAL_OAUTH_CONFIGURATION["default_user_groups"]:
                        django_group = Group.objects.get(name=group)
                        user.groups.add(django_group)
                    user.save()
                    
                if user is not None:
                    expiration_date = datetime.now() + timedelta(seconds=expires_in)
                    token_record = ExternalOauthToken()
                    token_record.access_token = access_token
                    token_record.refresh_token = refresh_token
                    token_record.id_token = id_token
                    token_record.access_token_expiration = expiration_date
                    token_record.user = user
                    return user
                
        except Exception as e:
            return None

        return None

    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False. Custom user models that don't have
        that attribute are allowed.
        """
        is_active = getattr(user, "is_active", None)
        return is_active or is_active is None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
