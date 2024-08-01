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

import logging
import importlib

from django.conf import settings

logger = logging.getLogger(__name__)


class ThumbnailFactory(object):
    def create(self):
        if settings.THUMBNAIL_GENERATOR:
            try:
                backend = settings.THUMBNAIL_GENERATOR
                components = backend.split(".")
                classname = components[len(components) - 1]
                modulename = (".").join(components[0 : len(components) - 1])
                return getattr(importlib.import_module(modulename), classname)()
            except:
                logger.warning(
                    f"A 'THUMBNAIL_GENERATOR' in settings.py is specified but can't be found or instantiated.  Thumbnails for uploaded files won't be created"
                )
                return None
        else:
            logger.info(
                f"A thumbnail generator isn't specified.  Set 'THUMBNAIL_GENERATOR' in settings.py to enable generation of thumbnails for uploded files."
            )
            return None


ThumbnailGeneratorInstance = ThumbnailFactory().create()
