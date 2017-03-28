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

MODE = get_env_variable('DJANGO_MODE') #options are either "PROD" or "DEV" (installing with Dev mode set, get's you extra dependencies)
DEBUG = ast.literal_eval(get_env_variable('DJANGO_DEBUG'))

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': get_env_variable('PGDBNAME'),
        'USER': 'postgres',
        'PASSWORD': get_env_variable('PGPASSWORD'),
        'HOST': get_env_variable('PGHOST'),
        'PORT': get_env_variable('PGPORT'),
        'POSTGIS_TEMPLATE': 'template_postgis_20',
    }
}

ELASTICSEARCH_HTTP_PORT = get_env_variable('ESPORT')
ELASTICSEARCH_HOSTS = [
    { 'host': get_env_variable('ESHOST'), 'port': ELASTICSEARCH_HTTP_PORT }
]

MAPBOX_API_KEY = get_env_variable('MAPBOX_API_KEY')


ALLOWED_HOSTS = get_env_variable('DOMAIN_NAMES').split()

# Fix for AWS ELB returning false bad health: ELB contacts EC2 instances through their private ip.
# An AWS service is called to get this private IP of the current EC2 node. Then the IP is added to ALLOWS_HOSTS so that Django answers to it.
EC2_PRIVATE_IP = None
try:
    EC2_PRIVATE_IP = requests.get('http://169.254.169.254/latest/meta-data/local-ipv4', timeout=0.01).text
except requests.exceptions.RequestException:
    pass
if EC2_PRIVATE_IP:
    ALLOWED_HOSTS.append(EC2_PRIVATE_IP)
EC2_PUBLIC_HOSTNAME = None
try:
    EC2_PUBLIC_HOSTNAME = requests.get('http://169.254.169.254/latest/meta-data/public-hostname', timeout=0.01).text
except requests.exceptions.RequestException:
    pass
if EC2_PUBLIC_HOSTNAME:
    ALLOWED_HOSTS.append(EC2_PUBLIC_HOSTNAME)