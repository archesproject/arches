import base64
import json
import os
import tempfile
import uuid
import zipfile
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.http import HttpRequest
from django.test import SimpleTestCase, TestCase

from arches.app.models.graph import Graph
from arches.app.models.models import (
    EditLog,
    ETLModule,
    File,
    GeoJSONGeometry,
    LoadErrors,
    LoadEvent,
    NodeGroup,
    ResourceInstance,
    ResourceXResource,
    TileModel,
)
from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.utils.data_management.resource_graphs.importer import (
    import_graph as resource_graph_importer,
)
from tests.base_test import ArchesTransactionTestCase
from arches.app.etl_modules.arches_json_importer import (
    ArchesJsonImporter,
    DB_CHECK_BATCH_SIZE,
    MEMO_MAX_VALUES_PER_NODE,
)

# these tests can be run from the command line via
# python manage.py test tests.bulkdata.arches_json_import_tests --settings="tests.test_settings"


# __init__ needs a user and a load event; these cover the pure validation logic.
def _bare_importer():
    importer = object.__new__(ArchesJsonImporter)
    importer.validated_data = {}
    importer._memo_disabled_nodes = set()
    return importer


class FileListShapeTests(SimpleTestCase):
    def test_accepts_localized_metadata(self):
        value = [
            {
                "file_id": "8a1e1c2b-0000-4000-8000-000000000001",
                "name": "plan.pdf",
                "altText": {"en": {"value": "A plan", "direction": "ltr"}},
            }
        ]
        self.assertIsNone(ArchesJsonImporter._check_file_list_shape(value))

    # A bare string here poisons the Elasticsearch mapping for every later
    # document, so it has to be rejected at import rather than written through.
    def test_rejects_bare_string_metadata(self):
        value = [
            {
                "file_id": "8a1e1c2b-0000-4000-8000-000000000001",
                "name": "plan.pdf",
                "altText": "A plan",
            }
        ]
        error = ArchesJsonImporter._check_file_list_shape(value)
        self.assertIsNotNone(error)
        self.assertIn("altText", str(error))

    def test_rejects_missing_file_id(self):
        self.assertIsNotNone(
            ArchesJsonImporter._check_file_list_shape([{"name": "plan.pdf"}])
        )

    def test_rejects_non_list(self):
        self.assertIsNotNone(
            ArchesJsonImporter._check_file_list_shape({"name": "plan.pdf"})
        )

    def test_allows_absent_and_null_metadata(self):
        value = [
            {
                "file_id": "8a1e1c2b-0000-4000-8000-000000000001",
                "name": "plan.pdf",
                "altText": None,
            }
        ]
        self.assertIsNone(ArchesJsonImporter._check_file_list_shape(value))


class ConstraintCandidateTests(SimpleTestCase):
    NODE = "3f0f1a44-0000-4000-8000-00000000000a"
    NODEGROUP = "9c2b7d10-0000-4000-8000-00000000000b"

    def _graph(self):
        return {"constraints": {self.NODEGROUP: [[self.NODE]]}}

    def test_same_value_on_two_resources_collides(self):
        candidates = {}
        for resourceid in ("resource-1", "resource-2"):
            ArchesJsonImporter._collect_constraint_candidates(
                {"nodegroup_id": self.NODEGROUP, "data": {self.NODE: "REF-001"}},
                resourceid,
                self._graph(),
                candidates,
            )
        group = candidates[(self.NODEGROUP, (self.NODE,))]
        self.assertEqual(len(group), 1, "one distinct value expected")
        self.assertEqual(
            sorted(next(iter(group.values()))), ["resource-1", "resource-2"]
        )

    def test_distinct_values_do_not_collide(self):
        candidates = {}
        for resourceid, ref in (("resource-1", "REF-001"), ("resource-2", "REF-002")):
            ArchesJsonImporter._collect_constraint_candidates(
                {"nodegroup_id": self.NODEGROUP, "data": {self.NODE: ref}},
                resourceid,
                self._graph(),
                candidates,
            )
        group = candidates[(self.NODEGROUP, (self.NODE,))]
        self.assertEqual(len(group), 2)
        for resourceids in group.values():
            self.assertEqual(len(resourceids), 1)

    def test_null_value_is_not_a_candidate(self):
        candidates = {}
        ArchesJsonImporter._collect_constraint_candidates(
            {"nodegroup_id": self.NODEGROUP, "data": {self.NODE: None}},
            "resource-1",
            self._graph(),
            candidates,
        )
        self.assertEqual(candidates.get((self.NODEGROUP, (self.NODE,)), {}), {})


class TileNodegroupTests(SimpleTestCase):
    GRAPH = "5c1f0e22-0000-4000-8000-00000000000c"
    NODEGROUP = "9c2b7d10-0000-4000-8000-00000000000b"

    def _validate(self, tile, cardinality):
        graph = {
            "graphid": self.GRAPH,
            "cardinality": cardinality,
            "constraints": {},
            "nodes": {},
        }
        return _bare_importer()._validate_tile(
            tile, "resource-1", graph, "data.json", {}, {}
        )

    def test_tile_without_a_nodegroup_is_rejected(self):
        errors = self._validate({"tileid": "t1", "data": {}}, {})
        self.assertEqual(len(errors), 1)
        self.assertIn("no nodegroup_id", errors[0]["error"])

    # The id comes from the file and load_errors.nodegroupid is a real foreign
    # key, so an unknown nodegroup must not be recorded against it.
    def test_nodegroup_outside_the_graph_is_rejected_without_a_foreign_key(self):
        errors = self._validate(
            {"tileid": "t1", "nodegroup_id": self.NODEGROUP, "data": {}}, {}
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("is not in graph", errors[0]["error"])
        self.assertIsNone(errors[0]["nodegroupid"])

    # A nodegroup whose only node is semantic contributes no entry to "nodes"
    # but is still a real nodegroup, so the check above must not reject it.
    def test_semantic_only_nodegroup_is_accepted(self):
        errors = self._validate(
            {"tileid": "t1", "nodegroup_id": self.NODEGROUP, "data": {}},
            {self.NODEGROUP: "n"},
        )
        self.assertEqual(errors, [])

    def _collect(self, cardinality, parenttile_id=None):
        keys = {}
        graph = {
            "graphid": self.GRAPH,
            "cardinality": {self.NODEGROUP: cardinality},
            "constraints": {},
            "nodes": {},
        }
        tile = {"tileid": "t1", "nodegroup_id": self.NODEGROUP, "data": {}}
        if parenttile_id:
            tile["parenttile_id"] = parenttile_id
        _bare_importer()._validate_tile(
            tile, "resource-1", graph, "data.json", {}, keys
        )
        return keys

    # Without this key nothing reaches _check_existing_cardinality, so a second
    # tile on a single-value nodegroup would be written unnoticed.
    def test_single_value_nodegroup_registers_a_cardinality_key(self):
        keys = self._collect("1")
        self.assertEqual(list(keys), [("resource-1", self.NODEGROUP, None)])
        self.assertEqual(keys[("resource-1", self.NODEGROUP, None)], ["t1"])

    def test_multi_value_nodegroup_registers_nothing(self):
        self.assertEqual(self._collect("n"), {})

    # Cardinality on a child nodegroup is per parent tile, so sibling tiles under
    # different parents must not share a key.
    def test_the_parent_tile_is_part_of_the_key(self):
        keys = self._collect("1", parenttile_id="parent-1")
        self.assertEqual(list(keys), [("resource-1", self.NODEGROUP, "parent-1")])


class ValidationMemoTests(SimpleTestCase):
    NODE = "3f0f1a44-0000-4000-8000-00000000000a"

    # Without the cap a large load retains every distinct string it has seen.
    def test_memo_is_dropped_for_high_cardinality_nodes(self):
        importer = _bare_importer()
        node = {"datatype": "string", "config": {}}

        class _NoErrors:
            def validate(self, value, **kwargs):
                return []

        class _Factory:
            def get_instance(self, datatype):
                return _NoErrors()

        importer.datatype_factory = _Factory()

        for i in range(MEMO_MAX_VALUES_PER_NODE + 5):
            importer._validate_value(node, self.NODE, f"value-{i}")

        self.assertIn(self.NODE, importer._memo_disabled_nodes)
        self.assertNotIn(self.NODE, importer.validated_data)

    def test_memo_returns_cached_errors(self):
        importer = _bare_importer()
        node = {"datatype": "string", "config": {}}
        calls = []

        class _CountingDatatype:
            def validate(self, value, **kwargs):
                calls.append(value)
                return [{"title": "bad", "message": "bad"}]

        class _Factory:
            def get_instance(self, datatype):
                return _CountingDatatype()

        importer.datatype_factory = _Factory()

        first = importer._validate_value(node, self.NODE, "repeated")
        second = importer._validate_value(node, self.NODE, "repeated")
        self.assertEqual(first, second)
        self.assertEqual(len(calls), 1, "second call should be served from the memo")


class BatchedDbCheckTests(SimpleTestCase):
    def test_batches_cover_everything_in_order(self):
        items = list(range(4_200_000))
        batches = list(ArchesJsonImporter._in_batches(items))
        self.assertEqual([x for b in batches for x in b], items)
        self.assertLessEqual(max(len(b) for b in batches), DB_CHECK_BATCH_SIZE)

    # legacyid__in becomes one bind parameter per value; Postgres caps at 65,535.
    def test_batch_stays_under_the_bind_parameter_limit(self):
        self.assertLess(DB_CHECK_BATCH_SIZE, 65535)

    def test_empty_input_runs_no_query(self):
        self.assertEqual(list(ArchesJsonImporter._in_batches([])), [])

    # _check_global_constraints batches the candidate-value dict this way.
    def test_a_dict_batches_by_key(self):
        keys = {f"k{i}": i for i in range(5)}
        self.assertEqual(
            list(ArchesJsonImporter._in_batches(keys, 2)),
            [["k0", "k1"], ["k2", "k3"], ["k4"]],
        )


# load_errors.nodeid and .nodegroupid are real foreign keys, so an id the file
# names but the database lacks used to fail the whole error batch with it.
class UnknownReferenceTests(TestCase):
    MISSING_NODEGROUP = "0efb4349-fded-583a-a8af-08d6c0781e40"
    MISSING_NODE = "1b2c3d4e-0000-4000-8000-00000000000f"

    def _failure(self, **overrides):
        failure = {
            "source": "data.json",
            "error": "Invalid value",
            "message": "something was wrong",
            "nodeid": None,
            "nodegroupid": None,
            "datatype": None,
            "value": None,
        }
        failure.update(overrides)
        return failure

    def test_unknown_nodegroup_is_moved_out_of_the_foreign_key(self):
        failures = [self._failure(nodegroupid=self.MISSING_NODEGROUP)]
        ArchesJsonImporter._demote_unknown_references(failures)

        self.assertIsNone(failures[0]["nodegroupid"])
        self.assertIn(self.MISSING_NODEGROUP, failures[0]["message"])
        self.assertIn("not in this database", failures[0]["message"])

    def test_unknown_node_is_moved_out_of_the_foreign_key(self):
        failures = [self._failure(nodeid=self.MISSING_NODE, datatype="string")]
        ArchesJsonImporter._demote_unknown_references(failures)

        self.assertIsNone(failures[0]["nodeid"])
        self.assertIn(self.MISSING_NODE, failures[0]["message"])

    def test_failures_without_references_are_untouched(self):
        failures = [self._failure(error="missing graph_id", message="missing graph_id")]
        ArchesJsonImporter._demote_unknown_references(failures)
        self.assertEqual(failures[0]["message"], "missing graph_id")

    # The counterpart to the two above: a real id must reach load_errors, or the
    # error report loses its node attribution for every genuine failure.
    def test_a_known_nodegroup_keeps_its_foreign_key(self):
        nodegroup = NodeGroup.objects.create(nodegroupid=uuid.uuid4())
        failures = [self._failure(nodegroupid=str(nodegroup.nodegroupid))]
        ArchesJsonImporter._demote_unknown_references(failures)

        self.assertEqual(failures[0]["nodegroupid"], str(nodegroup.nodegroupid))
        self.assertEqual(failures[0]["message"], "something was wrong")


# _in_batches is only worth anything if the callers actually use it.
class BatchedQueryTests(TestCase):
    def test_the_legacyid_lookup_is_issued_one_batch_at_a_time(self):
        importer = _bare_importer()
        legacyids = {
            "legacy-{}".format(i): (str(uuid.uuid4()), "data.json") for i in range(5)
        }
        with patch(
            "arches.app.etl_modules.arches_json_importer.DB_CHECK_BATCH_SIZE", 2
        ):
            with self.assertNumQueries(3):
                importer._check_existing_legacyids(legacyids)

    def test_one_batch_is_one_query(self):
        importer = _bare_importer()
        legacyids = {"legacy-1": (str(uuid.uuid4()), "data.json")}
        with self.assertNumQueries(1):
            importer._check_existing_legacyids(legacyids)


# Tile triggers are disabled database-wide, so a second concurrent load is
# refused. It must still be moved off "running", which the badge reads as
# "Validating", and told why.
class TriggerLockContentionTests(TestCase):
    def test_a_refused_load_is_marked_failed_with_a_reason(self):
        user = User.objects.create_user("lock-contention-tester")
        module = ETLModule.objects.get(slug="arches-json-importer")
        event = LoadEvent.objects.create(user=user, etl_module=module, status="running")

        importer = _bare_importer()
        importer.loadid = str(event.loadid)
        importer.config = {}
        importer._acquire_trigger_lock = lambda cursor: False

        result = importer.save_to_tiles(None, user.id, event.loadid)

        self.assertFalse(result["success"])
        self.assertEqual(result["data"]["title"], "Another bulk load is running")
        event.refresh_from_db()
        self.assertEqual(event.status, "failed")
        self.assertTrue(event.error_message)


# The parser's module choices come from the ETLModule table, so this also
# confirms the migration registered the importer.
class EtlCommandFlagTests(TestCase):
    MODULE = "arches-json-importer"

    def _parse(self, *argv):
        from arches.management.commands.etl import Command

        parser = Command().create_parser("manage.py", "etl")
        return vars(parser.parse_args([self.MODULE, "-s", "export.jsonl", *argv]))

    def test_overwrite_is_off_and_indexing_on_by_default(self):
        options = self._parse()
        self.assertFalse(options["overwrite"])
        self.assertTrue(options["index"])

    def test_overwrite_short_flag(self):
        self.assertTrue(self._parse("-ow")["overwrite"])

    def test_overwrite_long_flag(self):
        self.assertTrue(self._parse("--overwrite")["overwrite"])

    def test_no_index(self):
        self.assertFalse(self._parse("--no-index")["index"])

    def test_multiprocessing_flags(self):
        options = self._parse("-mp", "-mxp", "8")
        self.assertTrue(options["use_multiprocessing"])
        self.assertEqual(options["max_subprocesses"], 8)


# The file validator sniffs zip members, so the test needs a real image.
ONE_PIXEL_PNG = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
ALL_DATATYPES = "d71a8f56-987f-4fd1-87b5-538378740f15"
STRING_NODE = "bf611c24-c8be-11ed-b6a9-0242ac130009"
FILE_NODE = "1d1bfbea-c8bf-11ed-bf64-0242ac130009"
IMAGE_NODE = "f85dab40-791d-11ee-88a6-0242ac130007"
RESOURCE_NODE = "402c95f2-c8c1-11ed-87a7-0242ac130009"
GEOMETRY_NODE = "be25bdf0-c8bf-11ed-a172-0242ac130009"


def _resource(resourceid, *tiles):
    return {
        "resourceinstance": {
            "resourceinstanceid": str(resourceid),
            "graph_id": ALL_DATATYPES,
            "legacyid": None,
        },
        "tiles": list(tiles),
    }


# Every test node is the only node in its own nodegroup, so nodegroup id == node id.
def _tile(nodeid, value, tileid=None):
    return {
        "tileid": str(tileid or uuid.uuid4()),
        "nodegroup_id": nodeid,
        "parenttile_id": None,
        "sortorder": 0,
        "data": {nodeid: value},
    }


def _text(value):
    return {"en": {"value": value, "direction": "ltr"}}


def _point():
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "id": str(uuid.uuid4()),
                "properties": {},
                "geometry": {"type": "Point", "coordinates": [-5.93, 54.6]},
            }
        ],
    }


def _file(file_id, name):
    return {"file_id": file_id, "name": name, "status": "uploaded", "size": 10}


class ArchesJsonImportWriteTests(ArchesTransactionTestCase):
    serialized_rollback = True

    def setUp(self):
        with open("tests/fixtures/resource_graphs/All_Datatypes.json") as f:
            archesfile = JSONDeserializer().deserialize(f)
        resource_graph_importer(archesfile["graph"])
        Graph.objects.get(graphid=ALL_DATATYPES).publish(user=self.test_users["admin"])

    def _cli(self, *resources, overwrite=False):
        loadid = str(uuid.uuid4())
        module = ETLModule.objects.get(slug="arches-json-importer")
        importer = ArchesJsonImporter(
            loadid=loadid,
            params={
                "module": str(module.etlmoduleid),
                "overwrite": overwrite,
                "index": False,
            },
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "load.jsonl")
            with open(path, "w") as f:
                f.writelines(json.dumps(r) + "\n" for r in resources)
            return loadid, importer.cli(path)

    def _load(self, *resources, overwrite=False, status="completed"):
        loadid, response = self._cli(*resources, overwrite=overwrite)
        errors = list(
            LoadErrors.objects.filter(load_event_id=loadid).values_list(
                "message", flat=True
            )
        )
        # The load's status, not cli()'s answer: a load that fails validation still
        # comes back as a success, so the UI can show its error report.
        actual = LoadEvent.objects.get(loadid=loadid).status
        self.assertEqual(actual, status, f"{response} {errors}")
        return loadid

    def _read(self, path):
        module = ETLModule.objects.get(slug="arches-json-importer")
        importer = ArchesJsonImporter(
            loadid=str(uuid.uuid4()), params={"module": str(module.etlmoduleid)}
        )
        importer.start(importer.request)

        def cleanup():
            if default_storage.exists(importer.temp_dir):
                importer.delete_from_default_storage(importer.temp_dir)

        self.addCleanup(cleanup)
        return importer.read(source=path)

    def test_a_failed_write_is_reported_as_a_failure(self):
        monument = uuid.uuid4()
        with patch.object(
            ArchesJsonImporter, "_acquire_trigger_lock", return_value=False
        ):
            loadid, response = self._cli(
                _resource(monument, _tile(STRING_NODE, _text("Monument 17")))
            )

        self.assertFalse(response["success"])
        self.assertIn("Try again when it finishes", response["data"]["message"])
        self.assertEqual(LoadEvent.objects.get(loadid=loadid).status, "failed")

    def test_a_failed_index_is_not_reported_as_a_failed_write(self):
        with patch(
            "arches.app.etl_modules.arches_json_importer._post_save_edit_log",
            return_value={"success": False, "data": "saved"},
        ):
            loadid, response = self._cli(
                _resource(uuid.uuid4(), _tile(STRING_NODE, _text("Monument 17")))
            )

        self.assertTrue(response["success"], response)

    def test_a_rejected_upload_says_why_and_closes_the_file(self):
        opened = []

        def tracking_open(*args, **kwargs):
            opened.append(open(*args, **kwargs))
            return opened[-1]

        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "notes.txt")
            with open(path, "w") as f:
                f.write("not an export")
            with patch(
                "arches.app.etl_modules.arches_json_importer.open",
                tracking_open,
                create=True,
            ):
                response = self._read(path)

        self.assertEqual(response["data"]["title"], "Invalid file")
        self.assertTrue(opened and all(f.closed for f in opened))

    def _errors(self, loadid):
        return " | ".join(
            LoadErrors.objects.filter(load_event_id=loadid).values_list(
                "error", flat=True
            )
        )

    def test_an_existing_resource_fails_without_overwrite(self):
        monument, name = uuid.uuid4(), uuid.uuid4()
        self._load(_resource(monument, _tile(STRING_NODE, _text("Monument 17"), name)))

        loadid = self._load(
            _resource(monument, _tile(STRING_NODE, _text("Monument 17, again"))),
            status="failed",
        )

        self.assertIn("already exists", self._errors(loadid))
        self.assertEqual(
            list(
                TileModel.objects.filter(resourceinstance_id=monument).values_list(
                    "tileid", flat=True
                )
            ),
            [name],
        )

    def test_a_tile_held_by_another_resource_fails_even_with_overwrite(self):
        monument, site, tile = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
        self._load(_resource(monument, _tile(STRING_NODE, _text("Monument 17"), tile)))

        loadid = self._load(
            _resource(site, _tile(STRING_NODE, _text("Site 4"), tile)),
            overwrite=True,
            status="failed",
        )

        self.assertIn("already belongs to resource", self._errors(loadid))
        self.assertFalse(ResourceInstance.objects.filter(pk=site).exists())

    def test_a_tile_used_twice_in_one_import_fails(self):
        tile = uuid.uuid4()
        loadid = self._load(
            _resource(uuid.uuid4(), _tile(STRING_NODE, _text("Monument 17"), tile)),
            _resource(uuid.uuid4(), _tile(STRING_NODE, _text("Site 4"), tile)),
            status="failed",
        )

        self.assertIn("more than once", self._errors(loadid))

    def test_overwrite_matches_ids_whatever_their_case(self):
        monument, tile = uuid.uuid4(), uuid.uuid4()
        self._load(_resource(monument, _tile(STRING_NODE, _text("Monument 17"), tile)))

        self._load(
            _resource(
                str(monument).upper(),
                _tile(STRING_NODE, _text("Monument 17, renamed"), str(tile).upper()),
            ),
            overwrite=True,
        )

        self.assertEqual(
            TileModel.objects.get(pk=tile).data[STRING_NODE]["en"]["value"],
            "Monument 17, renamed",
        )

    def test_a_file_used_twice_in_one_import_fails(self):
        plan = str(uuid.uuid4())
        loadid = self._load(
            _resource(uuid.uuid4(), _tile(FILE_NODE, [_file(plan, "plan.pdf")])),
            _resource(uuid.uuid4(), _tile(FILE_NODE, [_file(plan, "plan.pdf")])),
            status="failed",
        )

        self.assertIn("more than once", self._errors(loadid))
        self.assertFalse(File.objects.filter(fileid=plan).exists())

    def test_a_file_held_by_another_resource_fails_in_either_mode(self):
        plan = str(uuid.uuid4())
        self._load(_resource(uuid.uuid4(), _tile(FILE_NODE, [_file(plan, "plan.pdf")])))
        owner = File.objects.get(fileid=plan).tile_id

        for overwrite in (False, True):
            with self.subTest(overwrite=overwrite):
                site = uuid.uuid4()
                loadid = self._load(
                    _resource(site, _tile(FILE_NODE, [_file(plan, "plan.pdf")])),
                    overwrite=overwrite,
                    status="failed",
                )
                self.assertIn("already in the database", self._errors(loadid))
                self.assertFalse(ResourceInstance.objects.filter(pk=site).exists())
                self.assertEqual(File.objects.get(fileid=plan).tile_id, owner)

    def test_a_zip_lists_the_files_it_ignores(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "export.zip")
            with zipfile.ZipFile(path, "w") as zf:
                zf.writestr(
                    "export.json", json.dumps({"business_data": {"resources": []}})
                )
                zf.writestr("photo.png", base64.b64decode(ONE_PIXEL_PNG))
            response = self._read(path)

        self.assertIn("data", response, response)
        self.assertEqual(response["data"]["summary"]["ignored_files"], 1)

    def test_overwrite_keeps_the_resource_and_links_into_it(self):
        monument, site = uuid.uuid4(), uuid.uuid4()
        name, geometry = uuid.uuid4(), uuid.uuid4()
        self._load(
            _resource(
                monument,
                _tile(STRING_NODE, _text("Monument 17"), name),
                _tile(GEOMETRY_NODE, _point(), geometry),
            )
        )
        link = {
            "resourceId": str(monument),
            "ontologyProperty": "",
            "inverseOntologyProperty": "",
        }
        self._load(_resource(site, _tile(RESOURCE_NODE, [link])))
        createdtime = ResourceInstance.objects.get(pk=monument).createdtime

        loadid = self._load(
            _resource(
                monument, _tile(STRING_NODE, _text("Monument 17, renamed"), name)
            ),
            overwrite=True,
        )

        self.assertTrue(
            ResourceXResource.objects.filter(
                from_resource_id=site, to_resource_id=monument
            ).exists()
        )
        site_tile = TileModel.objects.get(resourceinstance_id=site)
        self.assertEqual(site_tile.data[RESOURCE_NODE][0]["resourceId"], str(monument))
        self.assertEqual(
            ResourceInstance.objects.get(pk=monument).createdtime, createdtime
        )
        self.assertEqual(
            list(
                TileModel.objects.filter(resourceinstance_id=monument).values_list(
                    "tileid", flat=True
                )
            ),
            [name],
        )
        self.assertFalse(
            GeoJSONGeometry.objects.filter(resourceinstance_id=monument).exists()
        )
        self.assertFalse(
            EditLog.objects.filter(transactionid=loadid, edittype="create").exists()
        )
        deleted = EditLog.objects.filter(transactionid=loadid, edittype="tile delete")
        self.assertEqual(
            list(deleted.values_list("tileinstanceid", flat=True)), [str(geometry)]
        )

    def test_overwrite_keeps_the_row_of_a_file_it_imports_again(self):
        monument = uuid.uuid4()
        plan, sketch = str(uuid.uuid4()), str(uuid.uuid4())
        plan_tile, sketch_tile = uuid.uuid4(), uuid.uuid4()
        self._load(
            _resource(
                monument,
                _tile(FILE_NODE, [_file(plan, "plan.pdf")], plan_tile),
                _tile(IMAGE_NODE, [_file(sketch, "sketch.png")], sketch_tile),
            )
        )
        File.objects.filter(fileid=plan).update(
            path="uploadedfiles/plan_aB3x.pdf", thumbnail_data=b"thumb"
        )

        # The same tile id, as a real re-export has. Logging it as both deleted and
        # created would make _post_process upsert the file row twice and fail.
        loadid = self._load(
            _resource(monument, _tile(FILE_NODE, [_file(plan, "plan.pdf")], plan_tile)),
            overwrite=True,
        )

        kept = File.objects.get(fileid=plan)
        self.assertEqual(kept.path.name, "uploadedfiles/plan_aB3x.pdf")
        self.assertEqual(bytes(kept.thumbnail_data), b"thumb")
        self.assertEqual(kept.tile_id, plan_tile)
        self.assertFalse(File.objects.filter(fileid=sketch).exists())
        deleted = EditLog.objects.filter(transactionid=loadid, edittype="tile delete")
        self.assertEqual(
            list(deleted.values_list("tileinstanceid", flat=True)), [str(sketch_tile)]
        )

    def test_overwrite_reattaches_a_file_a_failed_overwrite_left_unhooked(self):
        monument, plan_tile = uuid.uuid4(), uuid.uuid4()
        plan = str(uuid.uuid4())
        self._load(
            _resource(monument, _tile(FILE_NODE, [_file(plan, "plan.pdf")], plan_tile))
        )
        File.objects.filter(fileid=plan).update(tile=None)

        self._load(
            _resource(monument, _tile(FILE_NODE, [_file(plan, "plan.pdf")], plan_tile)),
            overwrite=True,
        )

        self.assertEqual(File.objects.get(fileid=plan).tile_id, plan_tile)

    def _reverse(self, loadid):
        request = HttpRequest()
        request.method = "POST"
        request.user = self.test_users["admin"]
        request.POST["loadid"] = loadid
        return ArchesJsonImporter(loadid=loadid).reverse(request)

    def test_a_load_can_be_undone(self):
        monument = uuid.uuid4()
        loadid = self._load(
            _resource(monument, _tile(STRING_NODE, _text("Monument 17")))
        )

        response = self._reverse(loadid)

        self.assertTrue(response["success"], response)
        self.assertFalse(ResourceInstance.objects.filter(pk=monument).exists())
        self.assertEqual(LoadEvent.objects.get(loadid=loadid).status, "unloaded")

    def test_an_overwrite_load_cannot_be_undone(self):
        monument = uuid.uuid4()
        self._load(_resource(monument, _tile(STRING_NODE, _text("Monument 17"))))
        loadid = self._load(
            _resource(monument, _tile(STRING_NODE, _text("Monument 17, renamed"))),
            overwrite=True,
        )

        response = self._reverse(loadid)

        self.assertFalse(response["success"])
        self.assertIn("cannot be undone", response["data"]["message"])
        self.assertTrue(TileModel.objects.filter(resourceinstance_id=monument).exists())

    def test_a_write_failure_says_how_far_it_got(self):
        first, second, third = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
        real_chunks = ArchesJsonImporter._iter_resource_chunks
        real_write = ArchesJsonImporter._write_chunk
        calls = []

        def one_per_chunk(importer, chunk_size):
            return real_chunks(importer, 1)

        def second_chunk_fails(importer, *args):
            calls.append(args)
            if len(calls) == 2:
                raise RuntimeError("disk full")
            return real_write(importer, *args)

        with (
            patch.object(ArchesJsonImporter, "_iter_resource_chunks", one_per_chunk),
            patch.object(ArchesJsonImporter, "_write_chunk", second_chunk_fails),
        ):
            loadid = self._load(
                *(
                    _resource(r, _tile(STRING_NODE, _text("Monument")))
                    for r in (first, second, third)
                ),
                status="failed",
            )

        message = LoadEvent.objects.get(loadid=loadid).error_message
        self.assertIn(
            f"Wrote 1 of 3 resources; the chunk starting at resource {second} (#2) "
            "failed: disk full",
            message,
        )
        self.assertIn("Undo the load", message)
        self.assertEqual(
            list(
                ResourceInstance.objects.filter(
                    pk__in=[first, second, third]
                ).values_list("pk", flat=True)
            ),
            [first],
        )
