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
from arches.app.utils.i18n import (
    ArchesPOFileFetcher,
    ArchesPOLoader,
    ArchesPOWriter,
    LanguageSynchronizer,
)
from arches.app.models.system_settings import settings
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Commands for managing internationalization in Arches

    """

    def add_arguments(self, parser):
        parser.add_argument(
            "operation",
            nargs="?",
            choices=["makemessages", "loadmessages", "synclanguages"],
            help="Operation Type; "
            + "'makemessages'=Creates PO file messages from database "
            + "'loadmessages'=Reads PO file messages to the database "
            + "'synclanguages'=Synchronizes languages in settings with the user languages and publications ",
        )
        parser.add_argument(
            "-l", "--lang", action="store", dest="lang", default=None, help=""
        )

    def handle(self, *args, **options):
        if options["operation"] == "makemessages":
            self.make_messages(lang=options["lang"])
        if options["operation"] == "loadmessages":
            self.load_messages(lang=options["lang"])
        if options["operation"] == "synclanguages":
            self.sync_languages()

    def make_messages(self, lang=None):
        """Creates PO files for given language(s) (all if None)"""
        files = ArchesPOFileFetcher().get_po_files(lang, True)
        for file in files:
            ArchesPOWriter(file.file, settings.LANGUAGE_CODE, file.language).populate()

    def load_messages(self, lang):
        """Loads translated strings from po file/s"""
        files = ArchesPOFileFetcher().get_po_files(lang)
        for file in files:
            ArchesPOLoader(file.file, settings.LANGUAGE_CODE, file.language).load()

    def sync_languages(self):
        """
        Syncs languages in the settings file with languages in the database
        """
        LanguageSynchronizer.synchronize_settings_with_db()
