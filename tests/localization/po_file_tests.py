import builtins
import pathlib
from unittest.case import TestCase

import polib
import importlib
from arches.app.models.fields.i18n import I18n_String, I18n_JSON
from arches.app.models.models import CardModel, CardXNodeXWidget
from arches.app.utils.i18n import ArchesPOFileFetcher, ArchesPOLoader, ArchesPOWriter
from arches.app.models.system_settings import settings
from unittest.mock import Mock, MagicMock

# these tests can be run from the command line via
# python manage.py test tests.localization.po_file_tests --settings="tests.test_settings"


class PoFileTests(TestCase):
    def setUp(self):
        self.cardxnodexwidget_all = CardXNodeXWidget.objects.all
        self.cardmodel_all = CardModel.objects.all
        self.open = builtins.open
        self.mkdir = pathlib.Path.mkdir
        self.pofactory = polib.pofile
        self.languages = settings.LANGUAGES

    def tearDown(self):
        CardXNodeXWidget.objects.all = self.cardxnodexwidget_all
        CardModel.objects.all = CardModel.objects.all
        builtins.open = self.open
        pathlib.Path.mkdir = self.mkdir
        polib.pofile = self.pofactory
        settings.LANGUAGES = self.languages

    def test_populate(self):
        m_po_file = Mock(polib.POFile)
        m_all_method = Mock()
        m_all_method.return_value = []
        writer = ArchesPOWriter(m_po_file, "en", "en")
        CardXNodeXWidget.objects.all = m_all_method
        CardModel.objects.all = m_all_method
        writer.populate()
        self.assertEqual(m_all_method.call_count, 2)

    def test_populate_from_card_x_node_x_widget(self):
        "Test to ensure PO Entries are appended with appropriate english messageids (no translations)"
        m_po_file = Mock(polib.POFile)
        writer = ArchesPOWriter(m_po_file, "en", "en")
        model = MagicMock(CardXNodeXWidget)
        prop_dict = {"en": "configuration"}
        config_dict = {"i18n_properties": ["prop", "bob", "fred"], "prop": prop_dict, "fred": prop_dict, "label": prop_dict}
        model.config.__getitem__.side_effect = config_dict.__getitem__
        model.config.prop.__getitem__.side_effect = prop_dict.__getitem__
        label_dict = {"en": "label"}
        model.label.__getitem__.side_effect = label_dict.__getitem__
        writer.populate_from_card_x_node_x_widget([model])
        self.assertEqual(m_po_file.append.call_count, 3)

    def test_missing_i18n_properties(self):
        "Test to ensure PO Entries are appended with appropriate english messageids (no translations)"
        m_po_file = Mock(polib.POFile)
        writer = ArchesPOWriter(m_po_file, "en", "en")
        model = MagicMock(CardXNodeXWidget)
        prop_dict = {"en": "configuration"}
        config_dict = {"label": prop_dict}
        model.config.__getitem__.side_effect = config_dict.__getitem__
        model.config.prop.__getitem__.side_effect = prop_dict.__getitem__
        label_dict = {"en": "label"}
        model.label.__getitem__.side_effect = label_dict.__getitem__
        writer.populate_from_card_x_node_x_widget([model])
        self.assertEqual(m_po_file.append.call_count, 1)

    def test_populate_from_cards(self):
        "Test to ensure PO Entries are appended with appropriate english messageids (no translations)"
        m_po_file = Mock(polib.POFile)
        writer = ArchesPOWriter(m_po_file, "en", "en")
        model = MagicMock(CardModel)
        name_dict = {"en": "name"}
        description_dict = {"en": "description"}
        instructions_dict = {"en": "instructions"}
        helptitle_dict = {"en": "helptitle"}
        helptext_dict = {"en": "helptext"}
        model.name.__getitem__.side_effect = name_dict.__getitem__
        model.description.__getitem__.side_effect = description_dict.__getitem__
        model.instructions.__getitem__.side_effect = instructions_dict.__getitem__
        model.helptitle.__getitem__.side_effect = helptitle_dict.__getitem__
        model.helptext.__getitem__.side_effect = helptext_dict.__getitem__
        writer.populate_from_cards([model])
        self.assertEqual(m_po_file.append.call_count, 5)
        self.assertEqual(m_po_file.append.call_args_list[0][0][0].msgid, "name")
        self.assertEqual(m_po_file.append.call_args_list[0][0][0].msgstr, "")
        self.assertEqual(m_po_file.append.call_args_list[4][0][0].msgid, "helptext")
        self.assertEqual(m_po_file.append.call_args_list[4][0][0].msgstr, "")

    def test_populate_from_cards_spanish(self):
        "Test to ensure PO Entries are appended with appropriate spanish translations"
        m_po_file = Mock(polib.POFile)
        writer = ArchesPOWriter(m_po_file, "en", "es")
        model = MagicMock(CardModel)
        name_dict = {"en": "name", "es": "nombre"}
        description_dict = {"en": "description", "es": "descripción"}
        instructions_dict = {"en": "instructions", "es": "instrucciones"}
        helptitle_dict = {"en": "helptitle", "es": "texto de ayuda"}
        helptext_dict = {"en": "helptext", "es": "título de la ayuda"}
        model.name.__getitem__.side_effect = name_dict.__getitem__
        model.name.__contains__.side_effect = name_dict.__contains__
        model.description.__getitem__.side_effect = description_dict.__getitem__
        model.description.__contains__.side_effect = description_dict.__contains__
        model.instructions.__getitem__.side_effect = instructions_dict.__getitem__
        model.instructions.__contains__.side_effect = instructions_dict.__contains__
        model.helptitle.__getitem__.side_effect = helptitle_dict.__getitem__
        model.helptitle.__contains__.side_effect = helptitle_dict.__contains__
        model.helptext.__getitem__.side_effect = helptext_dict.__getitem__
        model.helptext.__contains__.side_effect = helptext_dict.__contains__
        writer.populate_from_cards([model])
        self.assertEqual(m_po_file.append.call_count, 5)
        self.assertEqual(m_po_file.append.call_args_list[0][0][0].msgid, "name")
        self.assertEqual(m_po_file.append.call_args_list[0][0][0].msgstr, "nombre")
        self.assertEqual(m_po_file.append.call_args_list[4][0][0].msgid, "helptext")
        self.assertEqual(m_po_file.append.call_args_list[4][0][0].msgstr, "título de la ayuda")

    def test_po_write_duplicate_exception_caught(self):
        def throw_value_error(val):
            raise ValueError()

        m_po_file = MagicMock(polib.POFile)
        m_po_file.append.side_effect = throw_value_error
        model = MagicMock(CardXNodeXWidget)
        prop_dict = {"en": "configuration"}
        config_dict = {"i18n_properties": ["prop"], "prop": prop_dict}
        model.config.__getitem__.side_effect = config_dict.__getitem__
        model.config.prop.__getitem__.side_effect = prop_dict.__getitem__
        label_dict = {"en": "label"}
        model.label.__getitem__.side_effect = label_dict.__getitem__
        writer = ArchesPOWriter(m_po_file, "en", "es")
        writer.populate_from_card_x_node_x_widget([model])

    def test_arches_po_loader(self):
        """happy path test of arches po loader"""
        m_po_file = MagicMock(polib.POFile)

        m_all_method_cardxnodexwidgets = Mock()
        m_cardxnodexwidget = MagicMock(CardXNodeXWidget)
        i18n_json_dict = {"i18n_properties": ["test", "test2"], "test": {"en": "test"}, "test2": {"en": "test2"}}
        m_i18n_json_field = MagicMock(I18n_JSON)
        m_i18n_json_field.__getitem__ = Mock()
        m_i18n_json_field.__getitem__.side_effect = i18n_json_dict.__getitem__
        m_cardxnodexwidget.config = m_i18n_json_field
        m_cardxnodexwidget.save.return_value = None
        m_all_method_cardxnodexwidgets.return_value = [m_cardxnodexwidget]
        CardXNodeXWidget.objects.all = m_all_method_cardxnodexwidgets

        m_all_method_cardmodel = Mock()
        m_card = MagicMock(CardModel)
        m_card.save.return_value = None
        m_all_method_cardmodel.return_value = [m_card]
        CardModel.objects.all = m_all_method_cardmodel

        loader = ArchesPOLoader(m_po_file, "en", "es")
        loader.load()

        m_card.save.assert_called()
        m_cardxnodexwidget.save.assert_called()

    def test_malformed_i18n_properties(self):
        """missing i18n_properties"""
        m_po_file = MagicMock(polib.POFile)

        m_all_method_cardxnodexwidgets = Mock()
        m_cardxnodexwidget = MagicMock(CardXNodeXWidget)
        i18n_json_dict = {"i18n_properties": ["test", "test2"], "test": {"en": "test"}}
        m_i18n_json_field = MagicMock(I18n_JSON)
        m_i18n_json_field.__getitem__ = Mock()
        m_i18n_json_field.__getitem__.side_effect = i18n_json_dict.__getitem__
        m_cardxnodexwidget.config = m_i18n_json_field
        m_cardxnodexwidget.save.return_value = None
        m_all_method_cardxnodexwidgets.return_value = [m_cardxnodexwidget]
        CardXNodeXWidget.objects.all = m_all_method_cardxnodexwidgets

        m_all_method_cardmodel = Mock()
        m_card = MagicMock(CardModel)
        m_card.save.return_value = None
        m_all_method_cardmodel.return_value = [m_card]
        CardModel.objects.all = m_all_method_cardmodel

        loader = ArchesPOLoader(m_po_file, "en", "es")
        loader.load()

        m_card.save.assert_called()
        m_cardxnodexwidget.save.assert_called()

    def test_po_loader_no_i18n_properties(self):
        """Tests removing entries from the database when PO entry is empty string"""
        m_po_entry = MagicMock(polib.POEntry)
        m_po_entry.msgid = "doom"
        m_po_entry.msgstr = ""
        m_po_file = MagicMock(polib.POFile)
        m_po_file.find.return_value = m_po_entry

        m_all_method_cardmodel = Mock()
        m_card = MagicMock(CardModel)
        m_card.save.return_value = None
        m_i18n_string = MagicMock(I18n_String)
        m_card.name = m_i18n_string
        i18n_string_dict = {"en": "doom", "es": ""}
        m_i18n_string.__getitem__.side_effect = i18n_string_dict.__getitem__
        m_i18n_string.pop = Mock()
        m_all_method_cardmodel.return_value = [m_card]

        m_all_method_cardxnodexwidgets = Mock()
        m_cardxnodexwidget = MagicMock(CardXNodeXWidget)
        i18n_json_dict = {"test": {"en": "test"}, "label": "doom"}
        m_i18n_json_field = MagicMock(I18n_JSON)
        m_i18n_json_field.__getitem__ = Mock()
        m_i18n_json_field.__getitem__.side_effect = i18n_json_dict.__getitem__
        m_cardxnodexwidget.config = m_i18n_json_field
        m_cardxnodexwidget.save.return_value = None
        m_all_method_cardxnodexwidgets.return_value = [m_cardxnodexwidget]
        CardXNodeXWidget.objects.all = m_all_method_cardxnodexwidgets

        loader = ArchesPOLoader(m_po_file, "en", "es")
        CardXNodeXWidget.objects.all = m_all_method_cardxnodexwidgets
        CardModel.objects.all = m_all_method_cardmodel
        loader.load()

        m_card.save.assert_called()
        m_cardxnodexwidget.save.assert_called()
        self.assertEqual(m_i18n_string.pop.call_count, 1)

    def test_arches_po_loader_removal(self):
        """Tests removing entries from the database when PO entry is empty string"""
        m_po_entry = MagicMock(polib.POEntry)
        m_po_entry.msgid = "doom"
        m_po_entry.msgstr = ""
        m_po_file = MagicMock(polib.POFile)
        m_po_file.find.return_value = m_po_entry

        m_all_method_cardmodel = Mock()
        m_card = MagicMock(CardModel)
        m_card.save.return_value = None
        m_i18n_string = MagicMock(I18n_String)
        m_card.name = m_i18n_string
        i18n_string_dict = {"en": "doom", "es": ""}
        m_i18n_string.__getitem__.side_effect = i18n_string_dict.__getitem__
        m_i18n_string.pop = Mock()
        m_all_method_cardmodel.return_value = [m_card]

        m_all_method_cardxnodexwidgets = Mock()
        m_cardxnodexwidget = MagicMock(CardXNodeXWidget)
        i18n_json_dict = {"i18n_properties": ["test", "test2"], "test": {"en": "test"}}
        m_i18n_json_field = MagicMock(I18n_JSON)
        m_i18n_json_field.__getitem__ = Mock()
        m_i18n_json_field.__getitem__.side_effect = i18n_json_dict.__getitem__
        m_cardxnodexwidget.config = m_i18n_json_field
        m_cardxnodexwidget.save.return_value = None
        m_all_method_cardxnodexwidgets.return_value = [m_cardxnodexwidget]
        CardXNodeXWidget.objects.all = m_all_method_cardxnodexwidgets

        loader = ArchesPOLoader(m_po_file, "en", "es")
        CardXNodeXWidget.objects.all = m_all_method_cardxnodexwidgets
        CardModel.objects.all = m_all_method_cardmodel
        loader.load()

        m_card.save.assert_called()
        m_cardxnodexwidget.save.assert_called()
        self.assertEqual(m_i18n_string.pop.call_count, 1)

        i18n_json_dict["test2"] = m_i18n_string
        loader.load()
        self.assertEqual(m_i18n_string.pop.call_count, 3)

        # test that a msgid key won't blow up the whole import
        loader = ArchesPOLoader(m_po_file, "ar", "es")
        CardXNodeXWidget.objects.all = m_all_method_cardxnodexwidgets
        CardModel.objects.all = m_all_method_cardmodel
        loader.load()

    def test_arches_po_loader_no_load_same_language(self):
        """Tests attempting to load same language - do not"""
        m_po_entry = MagicMock(polib.POEntry)
        m_po_entry.msgid = "doom"
        m_po_entry.msgstr = ""
        m_po_file = MagicMock(polib.POFile)
        m_po_file.find.return_value = m_po_entry

        m_all_method_cardmodel = Mock()
        m_card = MagicMock(CardModel)
        m_card.save.return_value = None
        m_all_method_cardmodel.return_value = [m_card]

        m_all_method_cardxnodexwidgets = Mock()
        m_cardxnodexwidget = MagicMock(CardXNodeXWidget)
        m_cardxnodexwidget.save.return_value = None
        m_all_method_cardxnodexwidgets.return_value = [m_cardxnodexwidget]

        loader = ArchesPOLoader(m_po_file, "en", "en")
        CardXNodeXWidget.objects.all = m_all_method_cardxnodexwidgets
        CardModel.objects.all = m_all_method_cardmodel
        loader.load()

        m_card.save.assert_not_called()
        m_cardxnodexwidget.save.assert_not_called()

    def test_get_all_po_files(self):
        fetcher = ArchesPOFileFetcher()
        m_mkdir = MagicMock()
        pathlib.Path.mkdir = m_mkdir
        settings.LANGUAGES = [
            ("de", ("German")),
            ("en", ("English")),
            ("en-gb", ("British English")),
            ("es", ("Spanish")),
            ("ar", ("Arabic")),
        ]
        m_pofile = MagicMock(polib.POFile)
        m_pofactory = MagicMock()
        m_pofactory.return_value = m_pofile

        builtins.open = MagicMock()
        polib.pofile = m_pofactory
        files = fetcher.get_po_files(None, True)

        m_pofactory.assert_called()
        m_mkdir.assert_called()
        self.assertEqual(len(settings.LANGUAGES), len(files))
