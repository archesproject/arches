import time
from django.contrib.auth.models import User, AnonymousUser
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject
from django.utils.six import text_type
from django.utils.translation import ugettext as _
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from jose import jwt, jws

HTTP_HEADER_ENCODING = 'iso-8859-1'

class SetAnonymousUser(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_anonymous():
            try:
                request.user = User.objects.get(username='anonymous')
            except:
                pass
            
        request.user.user_groups = [group.name for group in request.user.groups.all()]


class JWTAuthenticationMiddleware(MiddlewareMixin):
    """
    tries to setup the user on the request object based on the JSON web token passed in with the request

    """

    def get_user_from_token(self, token):
        decoded_json = jws.verify(token, settings.JWT_KEY, algorithms=[settings.JWT_ALGORITHM])
        decoded_dict = JSONDeserializer().deserialize(decoded_json)

        username = decoded_dict.get('username', None)
        expiration = decoded_dict.get('expiration', None)

        user = None
        try:
            user = User.objects.get(username=username)
        except:
            raise AuthenticationFailed(_('Invalid token.'))

        if not user.is_active:
            raise AuthenticationFailed(_('User inactive or deleted.'))

        if int(expiration) < int(time.time()):
            raise AuthenticationFailed(_('Token Expired.'))

        return user or AnonymousUser()

    def process_request(self, request):
        assert hasattr(request, 'token'), (
            "The JSON authentication middleware requires token middleware "
            "to be installed. Edit your MIDDLEWARE setting to insert "
            "'arches.app.utils.middleware.TokenMiddleware' before "
            "'arches.app.utils.middleware.JWTAuthenticationMiddleware'."
        )

        # if there is a session and the user isn't anonymous then don't modify request.user
        if request.user.is_anonymous() and request.token is not '':
            # try to get the user info from the token if it exists
            request.user = SimpleLazyObject(lambda: self.get_user_from_token(request.token))


class TokenMiddleware(MiddlewareMixin):
    """
    puts the Bearer token found in the request header onto the request object
    
    pulled from http://www.django-rest-framework.org

    """

    def get_authorization_header(self, request):
        """
        Return request's 'Authorization:' header, as a bytestring.
        Hide some test client ickyness where the header can be unicode.
        """
        auth = request.META.get('HTTP_AUTHORIZATION', b'').replace('Bearer ', '')
        if isinstance(auth, text_type):
            # Work around django test client oddness
            auth = auth.encode(HTTP_HEADER_ENCODING)
        return auth

    def process_request(self, request):
        token = self.get_authorization_header(request)
        request.token = token


class AuthenticationFailed(Exception):
    pass
