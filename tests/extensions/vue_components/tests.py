from uuid import uuid4
from django.test import TestCase
from django.core import management
from django.test.utils import captured_stdout

from arches.app.models.models import Widget
from arches.extensions.vue_components.models import WidgetMapping
from arches.extensions.vue_components.utils.widget_synchronizer import (
    WidgetSynchronizer,
)


class WidgetSynchronizerTestCase(TestCase):
    def setUp(self):
        self.dummy_widget_0 = Widget.objects.create(
            widgetid=uuid4(),
            name="dummy-widget",
            component="views/components/widgets/dummy",
            helptext=None,
            datatype="string",
            defaultconfig={"defaultValue": None},
        )

        self.dummy_widget_1 = Widget.objects.create(
            widgetid=uuid4(),
            name="another-widget",
            component="views/components/widgets/another",
            helptext=None,
            datatype="string",
            defaultconfig={"defaultValue": None},
        )

    def tearDown(self):
        WidgetMapping.objects.filter(
            widget__in=[self.dummy_widget_0, self.dummy_widget_1]
        ).delete()
        self.dummy_widget_0.delete()
        self.dummy_widget_1.delete()
        super().tearDown()

    def test_check_for_missing_mappings(self):
        self.assertFalse(
            WidgetMapping.objects.filter(
                widget_id__in=[
                    self.dummy_widget_0.widgetid,
                    self.dummy_widget_1.widgetid,
                ]
            ).exists()
        )
        widgets_without_mappings = WidgetSynchronizer().check_for_missing_mappings()
        self.assertIn(self.dummy_widget_0.widgetid, widgets_without_mappings)
        self.assertIn(self.dummy_widget_1.widgetid, widgets_without_mappings)

    def test_add_mapping(self):
        self.assertFalse(
            WidgetMapping.objects.filter(
                widget_id__in=[
                    self.dummy_widget_0.widgetid,
                    self.dummy_widget_1.widgetid,
                ]
            ).exists()
        )
        synchronizer = WidgetSynchronizer()
        expected_component_path_0 = (
            "arches_vue_components/widgets/DummyWidget/DummyWidget.vue"
        )

        mapping_0 = synchronizer.add_mapping(
            self.dummy_widget_0.name,
            expected_component_path_0,
        )

        self.assertIsNotNone(mapping_0)
        self.assertEqual(mapping_0.widget, self.dummy_widget_0)
        self.assertEqual(mapping_0.component, expected_component_path_0)

    def test_validate(self):
        with captured_stdout() as stdout:
            management.call_command("validate", "--codes", "2001", "--verbosity", "2")
            output = stdout.getvalue()
            self.assertIn(
                "Widgets without a mapping to an Arches Vue Components Vue component",
                output,
            )
