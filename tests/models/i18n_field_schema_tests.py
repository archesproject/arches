import json

from django.db import connection
from django.test import TestCase

from arches.app.models.fields.i18n import I18n_JSONField, I18n_TextField


class I18nFieldAddFieldTests(TestCase):
    """AddField must work on an existing table; the schema editor binds the default."""

    table = "i18n_addfield_test"

    def setUp(self):
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE TABLE {self.table} (id serial PRIMARY KEY)")
            cursor.execute(f"INSERT INTO {self.table} DEFAULT VALUES")

    def tearDown(self):
        with connection.cursor() as cursor:
            cursor.execute(f"DROP TABLE IF EXISTS {self.table}")

    def _add(self, field):
        from django.db import models

        class Meta:
            app_label = "models"
            db_table = self.table

        model = type(
            "I18nAddFieldTest", (models.Model,), {"__module__": __name__, "Meta": Meta}
        )
        field.set_attributes_from_name("name")
        with connection.schema_editor() as editor:
            editor.add_field(model, field)
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT name FROM {self.table}")
            return cursor.fetchall()

    def test_add_i18n_textfield(self):
        rows = self._add(I18n_TextField(blank=True, null=True))
        self.assertEqual(len(rows), 1)
        self.assertIsInstance(json.loads(rows[0][0]), dict)

    def test_add_non_null_i18n_textfield_writes_default(self):
        rows = self._add(I18n_TextField(blank=True, null=False))
        stored = json.loads(rows[0][0])
        self.assertEqual(len(stored), 1)
        self.assertEqual(list(stored.values()), [""])

    def test_add_i18n_jsonfield_with_default(self):
        rows = self._add(I18n_JSONField(default=dict, null=True))
        self.assertEqual(json.loads(rows[0][0]), {})
