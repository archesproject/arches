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

import shutil
import os
from arches.app.models.models import EditLog
from arches.app.models.graph import Graph
from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.utils.data_management.resource_graphs.importer import import_graph as resource_graph_importer
from arches.app.utils.i18n import LanguageSynchronizer
from arches.app.etl_modules.import_single_csv import ImportSingleCsv
from arches.app.models.system_settings import settings
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.db import connection
from django.http import HttpRequest
from django.test import override_settings
from django.test import TransactionTestCase
# these tests can be run from the command line via
# python manage.py test tests.bulkdata.single_csv_tests --settings="tests.test_settings"


class SingleCSVTests(TransactionTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        LanguageSynchronizer.synchronize_settings_with_db()
        with open(os.path.join("tests/fixtures/single_csv_bulk_manager_test_model.json"), "r") as f:
            archesfile = JSONDeserializer().deserialize(f)
        resource_graph_importer(archesfile["graph"])
        graph=Graph.objects.get(graphid="1bc910b3-99dc-4a5c-8168-61c9e1975658")
        admin = User.objects.get(username="admin")
        graph.publish(user=admin)
    

    @override_settings(
        MEDIA_ROOT = os.path.join(settings.ROOT_DIR, "..", "tests/fixtures/data")
    )
    def test_write(self):
        request = HttpRequest()
        request.method = "POST"
        request.user = User.objects.get(username="admin")
        load_id = '2d288e76-ebd3-11ee-85b8-0242ac120005'
        csv_file = 'single-csv-test-data.csv'

        with connection.cursor() as cursor:
            cursor.execute("""INSERT INTO load_event (loadid, complete, etl_module_id, user_id) values (%s, FALSE, '0a0cea7e-b59a-431a-93d8-e9f8c41bdd6b', 1)""", [load_id,])

        request.POST.__setitem__("fieldnames", "name,geometry")
        request.POST.__setitem__("hasHeaders", "true")
        request.POST.__setitem__("csvFileName", csv_file)
        request.POST.__setitem__("graphid", "1bc910b3-99dc-4a5c-8168-61c9e1975658")
        request.POST.__setitem__("load_id", load_id)
        request.POST.__setitem__("fieldMapping", '[{"field":"name","node":"name","language":{"code":"en","default_direction":"ltr","id":1,"isdefault":true,"name":"English","scope":"system"}},{"field":"geom","node":"geometry","language":{"code":"en","default_direction":"ltr","id":1,"isdefault":true,"name":"English","scope":"system"}},{"field":"resourceid","language":{"code":"en","default_direction":"ltr","id":1,"isdefault":true,"name":"English","scope":"system"}}]')

        tmp_path = default_storage.path(os.path.join(settings.UPLOADED_FILES_DIR, 'tmp', load_id))
        csv_file = default_storage.path(os.path.join(settings.UPLOADED_FILES_DIR, csv_file))

        if not os.path.exists(tmp_path):
            os.makedirs(tmp_path)

        shutil.copy(csv_file, tmp_path)
        importer = ImportSingleCsv(request=request, loadid=load_id)
        importer.write(request)
        edits = EditLog.objects.filter(transactionid=load_id)
        self.assertTrue(len(edits)==9)
