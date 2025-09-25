import os
from django.core.exceptions import ImproperlyConfigured
import ast


def get_env_variable(var_name):
    msg = "Set the %s environment variable"
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = msg % var_name
        raise ImproperlyConfigured(error_msg)


def get_optional_env_variable(var_name):
    try:
        return os.environ[var_name]
    except KeyError:
        return None


# options are either "PROD" or "DEV" (installing with Dev mode set gets you extra dependencies)
MODE = get_env_variable("DJANGO_MODE")

DEBUG = ast.literal_eval(get_env_variable("DJANGO_DEBUG"))

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": get_env_variable("PGDBNAME"),
        "USER": get_env_variable("PGUSERNAME"),
        "PASSWORD": get_env_variable("PGPASSWORD"),
        "HOST": get_env_variable("PGHOST"),
        "PORT": get_env_variable("PGPORT"),
        "POSTGIS_TEMPLATE": "template_postgis",
        "OPTIONS": {
            "options": "-c cursor_tuple_fraction=1",
        },
    }
}

CELERY_BROKER_URL = "amqp://{}:{}@rabbitmq_afs".format(
    get_env_variable("RABBITMQ_USER"), get_env_variable("RABBITMQ_PASS")
)  # RabbitMQ --> "amqp://guest:guest@localhost",  Redis --> "redis://localhost:6379/0"

CANTALOUPE_HTTP_ENDPOINT = "http://{}:{}".format(
    get_env_variable("CANTALOUPE_HOST"), get_env_variable("CANTALOUPE_PORT")
)
ELASTICSEARCH_HTTP_PORT = get_env_variable("ESPORT")
ELASTICSEARCH_HOSTS = [
    {
        "scheme": "http",
        "host": get_env_variable("ESHOST"),
        "port": int(ELASTICSEARCH_HTTP_PORT),
    }
]

USER_ELASTICSEARCH_PREFIX = get_optional_env_variable("ELASTICSEARCH_PREFIX")
if USER_ELASTICSEARCH_PREFIX:
    ELASTICSEARCH_PREFIX = USER_ELASTICSEARCH_PREFIX

ALLOWED_HOSTS = get_env_variable("DOMAIN_NAMES").split()

USER_SECRET_KEY = get_optional_env_variable("DJANGO_SECRET_KEY")
if USER_SECRET_KEY:
    # Make this unique, and don't share it with anybody.
    SECRET_KEY = USER_SECRET_KEY

STATIC_ROOT = "/static_root"
