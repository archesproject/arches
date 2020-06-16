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
import os
import zipfile
import datetime
from io import BytesIO
from arches.app.utils import import_class_from_string
from arches.app.models.system_settings import settings
from django.http import HttpResponse


class ResourceExporter(object):
    def __init__(self, format=None, **kwargs):
        kwargs["format"] = format
        self.writer = import_class_from_string(settings.RESOURCE_FORMATTERS[format])(**kwargs)

    def export(self, graph_id=None, resourceinstanceids=None):
        resources = self.writer.write_resources(graph_id=graph_id, resourceinstanceids=resourceinstanceids)
        return resources
