import base64
from dataclasses import dataclass
import time
from typing import Optional, Tuple, Literal
import uuid
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
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography import x509

logger = logging.getLogger(__name__)
PrivateKeyTypes = rsa.RSAPrivateKey | ec.EllipticCurvePrivateKey
JWTAlgorithmType = Literal["RS256", "RS384", "RS512", "ES256", "ES384", "ES512"]
JWTAlgorithm: JWTAlgorithmType = "RS256"
HashAlgorithm = hashes.SHA1 | hashes.SHA256 | hashes.SHA384 | hashes.SHA512


@dataclass
class KeyInfo:
    """Certificate and private key information"""

    public_key: x509.Certificate | rsa.RSAPublicKey | ec.EllipticCurvePublicKey
    private_key: PrivateKeyTypes
    thumbprint: str


class ExternalOauthAuthenticationBackend(ModelBackend):
    def _load_private_key(
        self, key_path: str, password: Optional[bytes] = None
    ) -> PrivateKeyTypes:
        """
        Load private key from PEM file

        Args:
            key_path: Path to PEM-encoded private key file
            password: Optional password for encrypted keys

        Returns:
            Private key object (RSA or EC)
        """
        with open(key_path, "rb") as f:
            private_key = serialization.load_pem_private_key(
                f.read(), password=password, backend=default_backend()
            )
        return private_key

    def _load_certificate(self, cert_path: str) -> x509.Certificate:
        """
        Load certificate from PEM file

        Args:
            cert_path: Path to PEM-encoded certificate file

        Returns:
            X.509 certificate object
        """
        with open(cert_path, "rb") as f:
            cert = x509.load_pem_x509_certificate(f.read(), default_backend())
        return cert

    def _load_public_key(self, public_key: str) -> x509.Certificate:
        """
        Load public key from PEM file

        Args:
            cert_path: Path to PEM-encoded public key file

        Returns:
            X.509 certificate object
        """
        with open(public_key, "rb") as f:
            public_key = serialization.load_pem_public_key(
                f.read(), backend=default_backend()
            )
        return public_key

    def _create_client_assertion(
        self,
        client_id,
        audience,
        private_key,
        thumbprint=None,
        algorithm="RS256",
        validity_seconds=None,
    ):
        if validity_seconds is None:
            validity_seconds = 300  # default to 5 minutes
        now = int(time.time())

        headers = {"alg": algorithm, "typ": "JWT"}

        if thumbprint is not None:
            headers["x5t"] = thumbprint

        payload = {
            "aud": audience,
            "exp": now + validity_seconds,
            "iss": client_id,
            "jti": str(uuid.uuid4()),
            "nbf": now,
            "sub": client_id,
        }

        token = jwt.encode(payload, private_key, algorithm=algorithm, headers=headers)
        return token

    def _load_certificate_info(
        self,
        public_key_path: str,
        private_key_path: str,
        private_key_password: bytes = None,
    ) -> KeyInfo:
        """
        Load certificate and private key, calculate thumbprint

        Args:
            config: OAuth configuration

        Returns:
            CertificateInfo with loaded cert, key, and thumbprint
        """
        try:
            public_key = self._load_certificate(public_key_path)
        except ValueError:
            public_key = self._load_public_key(public_key_path)
        private_key = self._load_private_key(private_key_path, private_key_password)
        if type(public_key) is x509.Certificate:
            thumbprint = self._get_certificate_thumbprint(public_key)
        else:
            thumbprint = None

        return KeyInfo(
            public_key=public_key, private_key=private_key, thumbprint=thumbprint
        )

    def _get_certificate_thumbprint(
        self, cert: x509.Certificate, hash_algorithm: HashAlgorithm = None
    ) -> str:
        """
        Get the thumbprint of the certificate

        Args:
            cert: X.509 certificate
            hash_algorithm: Hash algorithm to use (default: SHA-1 for Azure compatibility)

        Returns:
            Base64url-encoded thumbprint
        """
        if hash_algorithm is None:
            hash_algorithm = hashes.SHA1()

        thumbprint = cert.fingerprint(hash_algorithm)
        return base64.urlsafe_b64encode(thumbprint).decode("utf-8").rstrip("=")

    def authenticate(self, request, sso_authentication=False, **kwargs):
        try:
            if not sso_authentication or not request:
                return None

            oauth2_settings = ExternalOauthAuthenticationBackend._get_oauth2_settings()
            validate_id_token = (
                oauth2_settings["validate_id_token"]
                if "validate_id_token" in oauth2_settings
                else True
            )
            uid_claim = oauth2_settings["uid_claim"]
            client_id = oauth2_settings["app_id"]
            app_secret = oauth2_settings.get("app_secret", None)
            token_endpoint = oauth2_settings["token_endpoint"]
            token_endpoint_auth_method = oauth2_settings.get(
                "token_endpoint_auth_method", "client_secret_basic"
            )
            redirect_uri = request.build_absolute_uri(
                reverse("external_oauth_callback")
            )
            uid_claim_source = (
                oauth2_settings["uid_claim_source"]
                if "uid_claim_source" in oauth2_settings
                else "id_token"
            )
            jwt_audience = oauth2_settings.get("jwt_audience", token_endpoint)
            public_key = oauth2_settings.get(
                "public_key", oauth2_settings.get("public_certificate", None)
            )

            oauth = OAuth2Session(
                client_id,
                redirect_uri=redirect_uri,
                state=request.session["oauth_state"],
            )
            try:

                if token_endpoint_auth_method == "client_secret_basic":
                    token_response = oauth.fetch_token(
                        token_endpoint,
                        authorization_response=request.build_absolute_uri(),
                        client_secret=app_secret,
                        include_client_id=True,
                    )
                elif token_endpoint_auth_method == "private_key_jwt":
                    cert_info = self._load_certificate_info(
                        public_key,
                        oauth2_settings["private_key"],
                        oauth2_settings.get("private_key_password", None),
                    )
                    client_assertion = self._create_client_assertion(
                        client_id,
                        jwt_audience,
                        cert_info.private_key,
                        cert_info.thumbprint,
                        validity_seconds=(
                            oauth2_settings["validity_seconds"]
                            if "validity_seconds" in oauth2_settings
                            else None
                        ),
                    )
                    token_response = oauth.fetch_token(
                        token_endpoint,
                        authorization_response=request.build_absolute_uri(),
                        client_assertion=client_assertion,
                        client_assertion_type="urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
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

    def get_token(user: User) -> Optional[ExternalOauthToken]:
        """Get the token record for a particular user"""
        try:
            token = ExternalOauthToken.objects.get(user=user)
            return token
        except ExternalOauthToken.DoesNotExist:
            return None

    def get_token_for_username(
        username: str,
    ) -> Optional[Tuple[ExternalOauthToken, User]]:
        """Get the token record (and user) for a particular username"""
        try:
            user = User.objects.get(username=username)
            return ExternalOauthAuthenticationBackend.get_token(user), user
        except User.DoesNotExist:
            return (None, None)

    def _get_oauth2_settings() -> Optional[dict]:
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
        oauth2_settings = ExternalOauthAuthenticationBackend._get_oauth2_settings()
        client_id = oauth2_settings["app_id"]
        redirect_uri = request.build_absolute_uri(reverse("external_oauth_callback"))
        scope = oauth2_settings["scopes"]
        auth_url = oauth2_settings["authorization_endpoint"]

        oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scope)

        return oauth.authorization_url(auth_url)
