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
import logging
import trace
from typing import List
import urllib.request, urllib.error, urllib.parse
import json
import glob
import pathlib
import polib
from arches.app import models
from arches.app.models.fields.i18n import I18n_String
from arches.app.models.models import CardXNodeXWidget, CardModel, Widget
from datetime import datetime
import time
import traceback
from arches.management.commands import utils
from arches.app.models.system_settings import settings
from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Commands for managing internationalization in Arches

    """

    def add_arguments(self, parser):
        parser.add_argument(
            "operation",
            nargs="?",
            choices=["makemessages", "loadmessages"],
            help="Operation Type; "
            + "'makemessages'=Creates PO file messages from database "
            + "'loadmessages'=Reads PO file messages to the database "
        )
        parser.add_argument(
            "-l", "--lang", action="store", dest="lang", default=None, help=""
        )

    def handle(self, *args, **options):
        if options["operation"] == "makemessages":
            self.make_messages(lang=options["lang"])
        if options["operation"] == "loadmessages":
            self.load_messages(lang=options["lang"])

    def get_po_file(self, lang):
        """Gets a graph PO file for a specific language"""
        path = settings.LOCALE_PATHS[0]
        po_path = os.path.join(path, lang, "LC_MESSAGES")
        for pofilepath in glob.glob(os.path.join(po_path, "graphs.po")):
            return setup_file(polib.pofile(pofilepath))
        print(po_path)
        pathlib.Path(po_path).mkdir(parents=True, exist_ok=True)
        pofilepath = os.path.join(po_path, "graphs.po")
        if not os.path.exists(pofilepath):
            open(pofilepath, 'w').close()
        return setup_file(polib.pofile(pofilepath))

    def get_po_files(self, lang=None):
        """Get an array of PO files being loaded or written"""
        files = []
        if lang:
            files.append((lang, self.get_po_file(lang)))
        else:
            for lang, lang_name in settings.LANGUAGES:
                files.append((lang, self.get_po_file(lang)))
        return files

    def make_messages(self, lang=None):
        """Creates PO files for given language(s) (all if None)"""
        files = self.get_po_files(lang)
        for file in files:
            self.populate_po_file(file[1], settings.LANGUAGE_CODE, file[0])

    def populate_po_file(self, pofile: polib.POFile, lang: str, target_language: str):
        """Populates a PO file with entries in a particular language of msgids"""
        cards_x_nodes_x_widgets = CardXNodeXWidget.objects.all()
        for row in cards_x_nodes_x_widgets:
            try:
                i18n_properties = row.config["i18n_properties"]
                for prop in i18n_properties:
                    append_to_po_file(pofile, row.config[prop], lang, target_language, "cards_x_nodes_x_widgets")
                append_to_po_file(pofile, row.label, lang, target_language, "cards_x_nodes_x_widgets")
            except KeyError:
                pass

        cards = CardModel.objects.all()
        for row in cards:
            try:
                print("rowname", row.name, row.name[lang])
                append_to_po_file(pofile, row.name, lang, target_language, 'cards')
                append_to_po_file(pofile, row.description, lang, target_language, 'cards')
                append_to_po_file(pofile, row.instructions, lang, target_language, 'cards')
                append_to_po_file(pofile, row.helptitle, lang, target_language, 'cards')
                append_to_po_file(pofile, row.helptext, lang, target_language, 'cards')
            except KeyError:
                print('boom')
                pass

        pofile.save()

    def load_messages(self, lang):
        """Loads translated strings from po file/s"""
        files = self.get_po_files(lang)
        for file in files:
            self.load_po_file(file[1], settings.LANGUAGE_CODE, file[0])

    def load_po_file(self, pofile: polib.POFile, lang, target_language):
        """Iterates through database, Loading translations from PO files"""
        cards_x_nodes_x_widgets = CardXNodeXWidget.objects.all()
        cards = CardModel.objects.all()

        # if lang and target lang are the same, msgstr will always be empty; no need for translation
        if lang == target_language:
            return

        for row in cards_x_nodes_x_widgets:
            try:
                i18n_properties = row.config["i18n_properties"]
                for prop in i18n_properties:
                    entry = pofile.find(row.config[prop][lang])
                    if(entry is not None and entry.msgstr != ""):
                        row.config[prop][target_language] = entry.msgstr
                    else:
                        row.config[prop].pop(target_language, None)

                update_i18n_string_cell(pofile, row.label, lang, target_language)

                row.save()
            except KeyError:
                pass

        for row in cards:
            update_i18n_string_cell(pofile, row.name, lang, target_language)
            update_i18n_string_cell(pofile, row.description, lang, target_language)
            update_i18n_string_cell(pofile, row.instructions, lang, target_language)
            update_i18n_string_cell(pofile, row.helptitle, lang, target_language)
            update_i18n_string_cell(pofile, row.helptext, lang, target_language)

            row.save()

def append_to_po_file(pofile, cell: I18n_String, lang: str, target_lang: str, origin=None):
    """
    Given a PO File, append a new entry consisting of msgid and msgstr
    """
    if origin is None:
        occurrences = []
    else:
        occurrences = [(origin, "1")]
    print(origin, cell)
    msgid = cell[lang]
    if target_lang in cell:
        msgstr = cell[target_lang]
    else:
        print('not in cell', msgid, target_lang)
        msgstr = ""

    if(msgid is not None and msgid != ""):
        entry = polib.POEntry(msgid=msgid, msgstr=msgstr, occurrences=occurrences)
        try:
            print('appending')
            pofile.append(entry)
        except ValueError:
            pass

def update_i18n_string_cell(pofile: polib.POFile, cell: I18n_String, lang, target_language):
    """Updates an i18n string field with a translated language value"""
    try:
        entry = pofile.find(cell[lang])
        if(entry is not None and entry.msgstr != ""):
            cell[target_language] = entry.msgstr
        else:
            cell.pop(target_language, None)
    except KeyError:
        pass

def setup_file(pofile: polib.POFile, lang="en") -> polib.POFile:
    """Given a PO file, set up metadata and duplicate check property"""
    current_time = datetime.now()
    pofile.check_for_duplicates = True
    pofile.metadata = {
        'Project-Id-Version': '1.0',
        'Report-Msgid-Bugs-To': "dev@fargeo.com",
        'POT-Creation-Date': current_time.strftime("%Y-%m-%d %H:%M:%S%z"),
        'PO-Revision-Date': current_time.strftime("%Y-%m-%d %H:%M:%S%z"),
        'MIME-Version': '1.0',
        'Content-Type': 'text/plain; charset=utf-8',
        'Content-Transfer-Encoding': '8bit',
    }

    return pofile