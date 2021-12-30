from collections import namedtuple
from datetime import datetime
import glob
import os
import pathlib
from typing import List
import polib

from arches.app.models.system_settings import settings
from arches.app.models.fields.i18n import I18n_String
from arches.app.models.models import CardModel, CardXNodeXWidget

ArchesPOFile = namedtuple('ArchesPOFile', ['language', 'file'])

class ArchesPOFileFetcher():
    """Gets PO files for processing"""
    def get_po_file(self, lang, overwrite=False) -> polib.POFile:
        """Gets a graph PO file for a specific language"""
        path = settings.LOCALE_PATHS[0]
        po_path = os.path.join(path, lang, "LC_MESSAGES")
        pathlib.Path(po_path).mkdir(parents=True, exist_ok=True)
        pofilepath = os.path.join(po_path, "graphs.po")
        if overwrite or not os.path.exists(pofilepath):
            open(pofilepath, 'w').close()
            return self.setup_file(polib.pofile(pofilepath))

        for pofilepath in glob.glob(os.path.join(po_path, "graphs.po")):
            return self.setup_file(polib.pofile(pofilepath))

    def get_po_files(self, lang=None, overwrite=False) -> List[ArchesPOFile]:
        """Get an array of PO files being loaded or written"""
        files = []
        
        if lang:
            files.append((lang, self.get_po_file(lang), overwrite))
        else:
            for language in settings.LANGUAGES:
                files.append(ArchesPOFile(language[0], self.get_po_file(language[0], overwrite)))
        return files

    def setup_file(self, pofile: polib.POFile) -> polib.POFile:
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

class ArchesPOWriter():
    """Writes a PO file from arches graph tables"""
    def __init__(self, pofile: polib.POFile, id_language: str, target_language: str) -> None:
        self.pofile = pofile
        self.id_language = id_language
        self.target_language = target_language

    def populate(self):
        """Populates a PO file with entries from several arches graph tables"""
        self.populate_from_card_x_node_x_widget(CardXNodeXWidget.objects.all())
        self.populate_from_cards(CardModel.objects.all())

        self.pofile.save()
    
    def populate_from_card_x_node_x_widget(self, queryset):
        for row in queryset:
            try:
                i18n_properties = row.config["i18n_properties"]
                for prop in i18n_properties:
                    self.append(row.config[prop], "cards_x_nodes_x_widgets")
                self.append(row.label, "cards_x_nodes_x_widgets")
            except KeyError:
                pass
    
    def populate_from_cards(self, queryset):
        for row in queryset:
            try:
                self.append(row.name, 'cards')
                self.append(row.description, 'cards')
                self.append(row.instructions, 'cards')
                self.append(row.helptitle, 'cards')
                self.append(row.helptext, 'cards')
            except KeyError:
                pass

    def append(self, cell: I18n_String, origin=None):
        """
        append a new entry consisting of msgid and msgstr from an I18n_string field to the po file
        """
        if origin is None:
            occurrences = []
        else:
            occurrences = [(origin, "1")]
        
        msgid = cell[self.id_language]
        if self.target_language in cell:
            msgstr = cell[self.target_language]
        else:
            msgstr = ""

        if(msgid is not None and msgid != ""):
            entry = polib.POEntry(msgid=msgid, msgstr=msgstr, occurrences=occurrences)
            try:
                self.pofile.append(entry)
            
            # happens when there are duplicates, no need to do anything with it
            except ValueError:
                pass

class ArchesPOLoader():
    """Loads a PO file into arches graph tables"""
    def __init__(self, pofile: polib.POFile, id_language: str, target_language: str) -> None:
        self.pofile = pofile
        self.id_language = id_language
        self.target_language = target_language 
    
    def load(self):
        """Iterates through database, Loading translations from PO files"""
        cards_x_nodes_x_widgets = CardXNodeXWidget.objects.all()
        cards = CardModel.objects.all()

        # if lang and target lang are the same, msgstr will always be empty; do not load
        if self.id_language == self.target_language:
            return

        for row in cards_x_nodes_x_widgets:
            try:
                i18n_properties = row.config["i18n_properties"]
                for prop in i18n_properties:
                    entry = self.pofile.find(row.config[prop][self.id_language])
                    if(entry is not None and entry.msgstr != ""):
                        row.config[prop][self.target_language] = entry.msgstr
                    else:
                        row.config[prop].pop(self.target_language, None)

                self.update_i18n_string_cell(row.label)

                row.save()
            except KeyError:
                pass

        for row in cards:
            self.update_i18n_string_cell(row.name)
            self.update_i18n_string_cell(row.description)
            self.update_i18n_string_cell(row.instructions)
            self.update_i18n_string_cell(row.helptitle)
            self.update_i18n_string_cell(row.helptext)

            row.save()
    
    def update_i18n_string_cell(self, cell: I18n_String):
        """Updates an i18n string field with a translated language value"""
        try:
            entry = self.pofile.find(cell[self.id_language])
            if(entry is not None and entry.msgstr != ""):
                cell[self.target_language] = entry.msgstr
            else:
                cell.pop(self.target_language, None)
        except KeyError:
            pass