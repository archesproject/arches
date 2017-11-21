import time
from datetime import datetime
from django.contrib.auth.models import User, Group, AnonymousUser
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject
from django.utils.six import text_type
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
    def get_user_from_token(self, token):
        decoded_json = jws.verify(token, settings.JWT_KEY, algorithms=['HS256'])
        #jwt.decode(token, 'secret', algorithms='HS256')
        decoded_dict = JSONDeserializer().deserialize(decoded_json)

        username = decoded_dict.get('username', None)
        expiry = decoded_dict.get('expiry', None)

        print 'in get_user_from_token'


        user = AnonymousUser()
        try:
            user = User.objects.get(username=username)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if not user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        if int(expiry) < int(time.time()):
            raise exceptions.AuthenticationFailed(_('Token Expired.'))

        return user

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

        # if hasattr(request, 'session') and request.user.is_anonymous()
        # if not (hasattr(request, 'session') and request.user.is_anonymous()):
        # assert hasattr(request, 'session') and request.user.is_anonymous()
        print 'token'
        print request.token



class TokenMiddleware(MiddlewareMixin):
    # pulled from http://www.django-rest-framework.org
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


# from django.utils.functional import SimpleLazyObject
# from django.contrib.auth.models import AnonymousUser

# def get_user_jwt(request):
#     """
#     Replacement for django session auth get_user & auth.get_user
#      JSON Web Token authentication. Inspects the token for the user_id,
#      attempts to get that user from the DB & assigns the user on the
#      request object. Otherwise it defaults to AnonymousUser.

#     This will work with existing decorators like LoginRequired  ;)

#     Returns: instance of user object or AnonymousUser object
#     """

#     user = None
#     try:
#         user_jwt = request.user
#         if user_jwt is not None:
#             # store the first part from the tuple (user, obj)
#             user = user_jwt[0]
#     except:
#         pass

#     return user or AnonymousUser()


# class JWTAuthenticationMiddleware(MiddlewareMixin):
#     """ Middleware for authenticating JSON Web Tokens in Authorize Header """
#     def process_request(self, request):
#         request.user = SimpleLazyObject(lambda : get_user_jwt(request))


# class JWTAuthentication(object):

#     """
#     Simple token based authentication.
#     Clients should authenticate by passing the token key in the "Authorization"
#     HTTP header, prepended with the string "Token ".  For example:
#     Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
#     """

#     def authenticate(self, request):
#         auth = get_authorization_header(request).split()

#         if not auth or auth[0].lower() != b'token':
#             return None

#         try:
#             token = auth[1].decode()
#         except UnicodeError:
#             msg = _('Invalid token header. Token string should not contain invalid characters.')
#             raise exceptions.AuthenticationFailed(msg)

#         return self.authenticate_credentials(token)

#     def authenticate_credentials(self, payload):

#         decoded_dict = jws.verify(payload, 'seKre8', algorithms=['HS256'])

#         username = decoded_dict.get('username', None)
#         expiry = decoded_dict.get('expiry', None)

#         try:
#             usr = User.objects.get(username=username)
#         except model.DoesNotExist:
#             raise exceptions.AuthenticationFailed(_('Invalid token.'))

#         if not usr.is_active:
#             raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

#         if expiry < datetime.date.today():
#             raise exceptions.AuthenticationFailed(_('Token Expired.'))

#         return (usr, payload)

#     def authenticate_header(self, request):
#         return 'Token'