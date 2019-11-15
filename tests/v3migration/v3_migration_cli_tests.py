import os
import csv
import json
import shutil
from glob import glob
from django.core import management
from arches.app.models.tile import Tile
from arches.app.models.graph import Graph
from arches.app.models.models import ResourceInstance, ResourceXResource
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.data_management.resource_graphs.importer import import_graph
from arches.app.utils.data_management.resources.formats.archesfile import ArchesFileReader
from arches.app.utils.skos import SKOSReader
from arches.app.utils import v3utils
from arches.app.utils.v3migration import v3Importer, v3PreparedResource, DataValueConverter
from tests import test_settings
from tests.base_test import ArchesTestCase


class v3MigrationTests(ArchesTestCase):

    pkg_fixture = os.path.join(test_settings.TEST_ROOT, "fixtures", "v3migration-pkg")
    pkg = os.path.join(test_settings.TEST_ROOT, "v3migration", "pkg")

    @classmethod
    def setUpClass(cls):
        cls.loadOntology()
        management.call_command("packages", operation="import_graphs", source=os.path.join(cls.pkg_fixture, "graphs", "resource_models"))

    @classmethod
    def tearDownClass(cls):
        if os.path.isdir(cls.pkg):
            shutil.rmtree(cls.pkg)

    def load_v4_reference_data(self, dry_run=False):

        v4_thesaurus = os.path.join(self.pkg, "reference_data", "concepts", "thesaurus.xml")
        v4_collections = os.path.join(self.pkg, "reference_data", "collections", "collections.xml")
        for skosfile in [v4_thesaurus, v4_collections]:
            self.assertTrue(os.path.isfile(skosfile))
            if dry_run:
                continue
            skos = SKOSReader()
            rdf = skos.read_file(skosfile)
            ret = skos.save_concepts_from_skos(rdf, "overwrite", "keep")

    def test_v3migration_001_create_v3_data_dir(self):
        """Test the creation of a v3data directory within an existing package."""

        if os.path.isdir(self.pkg):
            shutil.rmtree(self.pkg)

        # make some of the standard v4 package directory structure
        # these are used later, but may as well be created here
        os.mkdir(self.pkg)
        os.mkdir(os.path.join(self.pkg, "reference_data"))

        management.call_command("v3", "start-migration", target=self.pkg, overwrite=True)

        self.assertTrue(os.path.isdir(os.path.join(self.pkg, "v3data", "business_data")))
        self.assertTrue(os.path.isdir(os.path.join(self.pkg, "v3data", "graph_data")))
        self.assertTrue(os.path.isdir(os.path.join(self.pkg, "v3data", "reference_data")))
        self.assertTrue(os.path.isfile(os.path.join(self.pkg, "reference_data", "v3topconcept_lookup.json")))

        # now that its existence is tested, update the topconcept lookup
        # file with the real one, whose contents is expected later
        fixture_lookup = os.path.join(self.pkg_fixture, "reference_data", "v3topconcept_lookup.json")
        shutil.copyfile(fixture_lookup, os.path.join(self.pkg, "reference_data", "v3topconcept_lookup.json"))

    def test_v3migration_002_generate_rm_configs(self):
        """Test the generation of resource model config file."""

        # copy in the resource model files, to mimic a user creating and
        # then exporting them into this package.
        shutil.copytree(os.path.join(self.pkg_fixture, "graphs", "resource_models"), os.path.join(self.pkg, "graphs", "resource_models"))

        # now run the management command
        management.call_command("v3", "generate-rm-configs", target=self.pkg)

        # test that the file has been created, and that it has the correct
        # number of entries to match the number of resource models.
        self.assertTrue(os.path.isfile(os.path.join(self.pkg, "v3data", "rm_configs.json")))
        num_rms = len(glob(os.path.join(self.pkg, "graphs", "resource_models", "*.json")))
        with open(os.path.join(self.pkg, "v3data", "rm_configs.json"), "rb") as conf:
            data = json.loads(conf.read())
            self.assertEqual(num_rms, len(list(data.keys())))

    def test_v3migration_003_generate_lookup_files(self):
        """Test the generation of node lookup files."""

        with open(os.path.join(self.pkg, "v3data", "rm_configs.json"), "rb") as conf:
            data = json.loads(conf.read())

        data["Activity"]["v3_entitytypeid"] = "ACTIVITY.E7"
        data["Actor"]["v3_entitytypeid"] = "ACTOR.E39"
        data["Historic District"]["v3_entitytypeid"] = "HERITAGE_RESOURCE_GROUP.E27"
        data["Historic Event"]["v3_entitytypeid"] = "HISTORICAL_EVENT.E5"
        data["Historic Resource"]["v3_entitytypeid"] = "HERITAGE_RESOURCE.E18"
        data["Information Resource"]["v3_entitytypeid"] = "INFORMATION_RESOURCE.E73"

        with open(os.path.join(self.pkg, "v3data", "rm_configs.json"), "w") as conf:
            json.dump(data, conf, indent=4, sort_keys=True)

        # copy the v3 graph data into the dummy package, then delete the
        # existing node lookups. this mimics a user action of manually adding
        # the CSV files.
        shutil.rmtree(os.path.join(self.pkg, "v3data", "graph_data"))
        shutil.copytree(os.path.join(self.pkg_fixture, "v3data", "graph_data"), os.path.join(self.pkg, "v3data", "graph_data"))
        node_lookups = glob(os.path.join(self.pkg, "v3data", "graph_data", "*_v4_lookup.csv"))
        for f in node_lookups:
            os.remove(f)

        # generate the lookup files. the fact that the are created is tested here,
        # not their content.
        management.call_command("v3", "generate-lookups", target=self.pkg, overwrite=True)

        for f in node_lookups:
            self.assertTrue(os.path.isfile(f))

        # copy the filled out fixture lookup files into the package. This
        # mimics a user manually filling out all of the node name matches
        # between v3 resource graphs and v4 resource models.
        shutil.rmtree(os.path.join(self.pkg, "v3data", "graph_data"))
        shutil.copytree(os.path.join(self.pkg_fixture, "v3data", "graph_data"), os.path.join(self.pkg, "v3data", "graph_data"))

        # run the test-lookups cli command. this tests the command, but NOT
        # the actual configs. that is done in the next section.
        management.call_command("v3", "test-lookups", target=self.pkg)

        # now run the function that is used to test the filled out resource
        # configs. This actually tests the configs.
        errors = v3utils.test_rm_configs(os.path.join(self.pkg, "v3data"))
        self.assertEqual(len(errors), 0)

    def test_v3migration_004_convert_v3_skos(self):
        """Test the conversion of v3 skos data."""

        # copy the v3 skos file from the fixture package to the working
        # package. this mimics the user copy and pasting the v3 export skos
        # into their v3data/reference_data directory.
        shutil.rmtree(os.path.join(self.pkg, "v3data", "reference_data"))
        shutil.copytree(os.path.join(self.pkg_fixture, "v3data", "reference_data"), os.path.join(self.pkg, "v3data", "reference_data"))

        # create anticipated directory locations
        os.mkdir(os.path.join(self.pkg, "reference_data", "concepts"))
        os.mkdir(os.path.join(self.pkg, "reference_data", "collections"))

        # run the conversion command.
        management.call_command("v3", "convert-v3-skos", target=self.pkg)

        # now test that the files exist
        self.load_v4_reference_data(dry_run=True)

    def test_v3migration_005_write_v4_relations_file(self):
        """Test the conversion of the v3 relations file to v4 format."""

        # copy the v3 business data from the fixture package to the working
        # package. this mimics the user copy and pasting the v3 export files
        # into their v3data/business_data directory.
        shutil.rmtree(os.path.join(self.pkg, "v3data", "business_data"))
        shutil.copytree(os.path.join(self.pkg_fixture, "v3data", "business_data"), os.path.join(self.pkg, "v3data", "business_data"))

        # make empty directory to hold business data
        os.mkdir(os.path.join(self.pkg, "business_data"))
        os.mkdir(os.path.join(self.pkg, "business_data", "relations"))

        # run the conversion command.
        management.call_command("v3", "write-v4-relations", target=self.pkg)

        # now test that the new relations file exist, and has the right headers
        v4_relations = os.path.join(self.pkg, "business_data", "relations", "all.relations")
        self.assertTrue(os.path.isfile(v4_relations))
        v4_ct = 0
        with open(v4_relations, "r") as openfile:
            reader = csv.reader(openfile)
            headers = next(reader)
            self.assertEqual(
                headers, ["resourceinstanceidfrom", "resourceinstanceidto", "relationshiptype", "datestarted", "dateended", "notes"]
            )
            for r in reader:
                self.assertEqual(len(r), 6)
                v4_ct += 1

        # get count of v3 relationships for comparison
        v3_ct = 0
        v3_relations = os.path.join(self.pkg, "v3data", "business_data", "v3sample.relations")
        with open(v3_relations, "r") as openfile:
            reader = csv.reader(openfile, delimiter="|")
            headers = next(reader)
            for r in reader:
                v3_ct += 1

        self.assertEqual(v3_ct, v4_ct)

    def test_v3migration_006_import_data_and_relations(self):
        """Test the conversion and import of v3 business data."""

        # test run of the command line tool that writes the v4 json
        # this data is not loaded at this time.
        rm_dir = os.path.join(self.pkg, "graphs", "resource_models")
        all_models = [os.path.splitext(i)[0] for i in os.listdir(rm_dir) if i.endswith(".json")]

        temp_file = os.path.join(self.pkg, "business_data", "single_resource.json")
        management.call_command("v3", "write-v4-json", target=self.pkg, number=10, resource_models=all_models, verbose=True)

        # basic test to make sure the v4 file has been created. No tests on
        # the actual data load operations are performed up to this point.
        v4_bd = os.path.join(self.pkg, "business_data", "v3sample-Historic Resource.json")
        self.assertTrue(os.path.isfile(v4_bd))

        # return early if the migration data should not actually be loaded
        if not test_settings.LOAD_V3_DATA_DURING_TESTS:
            return

        # load all of the reference data
        self.load_v4_reference_data()

        # initial checks on the database contents
        ResourceInstance.objects.all().delete()
        self.assertEqual(Tile.objects.all().count(), 0)

        # now do a much more granular set of tests on the import process itself
        v3_bd = os.path.join(self.pkg, "v3data", "business_data", "v3sample.json")
        for rm in all_models:

            print("testing import of " + rm)
            importer = v3Importer(os.path.join(self.pkg, "v3data"), rm, v3_bd)

            # process and import the v3 resources one at a time and
            # test the value and tile counts during this process.
            for res in importer.v3_resources:

                v3_resource = v3PreparedResource(res, importer.v4_graph.graphid, importer.node_lookup, importer.v3_mergenodes)
                v3_value_ct = len(v3_resource.node_list)

                v3_resource.process(importer.v4_nodes)
                v4_json = v3_resource.get_resource_json()

                out_json = {"business_data": {"resources": [v4_json]}}
                with open(temp_file, "wb") as openfile:
                    openfile.write(JSONSerializer().serialize(out_json, indent=4))

                existing = ResourceInstance.objects.all().count()
                management.call_command("packages", operation="import_business_data", source=temp_file, overwrite="overwrite")

                self.assertEqual(ResourceInstance.objects.all().count(), existing + 1)

                resid = v4_json["resourceinstance"]["resourceinstanceid"]
                v4_counts = v3utils.count_tiles_and_values(resid)
                self.assertEqual(v3_value_ct, len(v4_counts["values"]))

        # test loading of the resource relations
        self.assertEqual(ResourceXResource.objects.all().count(), 0)

        # run the conversion command.
        management.call_command("v3", "write-v4-relations", "--import", target=self.pkg)

        # get count of v3 relationships for comparison
        v3_ct = 0
        v3_relations = os.path.join(self.pkg, "v3data", "business_data", "v3sample.relations")
        with open(v3_relations, "rb") as openfile:
            reader = csv.reader(openfile, delimiter="|")
            headers = next(reader)
            for r in reader:
                v3_ct += 1

        # test that the number of loaded relations matches the number in the
        # original v3 file
        self.assertEqual(ResourceXResource.objects.all().count(), v3_ct)
