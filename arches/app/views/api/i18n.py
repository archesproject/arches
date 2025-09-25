import json
import logging
import os

from django.utils.translation import get_language, gettext as _

from arches.app.models.system_settings import settings
from arches.app.utils.response import JSONResponse
from arches.app.views.api import APIBase
from arches.settings_utils import list_arches_app_paths

logger = logging.getLogger(__name__)


class GetFrontendI18NData(APIBase):
    def get(self, request):
        user_language = get_language()

        language_file_path = []

        language_file_path.append(
            os.path.join(settings.ROOT_DIR, "locale", user_language + ".json")
        )

        for arches_app_path in list_arches_app_paths():
            language_file_path.append(
                os.path.join(arches_app_path, "locale", user_language + ".json")
            )

        language_file_path.append(
            os.path.join(settings.APP_ROOT, "locale", user_language + ".json")
        )

        localized_strings = {}
        for lang_file in language_file_path:
            try:
                with open(lang_file, "r", encoding="utf-8") as f:
                    localized_strings = json.load(f)[user_language] | localized_strings
            except FileNotFoundError:
                pass

        return JSONResponse(
            {
                "enabled_languages": {
                    language_tuple[0]: str(language_tuple[1])
                    for language_tuple in settings.LANGUAGES
                },
                "translations": {user_language: localized_strings},
                "language": user_language,
            }
        )
