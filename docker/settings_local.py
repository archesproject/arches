import os
from django.core.exceptions import ImproperlyConfigured
import ast
import requests
import sys
from settings import *


def get_env_variable(var_name):
    msg = "Set the %s environment variable"
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = msg % var_name
        raise ImproperlyConfigured(error_msg)


def opt_env(var_name, default_resp=None):
    try:
        return os.environ[var_name]
    except KeyError:
        return default_resp


# options are either "PROD" or "DEV" (installing with Dev mode set gets you extra dependencies)
MODE = get_env_variable('DJANGO_MODE')

DEBUG = ast.literal_eval(get_env_variable('DJANGO_DEBUG'))

COUCHDB_URL = 'http://{}:{}@{}:{}'.format(get_env_variable('COUCHDB_USER'), get_env_variable('COUCHDB_PASS'),
                                          get_env_variable('COUCHDB_HOST'),
                                          get_env_variable('COUCHDB_PORT'))  # defaults to localhost:5984

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': get_env_variable('PGDBNAME'),
        'USER': get_env_variable('PGUSERNAME'),
        'PASSWORD': get_env_variable('PGPASSWORD'),
        'HOST': get_env_variable('PGHOST'),
        'PORT': get_env_variable('PGPORT'),
        'POSTGIS_TEMPLATE': 'template_postgis_20',
    }
}

ELASTICSEARCH_HTTP_PORT = get_env_variable('ESPORT')
ELASTICSEARCH_HOSTS = [
    {'host': get_env_variable('ESHOST'), 'port': ELASTICSEARCH_HTTP_PORT}
]

USER_ELASTICSEARCH_PREFIX = opt_env('ELASTICSEARCH_PREFIX')
if USER_ELASTICSEARCH_PREFIX:
    ELASTICSEARCH_PREFIX = USER_ELASTICSEARCH_PREFIX

ALLOWED_HOSTS = get_env_variable('DOMAIN_NAMES').split()

USER_SECRET_KEY = opt_env('DJANGO_SECRET_KEY')
if USER_SECRET_KEY:
    # Make this unique, and don't share it with anybody.
    SECRET_KEY = USER_SECRET_KEY

STATIC_ROOT = '/static_root'

#############################################
# ==============LDAP CONFIG START============
#############################################

# set the following to enable the LDAP authentication backend
# To install:
# sudo apt-get install libsasl2-dev python-dev libldap2-dev libssl-dev
# (ENV) $ pip install django-auth-ldap

ARCHES_USE_LDAP = opt_env("USE_LDAP", False)

if ARCHES_USE_LDAP:
    import ldap
    from django_auth_ldap.config import LDAPSearch

    # Baseline configuration.
    AUTHENTICATION_BACKENDS = ('django_auth_ldap.backend.LDAPBackend',) + AUTHENTICATION_BACKENDS
    AUTH_LDAP_SERVER_URI = get_env_variable("AUTH_LDAP_SERVER_URI")

    # Some ldap options for TLS (https://python-ldap.readthedocs.io/en/latest/reference/ldap.html#ldap-options)
    # AUTH_LDAP_CONNECTION_OPTIONS = {
    #   ldap.OPT_REFERRALS: 0,
    #   ldap.OPT_PROTOCOL_VERSION: 3
    #   ldap.OPT_X_TLS_CACERTFILE: '/absolute/path/to/ldap/cert/file.pem',
    #   ldap.OPT_X_TLS: ldap.OPT_X_TLS_DEMAND,
    #   ldap.OPT_X_TLS_DEMAND: True,
    # }

    # By default, all mapped user fields will be updated each time the user logs in.
    # To disable this, set AUTH_LDAP_ALWAYS_UPDATE_USER to False
    AUTH_LDAP_ALWAYS_UPDATE_USER = True   # Default

    AUTH_LDAP_BIND_DN = opt_env("AUTH_LDAP_BIND_DN", "")
    AUTH_LDAP_BIND_PASSWORD = opt_env("AUTH_LDAP_BIND_PASSWORD", "")
    AUTH_LDAP_USER_SEARCH = LDAPSearch(
        get_env_variable("AUTH_LDAP_BASE_DN_SEARCH"),
        ldap.SCOPE_SUBTREE,
        '(uid=%(user)s)',
    )
    # Or:
    # AUTH_LDAP_USER_DN_TEMPLATE = 'uid=%(user)s,ou=users,dc=example,dc=org'

    AUTH_LDAP_USER_ATTR_MAP = {"first_name": "givenName",
                               "last_name": "sn",
                               "email": "mail"}
