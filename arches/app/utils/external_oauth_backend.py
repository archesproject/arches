from typing import Tuple
from django.contrib.auth.models import User, Group
from django.contrib.auth.backends import ModelBackend
from django.urls import reverse
from arches.app.models.system_settings import settings
from arches.app.models.models import ExternalOauthToken
from datetime import datetime, timedelta
import requests
import logging
import jwt
from jwt import PyJWKClient
from requests_oauthlib import OAuth2Session

logger = logging.getLogger(__name__)


class ExternalOauthAuthenticationBackend(ModelBackend):
    def authenticate(self, request, sso_authentication=False, **kwargs):
        try:
            if not sso_authentication or not request:
                return None

            oauth2_settings = ExternalOauthAuthenticationBackend.get_oauth2_settings()
            validate_id_token = (
                oauth2_settings["validate_id_token"]
                if "validate_id_token" in oauth2_settings
                else True
            )
            uid_claim = oauth2_settings["uid_claim"]
            client_id = oauth2_settings["app_id"]
            app_secret = oauth2_settings["app_secret"]
            redirect_uri = request.build_absolute_uri(
                reverse("external_oauth_callback")
            )
            uid_claim_source = (
                oauth2_settings["uid_claim_source"]
                if "uid_claim_source" in oauth2_settings
                else "id_token"
            )

            oauth = OAuth2Session(
                client_id,
                redirect_uri=redirect_uri,
                state=request.session["oauth_state"],
            )
            try:
                token_response = oauth.fetch_token(
                    oauth2_settings["token_endpoint"],
                    authorization_response=request.build_absolute_uri(),
                    client_secret=app_secret,
                    include_client_id=True,
                )
            except Exception as e:
                logger.error("Error getting id/access tokens", exc_info=True)
                raise e  # raise, otherwise this will mysteriously smother.

            expires_in = token_response["expires_in"]
            id_token = token_response["id_token"]
            access_token = token_response["access_token"]
            refresh_token = (
                token_response["refresh_token"]
                if "refresh_token" in token_response
                else None
            )

            if uid_claim_source == "id_token" and id_token is not None:
                if validate_id_token:
                    alg = jwt.get_unverified_header(id_token)["alg"]
                    jwks_client = PyJWKClient(oauth2_settings["jwks_uri"])
                    signing_key = jwks_client.get_signing_key_from_jwt(id_token)
                    decoded_id_token = jwt.decode(
                        id_token, signing_key.key, audience=client_id, algorithms=[alg]
                    )
                else:
                    decoded_id_token = jwt.decode(
                        id_token, options={"verify_signature": False}
                    )

                username = (
                    decoded_id_token[uid_claim]
                    if decoded_id_token and uid_claim in decoded_id_token
                    else None
                )
            else:  # this can be extended to pull user claims from the oidc user endpoint if desired
                username = None

            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = None

            # default_user_groups are used to assign groups to users that don't yet exist.
            if user is None and "default_user_groups" in oauth2_settings:
                email = (
                    decoded_id_token["email"] if "email" in decoded_id_token else None
                )
                given_name = (
                    decoded_id_token["given_name"]
                    if "given_name" in decoded_id_token
                    else ""
                )
                family_name = (
                    decoded_id_token["family_name"]
                    if "family_name" in decoded_id_token
                    else ""
                )
                is_superuser = (
                    True
                    if "create_as_superuser" in oauth2_settings
                    and oauth2_settings["create_as_superuser"]
                    else False
                )
                is_staff = (
                    True
                    if "create_as_staff" in oauth2_settings
                    and oauth2_settings["create_as_staff"]
                    else False
                )
                user = User.objects.create_user(
                    username,
                    email=email,
                    first_name=given_name,
                    last_name=family_name,
                    is_staff=is_staff,
                    is_superuser=is_superuser,
                )
                for group in oauth2_settings["default_user_groups"]:
                    django_group = Group.objects.get(name=group)
                    user.groups.add(django_group)
                user.save()

            if user is None:
                return None

            token = ExternalOauthAuthenticationBackend.get_token(user)
            if token is not None and token.access_token_expiration > datetime.now():
                return user

            expiration_date = datetime.now() + timedelta(seconds=int(expires_in))
            ExternalOauthToken.objects.filter(user=user).delete()
            token_record = ExternalOauthToken.objects.create(
                user=user,
                access_token=access_token,
                refresh_token=refresh_token,
                id_token=id_token,
                access_token_expiration=expiration_date,
            )
            token_record.save()
            return user

        except Exception as e:
            logger.error("Error in external oauth backend", exc_info=True)
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

    def get_token(user: User) -> ExternalOauthToken or None:
        """Get the token record for a particular user"""
        try:
            token = ExternalOauthToken.objects.get(user=user)
            return token
        except ExternalOauthToken.DoesNotExist:
            return None

    def get_token_for_username(
        username: str,
    ) -> Tuple[ExternalOauthToken, User] or None:
        """Get the token record (and user) for a particular username"""
        try:
            user = User.objects.get(username=username)
            return ExternalOauthAuthenticationBackend.get_token(user), user
        except User.DoesNotExist:
            return (None, None)

    def get_oauth2_settings() -> dict or None:
        """Get oauth2 settings from oidc endpoint or settings.EXTERNAL_OAUTH_CONFIGURATION"""
        oauth_settings = {**{}, **settings.EXTERNAL_OAUTH_CONFIGURATION}
        if "oidc_discovery_url" in oauth_settings:
            try:
                r = requests.get(oauth_settings["oidc_discovery_url"])

                response_json = r.json()
                oauth_settings["jwks_uri"] = response_json["jwks_uri"]
                oauth_settings["token_endpoint"] = response_json["token_endpoint"]
                oauth_settings["authorization_endpoint"] = response_json[
                    "authorization_endpoint"
                ]
                oauth_settings["end_session_endpoint"] = response_json[
                    "end_session_endpoint"
                ]
                return oauth_settings
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.error("Error with oidc discovery", exc_info=1)
                raise e

        return oauth_settings if len(oauth_settings) > 0 else None

    def get_authorization_url(request) -> Tuple[str, str]:
        """Return authorization URL to redirect user to and XSRF state token"""
        oauth2_settings = ExternalOauthAuthenticationBackend.get_oauth2_settings()
        client_id = oauth2_settings["app_id"]
        redirect_uri = request.build_absolute_uri(reverse("external_oauth_callback"))
        scope = oauth2_settings["scopes"]
        auth_url = oauth2_settings["authorization_endpoint"]

        oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scope)

        return oauth.authorization_url(auth_url)
