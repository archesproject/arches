from arches.app.models.fields.i18n import I18n_TextField
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
        """

        cursor = connection.cursor()
        cursor.execute(sql)


    def test_i18n_text_field(self):
        class LocalizationTestModel(models.Model):
            name = I18n_TextField()
            id = models.IntegerField(primary_key=True)
            
            class Meta: 
                app_label = '_test'
                managed = True
                db_table = "_localization_test_model"

        m = LocalizationTestModel()
        m.id = 1

        translation.activate('en')
        m.name = 'foo'
        m.save()

        translation.activate('de')
        m.name = 'foo-bar'
        m.save()

        # self.assertEqual(str(m.name), 'foo-bar')

        translation.activate('en')
        m = LocalizationTestModel.objects.get(pk=1)
        self.assertEqual(str(m.name), 'foo')

        translation.activate('de')
        m = LocalizationTestModel.objects.get(pk=1)
        self.assertEqual(str(m.name), 'foo-bar')

