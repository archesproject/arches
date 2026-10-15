import uuid
from unittest.mock import patch

from arches.app.etl_modules.save import _call_post_import_functions
from arches.app.functions.base import BaseFunction
from arches.app.models.models import EditLog, Function, FunctionXGraph, GraphModel
from tests.base_test import ArchesTestCase

# these tests can be run from the command line via
# python manage.py test tests.bulkdata.post_import_tests --settings="tests.test_settings"


class RecordingFunction(BaseFunction):
    calls = []

    def post_import(self, transaction_id, *args, **kwargs):
        RecordingFunction.calls.append((self.config, transaction_id))


class CallPostImportFunctionsTests(ArchesTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.loaded_graph = GraphModel.objects.create(
            graphid=uuid.uuid4(), slug="post-import-loaded", isresource=True
        )
        cls.other_graph = GraphModel.objects.create(
            graphid=uuid.uuid4(), slug="post-import-other", isresource=True
        )

        def make_function(functiontype, classname="RecordingFunction"):
            return Function.objects.create(
                functionid=uuid.uuid4(),
                functiontype=functiontype,
                modulename="post_import_tests.py",
                classname=classname,
            )

        cls.graph_function = make_function("node_value")
        FunctionXGraph.objects.create(
            graph=cls.loaded_graph,
            function=cls.graph_function,
            config={"name": "loaded graph"},
        )
        FunctionXGraph.objects.create(
            graph=cls.other_graph,
            function=cls.graph_function,
            config={"name": "other graph"},
        )
        FunctionXGraph.objects.create(
            graph=cls.loaded_graph,
            function=make_function("primarydescriptors"),
            config={"name": "descriptors"},
        )
        cls.global_function = make_function("global")
        cls.unimplemented_function = make_function("global", "BaseFunction")

        cls.transaction_id = uuid.uuid4()
        EditLog.objects.create(
            resourceclassid=str(cls.loaded_graph.pk),
            resourceinstanceid=str(uuid.uuid4()),
            transactionid=cls.transaction_id,
            edittype="create",
        )

    def setUp(self):
        RecordingFunction.calls = []
        test_functionids = {
            self.graph_function.pk,
            self.global_function.pk,
            self.unimplemented_function.pk,
        }
        original_get_class_module = Function.get_class_module

        def get_class_module(function):
            # only route the functions created here to the test classes, so
            # functions registered by migrations behave as they would in a load
            if function.pk not in test_functionids:
                return original_get_class_module(function)
            if function.classname == "RecordingFunction":
                return RecordingFunction
            return BaseFunction

        patcher = patch.object(
            Function, "get_class_module", autospec=True, side_effect=get_class_module
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_calls_functions_bound_to_loaded_graphs_and_globals(self):
        _call_post_import_functions(self.transaction_id)

        self.assertCountEqual(
            RecordingFunction.calls,
            [
                ({"name": "loaded graph"}, self.transaction_id),
                (None, self.transaction_id),
            ],
        )

    def test_only_calls_globals_when_load_touched_no_bound_graphs(self):
        other_transaction_id = uuid.uuid4()

        _call_post_import_functions(other_transaction_id)

        self.assertEqual(RecordingFunction.calls, [(None, other_transaction_id)])
