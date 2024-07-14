import os
import glob
import pathlib
import polib
from collections import namedtuple
from datetime import datetime
from typing import List
from arches.app.models.system_settings import settings
from arches.app.models.fields.i18n import I18n_String
from arches.app.models.models import (
    CardModel,
    CardXNodeXWidget,
    Language,
    PublishedGraph,
)
from django.contrib.gis.db.models import Model
from django.utils.translation import get_language, get_language_info
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer


ArchesPOFile = namedtuple("ArchesPOFile", ["language", "file"])


def localize_complex_input(input):
    """
    This method accepts an input of a list, dictionary, or model. It will then recursively update the
    inputs' data to return only the localized version of any i18n values

    Arguments:
    input -- (required) A list, dictionary, or model

    Returns:
    The input, with any internationalized string/text dictionaries localized to a string in the requested
    language, with the application language as a fallback.
    """

    def _recursive_localize(obj):
        if isinstance(obj, list):
            for item in obj:
                _recursive_localize(item)
        if isinstance(obj, dict):
            for key in obj.keys():
                try:
                    localized_value = get_localized_value(obj[key])
                    obj[key] = (
                        localized_value["value"]
                        if isinstance(localized_value, dict)
                        else localized_value
                    )
                except:
                    _recursive_localize(obj[key])
        if isinstance(obj, Model):
            for field in obj._meta.get_fields():
                data = getattr(obj, field.name)
                _recursive_localize(data)
        return obj

    return _recursive_localize(input)


def get_localized_value(obj, lang=None, return_lang=False):
    """
    This method accepts a localized object or a simple string
    eg: obj => {"en": "tree", "es": "arbol"}
    eg: simple string => "tree"
    and attempts to return the string based on the requested language


    If lang is specified it will return the value of the string with that language key
    or th string

    Arguments:
    obj -- (required) a localized object or a simple string

    Keyword Arguments:
    lang -- (optional) the specific value to return from the obj that has that language
    return_lang -- (optional) False (default) to return just the
        string value of the requested language
        True to return an object keyed by the language

    Returns:
        the value of the string in "obj" that was keyed to the requested language
        or an obj with just a single languag

    Examples:
        if obj = {"en": "tree", "es": "arbol"} and lang is "es" then will reutrn "arbol"
        or {"es": "arbol"} if "return_lang" is True

        if lang isn't specified, then the activated language will be used.

    """
    lang = get_language() if lang is None else lang
    if not isinstance(obj, dict):
        return {lang: obj} if return_lang else obj
    else:
        found_lang = None
        if lang in obj:
            found_lang = lang
        else:
            for langcode in obj.keys():
                if langcode.split("-")[0] == lang.split("-")[0]:
                    found_lang = langcode

            if settings.LANGUAGE_CODE in obj:
                found_lang = settings.LANGUAGE_CODE

        if found_lang not in obj:
            raise Exception()

        return {found_lang: obj[found_lang]} if return_lang else obj[found_lang]


def rank_label(kind="prefLabel", source_lang="", target_lang=""):
    """Rank a label language, preferring prefLabel over altLabel,
    the target language over the system language, and both of those
    languages over other languages.
    """

    if kind == "prefLabel":
        rank = 10
    elif kind == "altLabel":
        rank = 4
    else:
        rank = 1

    label_language_exact = source_lang.lower()
    label_language_fuzzy = source_lang.split("-")[0].lower()
    user_language_exact = (target_lang or get_language()).lower()
    user_language_fuzzy = user_language_exact.split("-")[0].lower()
    system_language_exact = settings.LANGUAGE_CODE.lower()
    system_language_fuzzy = settings.LANGUAGE_CODE.split("-")[0].lower()

    if label_language_exact == user_language_exact:
        rank *= 10
    elif label_language_fuzzy == user_language_fuzzy:
        rank *= 5
    elif label_language_exact == system_language_exact:
        rank *= 3
    elif label_language_fuzzy == system_language_fuzzy:
        rank *= 2

    return rank


def capitalize_region(code):
    """Normalize a code such as en-us to en-US."""
    lang_parts = code.lower().replace("_", "-").split("-")
    try:
        lang_parts[1] = lang_parts[1].upper()
    except:
        pass
    return "-".join(lang_parts)


class ArchesPOFileFetcher:
    """Gets PO files for processing"""

    def get_po_file(self, lang, overwrite=False) -> polib.POFile:
        """Gets a graph PO file for a specific language"""
        path = settings.LOCALE_PATHS[0]
        po_path = os.path.join(path, lang, "LC_MESSAGES")
        pathlib.Path(po_path).mkdir(parents=True, exist_ok=True)
        pofilepath = os.path.join(po_path, "graphs.po")
        if overwrite or not os.path.exists(pofilepath):
            open(pofilepath, "w").close()
            return self.setup_file(polib.pofile(pofilepath))

        for pofilepath in glob.glob(os.path.join(po_path, "graphs.po")):
            return self.setup_file(polib.pofile(pofilepath))

    def get_po_files(self, lang=None, overwrite=False) -> List[ArchesPOFile]:
        """Get an array of PO files being loaded or written"""
        files = []

        if lang:
            files.append(ArchesPOFile(lang, self.get_po_file(lang, overwrite)))
        else:
            for language in settings.LANGUAGES:
                files.append(
                    ArchesPOFile(language[0], self.get_po_file(language[0], overwrite))
                )
        return files

    def setup_file(self, pofile: polib.POFile) -> polib.POFile:
        """Given a PO file, set up metadata and duplicate check property"""
        current_time = datetime.now()
        pofile.check_for_duplicates = True
        pofile.metadata = {
            "Project-Id-Version": "1.0",
            "Report-Msgid-Bugs-To": "dev@fargeo.com",
            "POT-Creation-Date": current_time.strftime("%Y-%m-%d %H:%M:%S%z"),
            "PO-Revision-Date": current_time.strftime("%Y-%m-%d %H:%M:%S%z"),
            "MIME-Version": "1.0",
            "Content-Type": "text/plain; charset=utf-8",
            "Content-Transfer-Encoding": "8bit",
        }

        return pofile


class ArchesPOWriter:
    """Writes a PO file from arches graph tables"""

    def __init__(
        self, pofile: polib.POFile, id_language: str, target_language: str
    ) -> None:
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
            self.append(row.label, "cards_x_nodes_x_widgets")
            try:
                i18n_properties = row.config["i18n_properties"]
                for prop in i18n_properties:
                    try:
                        self.append(row.config[prop], "cards_x_nodes_x_widgets")
                    except KeyError:
                        pass
            except KeyError:
                pass

    def populate_from_cards(self, queryset):
        for row in queryset:
            try:
                self.append(row.name, "cards")
                self.append(row.description, "cards")
                self.append(row.instructions, "cards")
                self.append(row.helptitle, "cards")
                self.append(row.helptext, "cards")
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

        if self.target_language != self.id_language:
            try:
                msgstr = cell[self.target_language]
            except KeyError:
                msgstr = ""
        else:
            msgstr = ""

        if msgid is not None and msgid != "":
            entry = polib.POEntry(msgid=msgid, msgstr=msgstr, occurrences=occurrences)
            try:
                self.pofile.append(entry)

            # happens when there are duplicates, no need to do anything with it
            except ValueError:
                pass


class ArchesPOLoader:
    """Loads a PO file into arches graph tables"""

    def __init__(
        self, pofile: polib.POFile, id_language: str, target_language: str
    ) -> None:
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
            self.update_i18n_string_cell(row.label)
            row.save()
            try:
                i18n_properties = row.config["i18n_properties"]
                for prop in i18n_properties:
                    entry = self.pofile.find(row.config[prop][self.id_language])
                    if entry is not None and entry.msgstr != "":
                        row.config[prop][self.target_language] = entry.msgstr
                    else:
                        row.config[prop].pop(self.target_language, None)

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
            if entry is not None and entry.msgstr != "":
                cell[self.target_language] = entry.msgstr
            else:
                cell.pop(self.target_language, None)
        except KeyError:
            pass


class LanguageSynchronizer:
    def synchronize_settings_with_db(update_published_graphs=True):
        from arches.app.models.graph import Graph  # avoids circular import

        if settings.LANGUAGES:
            for lang in settings.LANGUAGES:
                found_language = Language.objects.filter(code=lang[0]).first()

                # no need to add the language if it already exists
                if found_language:
                    continue

                language_info = get_language_info(lang[0])
                Language.objects.create(
                    code=lang[0],
                    name=language_info["name"],
                    default_direction="rtl" if language_info["bidi"] else "ltr",
                    scope="system",
                    isdefault=False,
                )

            if update_published_graphs:
                for graph in Graph.objects.all():
                    if graph.publication_id:
                        graph.update_published_graphs()
