import json

from arches.app.models.models import DDataType
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models.fields.i18n import I18n_String, I18n_TextField, I18n_JSON, I18n_JSONField
from tests.base_test import ArchesTestCase
from django.contrib.gis.db import models
from django.utils import translation
from django.db import connection

# these tests can be run from the command line via
# python manage.py test tests.localization.field_tests --settings="tests.test_settings"


class Customi18nTextFieldTests(ArchesTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

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

    @classmethod
    def tearDownClass(cls):
        cursor = connection.cursor()
        cursor.execute("DROP TABLE public._localization_test_model")
        super().tearDownClass()

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
        self.assertEqual(str(m.name), "")
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
        self.assertEqual(str(m.name), "")
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

    def test_quoted_string_i18n_text_field_data_consistency_before_and_after_save(self):
        # re https://github.com/archesproject/arches/issues/9623
        translation.activate("en")
        m = self.LocalizationTestModel()
        m.name = "\"Hello World\""
        m.id = 11
        self.assertEqual(str(m.name),"\"Hello World\"")
        m.save()

        # test that post save everything is the same
        self.assertEqual(str(m.name), "\"Hello World\"")

        # test that the object retrieved from the database is the same
        m = self.LocalizationTestModel.objects.get(pk=11)
        self.assertEqual(str(m.name), "\"Hello World\"")
        self.assertEqual(m.name.raw_value, {"en": "\"Hello World\""})

    def test_equality(self):
        value = I18n_String("toast")
        self.assertEqual(value, "toast")

        value = I18n_String('{"de": "genau", "en": "precisely"}')
        translation.activate("en")
        self.assertEqual(value, "precisely")
        translation.activate("de")
        self.assertEqual(value, "genau")


class Customi18nJSONFieldTests(ArchesTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        sql = """
        CREATE TABLE public._localization_test_json_model
        (
            config jsonb,
            id integer,
            PRIMARY KEY (id)
        );

        ALTER TABLE public._localization_test_json_model
            OWNER to postgres;
        """

        cursor = connection.cursor()
        cursor.execute(sql)

    @classmethod
    def tearDownClass(cls):
        cursor = connection.cursor()
        cursor.execute("DROP TABLE public._localization_test_json_model")
        super().tearDownClass()

    class LocalizationTestJsonModel(models.Model):
        config = I18n_JSONField(null=False)
        id = models.IntegerField(primary_key=True)

        class Meta:
            app_label = "_test"
            managed = True
            db_table = "_localization_test_json_model"

    def test_i18n_json_class(self):
        test_json = json.dumps(
            {"i18n_properties": ["placeholder"], "placeholder": {"en": "choose one", "es": "elija uno"}, "min_length": 19}
        )
        expected_output = json.dumps({"i18n_properties": ["placeholder"], "placeholder": "choose one", "min_length": 19})
        translation.activate("en")
        j = I18n_JSON(test_json)
        self.assertEqual(str(j), expected_output)

    def test_i18n_json_field(self):
        test_json = {"i18n_properties": ["placeholder"], "placeholder": {"en": "choose an option", "es": "elija uno"}, "min_length": 19}

        translation.activate("en")
        m = self.LocalizationTestJsonModel()
        m.id = 1
        m.config = test_json
        m.save()
        m = self.LocalizationTestJsonModel.objects.get(pk=1)
        self.assertEqual(m.config.raw_value, test_json)

        updated_input = json.dumps({"i18n_properties": ["placeholder"], "placeholder": "choose one", "min_length": 19})
        m.config = updated_input
        m.save()

        expected_output = {"i18n_properties": ["placeholder"], "placeholder": {"en": "choose one", "es": "elija uno"}, "min_length": 19}
        m = self.LocalizationTestJsonModel.objects.get(pk=1)
        self.assertEqual(m.config.raw_value, expected_output)

    def test_i18n_json_field_multiple(self):
        test_json = {
            "i18n_properties": ["trueLabel", "falseLabel"],
            "trueLabel": {"en": "true", "es": "verdad"},
            "falseLabel": {"en": "false", "es": "falso"},
            "min_length": 19,
        }

        translation.activate("es")
        m = self.LocalizationTestJsonModel()
        m.id = 2
        m.config = test_json
        m.save()
        m = self.LocalizationTestJsonModel.objects.get(pk=2)
        self.assertEqual(m.config.raw_value, test_json)

        self.assertEqual(json.loads(str(m.config))["trueLabel"], "verdad")
        self.assertEqual(json.loads(str(m.config))["falseLabel"], "falso")
        self.assertEqual(json.loads(str(m.config))["min_length"], 19)
        self.assertEqual(json.loads(str(m.config))["i18n_properties"], ["trueLabel", "falseLabel"])

        translation.activate("de")
        updated_input = json.dumps(
            {"i18n_properties": ["trueLabel", "falseLabel"], "trueLabel": "wahr", "falseLabel": "falsch", "min_length": 45}
        )
        m.config = updated_input
        m.save()

        expected_output = {
            "i18n_properties": ["trueLabel", "falseLabel"],
            "trueLabel": {"en": "true", "es": "verdad", "de": "wahr"},
            "falseLabel": {"en": "false", "es": "falso", "de": "falsch"},
            "min_length": 45,
        }
        m = self.LocalizationTestJsonModel.objects.get(pk=2)
        self.assertEqual(m.config.raw_value, expected_output)

    def test_i18n_json_class_as_dict(self):
        test_json = {"i18n_properties": ["placeholder"], "placeholder": {"en": "choose one", "es": "elija uno"}, "min_length": 19}
        translation.activate("en")
        j = I18n_JSON(test_json)

        self.assertEqual(j["min_length"], test_json["min_length"])
        self.assertTrue("min_length" in j)
        self.assertEqual(j.get("min_length"), 19)
        self.assertEqual(list(j.keys()), ["i18n_properties", "placeholder", "min_length"])
        self.assertEqual(j.pop("min_length"), 19)
        self.assertEqual(list(j.keys()), ["i18n_properties", "placeholder"])

        # test item assignment
        j["new_property"] = "TACO"
        self.assertEqual(list(j.keys()), ["i18n_properties", "placeholder", "new_property"])

    def test_i18nJSONField_can_handle_different_initial_states(self):
        initial_json = {
            "trueLabel": None,
            "falseLabel": {},
            "altLabel": "",
            "min_length": 19,
        }

        json_to_save = {
            "i18n_properties": ["trueLabel", "falseLabel", "altLabel"],
            "trueLabel": "YES",
            "falseLabel": "NO",
            "altLabel": "taco",
            "min_length": 19,
        }

        expected_output_json = {
            "i18n_properties": ["trueLabel", "falseLabel", "altLabel"],
            "trueLabel": {"en": "YES"},
            "falseLabel": {"en": "NO"},
            "altLabel": {"en": "taco"},
            "min_length": 19,
        }

        translation.activate("en")
        m = self.LocalizationTestJsonModel()
        m.id = 3
        m.config = initial_json
        m.save()
        m = self.LocalizationTestJsonModel.objects.get(pk=3)
        self.assertEqual(m.config.raw_value, initial_json)

        m.config = json_to_save
        m.save()
        m = self.LocalizationTestJsonModel.objects.get(pk=3)
        self.assertEqual(m.config.raw_value, expected_output_json)


class I18nJSONFieldBulkUpdateTests(ArchesTestCase):
    def test_bulk_update_node_config_homogenous_value(self):
        new_config = I18n_JSON({
            "en": "some",
            "zh": "json",
        })
        for_bulk_update = []
        for dt in DDataType.objects.all()[:3]:
            dt.defaultconfig = new_config
            for_bulk_update.append(dt)

        DDataType.objects.bulk_update(for_bulk_update, fields=["defaultconfig"])

        for i, obj in enumerate(for_bulk_update):
            with self.subTest(obj_index=i):
                obj.refresh_from_db()
                self.assertEqual(str(obj.defaultconfig), str(new_config))

    def test_bulk_update_heterogenous_values(self):
        new_configs = [
            I18n_JSON({
                "en": "some",
                "zh": "json",
            }),
            I18n_JSON({}),
            None,
        ]
        for_bulk_update = []
        for i, dt in enumerate(DDataType.objects.all()[:3]):
            dt.defaultconfig = new_configs[i]
            for_bulk_update.append(dt)

        with self.assertRaises(NotImplementedError):
            DDataType.objects.bulk_update(for_bulk_update, fields=["defaultconfig"])

        # If the above starts failing, it's likely the underlying Django
        # regression was fixed.
        # https://code.djangoproject.com/ticket/35167
        
        # In that case, remove the with statement, de-indent the bulk_update,
        # and comment the following code back in:

        # for i, obj in enumerate(for_bulk_update):
        #     new_config_as_string = str(new_configs[i])
        #     with self.subTest(new_config=new_config_as_string):
        #         obj.refresh_from_db()
        #         self.assertEqual(str(obj.defaultconfig), new_config_as_string)

        # Also consider removing the code at the top of I18n_JSON._parse()


class AsSqlTests(ArchesTestCase):
    def test_domain_datatype(self):
        datatype = DataTypeFactory().get_instance("domain-value")
        domain_value = I18n_JSON({"en": "it's a bird"})

        # Apostrophe in "it's" is doubly-escaped so it doesn't close the string
        expected = "jsonb_set(None, array[\'en\'], \'\"it\'\'s a bird\"\')"
        self.assertEqual(datatype.i18n_as_sql(domain_value, None, None), expected)
