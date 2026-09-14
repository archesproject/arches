from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase

from arches.app.models.models import ETLModule, LoadEvent
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

        self.assertEqual(result["status"], 409)
        event.refresh_from_db()
        self.assertEqual(event.status, "failed")
        self.assertTrue(event.error_message)
