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

from arches.app.models.system_settings import settings
from django.core.exceptions import ImproperlyConfigured

# from importlib import import_module


class SearchEngineFactory(object):
    def create(
        self,
        hosts=settings.ELASTICSEARCH_HOSTS,
        prefix=settings.ELASTICSEARCH_PREFIX,
        connection_options=settings.ELASTICSEARCH_CONNECTION_OPTIONS,
    ):
        backend = settings.SEARCH_BACKEND
        components = backend.split(".")
        classname = components[len(components) - 1]
        modulename = (".").join(components[0 : len(components) - 1])
        _temp = __import__(
            modulename, globals(), locals(), [classname]
        )  # in py3, level must be >= 0
        args = {}
        args["prefix"] = prefix
        if "cloud_id" not in settings.ELASTICSEARCH_CONNECTION_OPTIONS:
            args["hosts"] = hosts

        return getattr(_temp, classname)(**args, **connection_options)


SearchEngineInstance = SearchEngineFactory().create()
