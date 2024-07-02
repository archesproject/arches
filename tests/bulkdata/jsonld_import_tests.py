import io
import os
import shutil
import textwrap
import uuid
from pathlib import Path

from arches.app.etl_modules.jsonld_importer import JSONLDImporter
from arches.app.models.models import (
    EditLog,
    ETLModule,
    GraphModel,
    LoadEvent,
    Node,
    ResourceInstance,
    TileModel,
)
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.utils.data_management.resource_graphs.importer import (
    import_graph as ResourceGraphImporter,
)
from arches.app.utils.i18n import LanguageSynchronizer
from arches.app.utils.skos import SKOSReader
from tests.base_test import ArchesTestCase

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.http import HttpRequest
from django.urls import reverse
from django.test import TransactionTestCase
from django.test.client import Client

# these tests can be run from the command line via
# python manage.py test tests.bulkdata.jsonld_import_tests --settings="tests.test_settings"


class JSONLDImportTests(TransactionTestCase):
    """
    Subclass TransactionTestCase because
    the functionality under test in the etl modules uses a raw cursor to
    disable triggers in the tiles table, which blows up using TestCase.
    (Cannot simply ALTER TABLE during a transaction...)
    """

    serialized_rollback = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ArchesTestCase.loadOntology()
        LanguageSynchronizer.synchronize_settings_with_db()

        skos = SKOSReader()
        rdf = skos.read_file("tests/fixtures/jsonld_base/rdm/jsonld_test_thesaurus.xml")
        skos.save_concepts_from_skos(rdf)

        skos = SKOSReader()
        rdf = skos.read_file(
            "tests/fixtures/jsonld_base/rdm/jsonld_test_collections.xml"
        )
        skos.save_concepts_from_skos(rdf)

        with open(
            os.path.join("tests/fixtures/jsonld_base/models/test_1_basic_object.json"),
            "r",
        ) as f:
            archesfile = JSONDeserializer().deserialize(f)
        ResourceGraphImporter(archesfile["graph"])

        cls.basic_graph = GraphModel.objects.get(slug="basic")
        cls.basic_resource_1 = ResourceInstance.objects.create(
            pk=uuid.UUID("58da1c67-187e-460e-a94f-6b45f9cbc219"),
            graph=cls.basic_graph,
        )
        cls.note_node = Node.objects.get(pk="cdfc22b2-f6b5-11e9-8f09-a4d18cec433a")
        tile = TileModel(
            nodegroup=cls.note_node.nodegroup,
            data={
                str(cls.note_node.pk): {
                    "en": {
                        "direction": "ltr",
                        "value": "Test value",
                    },
                },
            },
        )
        cls.basic_resource_1.tilemodel_set.add(tile, bulk=False)
        cls.basic_resource_1_as_jsonld_bytes = (
            Client().get(reverse("resources", args=[cls.basic_resource_1.pk])).content
        )

        cls.write_zip_file_to_uploaded_files()

    @classmethod
    def write_zip_file_to_uploaded_files(cls):
        basic_resource_1_dest = (
            Path(settings.UPLOADED_FILES_DIR)
            / "testzip"
            / "basic"
            / "58"
            / f"{cls.basic_resource_1.pk}.json"
        )
        default_storage.save(
            basic_resource_1_dest, io.BytesIO(cls.basic_resource_1_as_jsonld_bytes)
        )
        cls.dir_to_zip = (
            Path(default_storage.location)
            / default_storage.location
            / Path(settings.UPLOADED_FILES_DIR)
            / "testzip"
        )
        zip_dest = Path(cls.dir_to_zip.parent) / "test-jsonld-import"
        cls.addClassCleanup(shutil.rmtree, cls.dir_to_zip)
        cls.uploaded_zip_location = shutil.make_archive(zip_dest, "zip", cls.dir_to_zip)
        cls.addClassCleanup(os.unlink, cls.uploaded_zip_location)

    def test_write(self):
        request = HttpRequest()
        request.method = "POST"
        request.user = User.objects.get(username="admin")

        # Mock a load event
        module = ETLModule.objects.get(slug="jsonld-importer")
        start_event = LoadEvent.objects.create(
            user=request.user, etl_module=module, status="running"
        )
        request.POST.__setitem__("load_id", str(start_event.pk))
        request.POST.__setitem__("module", str(module.pk))

        # Mock a read() operation
        request.POST.__setitem__(
            "load_details",
            textwrap.dedent(
                """
            {"result":
                {"summary":
                    {"cumulative_files_size":255,
                        "files":
                            {"testzip/basic/58/58da1c67-187e-460e-a94f-6b45f9cbc219.json":
                                {"size":"255.00 bytes"}
                            },
                        "name":"testzip.zip",
                        "size":"1006.00 bytes"
                    }
                }
            }
            """
            ),
        )
        importer = JSONLDImporter(request=request, loadid=str(start_event.pk))
        importer.prepare_temp_dir(request)  # ordinarily done with the .read() request

        # Do a hack job of a read.
        # This just copies the before-compressed json at uploadedfiles/testzip/basic/58/...
        # to uploadedfiles/tmp/basic/58/...
        shutil.copytree(self.dir_to_zip, default_storage.path(Path(importer.temp_dir)))

        importer.write(request)

        self.assertEqual(
            EditLog.objects.filter(transactionid=start_event.pk).count(), 2
        )
