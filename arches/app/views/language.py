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

from arches.app.utils.betterJSONSerializer import JSONSerializer
import logging

from arches.app.models import models

from arches.app.utils.response import JSONResponse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.generic import View
from arches.app.utils.betterJSONSerializer import JSONSerializer

logger = logging.getLogger(__name__)


class LanguageView(View):
    def get(self, request):
        try:
            languages = models.Language.objects.all()
            serializedLanguages = JSONSerializer().serializeToPython(languages)
        except models.Language.DoesNotExist:
            pass
        return JSONResponse({"languages": serializedLanguages})
