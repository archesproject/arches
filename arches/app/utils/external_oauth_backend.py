from django.contrib.auth.models import User, Group
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import check_password
from arches.app.models.system_settings import settings
from arches.app.models.models import ExternalOauthToken
from datetime import datetime, timedelta
import requests
import logging 
import jwt
from jwt import PyJWKClient
from requests_oauthlib import OAuth2Session

class ExternalOauthAuthenticationBackend(ModelBackend):
    def authenticate(self, request, sso_authentication=False, **kwargs):
        try:
            if not sso_authentication or not request:
                return None
            
            # grab settings via oidc discovery or manual
            oauth2_settings = ExternalOauthAuthenticationBackend.get_oauth2_settings()
            validate_id_token = oauth2_settings['validate_id_token']
            uid_claim = oauth2_settings['uid_claim']
            client_id = oauth2_settings['app_id']
            app_secret = oauth2_settings['app_secret']
            redirect_uri = oauth2_settings['redirect_url']

            oauth = OAuth2Session(client_id, redirect_uri=redirect_uri)
            try:
                token_response = oauth.fetch_token(oauth2_settings['token_endpoint'], authorization_response=request.build_absolute_uri(), client_secret=app_secret, include_client_id=True)
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.error("Error getting id/access tokens", exc_info=1)
                raise e

            expires_in=token_response['expires_in']
            id_token=token_response['id_token']
            access_token=token_response['access_token']
            refresh_token=token_response['refresh_token'] if 'refresh_token' in token_response else None  

            if validate_id_token and id_token is not None: 
                alg = jwt.get_unverified_header(id_token)['alg']
                jwks_client = PyJWKClient(oauth2_settings['jwks_uri'])
                signing_key = jwks_client.get_signing_key_from_jwt(id_token)
                decoded_id_token = jwt.decode(id_token, signing_key.key, audience=client_id, algorithms=[alg])
            elif id_token is not None:
                decoded_id_token = jwt.decode(id_token, options={"verify_signature": False})

            username = decoded_id_token[uid_claim]

            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = None

            if user is None and "default_user_groups" in oauth2_settings:
                email = decoded_id_token['email'] if 'email' in decoded_id_token else None
                given_name = decoded_id_token['given_name'] if 'given_name' in decoded_id_token else None
                family_name = decoded_id_token['family_name'] if 'family_name' in decoded_id_token else None
                is_superuser = True if 'create_as_superuser' in oauth2_settings and oauth2_settings['create_as_superuser'] else False
                is_staff = True if 'create_as_staff' in oauth2_settings and oauth2_settings['create_as_staff'] else False
                user = User.objects.create_user(username, email=email, first_name=given_name, last_name=family_name, is_staff=is_staff, is_superuser=is_superuser)
                for group in oauth2_settings["default_user_groups"]:
                    django_group = Group.objects.get(name=group)
                    user.groups.add(django_group)
                user.save()

            if user is None:
                return None

            token = ExternalOauthAuthenticationBackend.get_token(user)
            if(token != None and token.access_token_expiration > datetime.now()):
                return user


            expiration_date = datetime.now() + timedelta(seconds=int(expires_in))
            ExternalOauthToken.objects.filter(user=user).delete()
            token_record = ExternalOauthToken.objects.create(
                user = user,
                access_token = access_token,
                refresh_token = refresh_token,
                id_token = id_token,
                access_token_expiration = expiration_date
            )
            token_record.save()
            return user
                
        except Exception as e:
            raise e

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
    
    def get_token(user):
        try: 
            token = ExternalOauthToken.objects.get(user=user)
            return token
        except ExternalOauthToken.DoesNotExist:
            return None
    
    def get_oauth2_settings() -> dict or None:
        oauth_settings = {**{}, **settings.EXTERNAL_OAUTH_CONFIGURATION}
        if('oidc_discovery_url' in oauth_settings):
            try:
                r = requests.get(oauth_settings['oidc_discovery_url'])
  
                response_json = r.json()
                oauth_settings["jwks_uri"] = response_json["jwks_uri"]
                oauth_settings["token_endpoint"] = response_json["token_endpoint"]
                oauth_settings["authorization_endpoint"] = response_json["authorization_endpoint"]
                return oauth_settings
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.error("Error with oidc discovery", exc_info=1)
                raise e


        return oauth_settings if len(oauth_settings) > 0 else None
        