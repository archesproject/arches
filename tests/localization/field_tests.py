from arches.app.models.fields.i18n import I18n_String, I18n_TextField
from tests.base_test import ArchesTestCase
from django.contrib.gis.db import models
from django.utils import translation
from django.db import connection

# these tests can be run from the command line via
# python manage.py test tests/localization/field_tests.py --settings="tests.test_settings"


class Customi18nTextFieldTests(ArchesTestCase):
    @classmethod
    def setUpClass(cls):
        sql = """
        CREATE TABLE public._localization_test_model
        (
            name jsonb,
            id integer,
            PRIMARY KEY (id)
        );

        ALTER TABLE public._localization_test_model
            OWNER to postgres;

        CREATE TABLE public._localization_test_model_w_nulls
        (
            name jsonb,
            id integer,
            PRIMARY KEY (id)
        );

        ALTER TABLE public._localization_test_model
            OWNER to postgres;
        """

        cursor = connection.cursor()
        cursor.execute(sql)

    class LocalizationTestModel(models.Model):
        name = I18n_TextField(null=False)
        id = models.IntegerField(primary_key=True)

        class Meta:
            app_label = "_test"
            managed = True
            db_table = "_localization_test_model"

    class LocalizationTestModelWNulls(models.Model):
        name = I18n_TextField(null=True)
        id = models.IntegerField(primary_key=True)

        class Meta:
            app_label = "_test"
            managed = True
            db_table = "_localization_test_model_w_nulls"

    def test_i18n_text_field(self):
        m = self.LocalizationTestModel()
        m.id = 1

        translation.activate("en")
        m.name = "boat"
        m.save()

        translation.activate("es")
        m.name = "barco"
        m.save()

        # test that we can save a single localized value
        translation.activate("en")
        m = self.LocalizationTestModel.objects.get(pk=1)
        self.assertEqual(str(m.name), "boat")

        # test that we can save a different localized value to the same object
        translation.activate("es")
        m = self.LocalizationTestModel.objects.get(pk=1)
        self.assertEqual(str(m.name), "barco")

        # test that we can access the raw value with all languages
        self.assertEqual(m.name.raw_value, {"en": "boat", "es": "barco"})

        # test that we can update just a single language
        translation.activate("en")
        m.name = "ship"
        m.save()
        m = self.LocalizationTestModel.objects.get(pk=1)
        self.assertEqual(str(m.name), "ship")
        self.assertEqual(m.name.raw_value, {"en": "ship", "es": "barco"})

    def test_i18n_text_field_w_blank_strings(self):
        translation.activate("en")
        m = self.LocalizationTestModel()
        m.id = 2
        m.save()
        self.assertEqual(str(m.name), "")
        self.assertEqual(m.name.raw_value, {"en": ""})

    def test_i18n_text_field_w_nulls(self):
        translation.activate("en")
        m = self.LocalizationTestModelWNulls()
        m.id = 3
        m.save()
        self.assertEqual(str(m.name), "null")
        self.assertEqual(m.name.raw_value, {"en": None})

    def test_i18n_text_field_return_default_language(self):
        # test that if the language code requested doesn't exist then return the defualt language instead
        translation.activate("en")
        m = self.LocalizationTestModel()
        m.id = 4
        m.name = "one"
        m.save()

        translation.activate("de")
        m = self.LocalizationTestModel.objects.get(pk=4)
        self.assertEqual(str(m.name), "one")

    def test_init_i18n_text_field_w_dict(self):
        m = self.LocalizationTestModel()
        m.id = 5
        m.name = {"en": "one", "es": "uno"}
        m.save()

        translation.activate("es")
        m = self.LocalizationTestModel.objects.get(pk=5)
        self.assertEqual(str(m.name), "uno")

    def test_init_i18n_text_field_w_json(self):
        m = self.LocalizationTestModel.objects.create(id=6, name='{"en": "one", "es": "uno"}')
        m.save()

        translation.activate("es")
        m = self.LocalizationTestModel.objects.get(pk=6)
        self.assertEqual(str(m.name), "uno")

    def test_init_i18n_text_field_w_i18n_string(self):
        m = self.LocalizationTestModel()
        m.name = I18n_String(value='{"en": "one", "es": "uno"}')
        m.id = 7
        m.save()

        translation.activate("es")
        m = self.LocalizationTestModel.objects.get(pk=7)
        self.assertEqual(str(m.name), "uno")

    def test_init_i18n_text_field_w_i18n_string_dict(self):
        m = self.LocalizationTestModel()
        m.name = I18n_String(value={"en": "one", "es": "uno"})
        m.id = 8
        m.save()

        translation.activate("es")
        m = self.LocalizationTestModel.objects.get(pk=8)
        self.assertEqual(str(m.name), "uno")

    def test_init_i18n_text_field_w_null_update(self):
        m = self.LocalizationTestModelWNulls()
        m.name = I18n_String(value={"en": "one", "es": "uno"})
        m.id = 9
        m.save()

        translation.activate("es")
        m.name = None
        m.save()
        m = self.LocalizationTestModelWNulls.objects.get(pk=9)
        self.assertEqual(str(m.name), "null")
        self.assertEqual(m.name.raw_value, {"en": "one", "es": None})

    def test_i18n_text_field_data_consistency_before_and_after_save(self):
        translation.activate("en")
        m = self.LocalizationTestModel()
        m.name = "Marco"
        m.id = 10
        self.assertEqual(str(m.name), "Marco")
        m.save()

        # test that post save everything is the same
        self.assertEqual(str(m.name), "Marco")

        # test that the object retrieved from the database is the same
        m = self.LocalizationTestModel.objects.get(pk=10)
        self.assertEqual(str(m.name), "Marco")
        self.assertEqual(m.name.raw_value, {"en": "Marco"})

    def test_equality(self):
        value = I18n_String("toast")
        self.assertEqual(value, "toast")

        value = I18n_String('{"de": "genau", "en": "precisely"}')
        translation.activate("de")
        self.assertEqual(value, "genau")
        translation.activate("en")
        self.assertEqual(value, "precisely")