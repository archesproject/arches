from django.test import SimpleTestCase

from arches.app.utils.decorators import deprecated

# these tests can be run from the command line via
# python manage.py test tests.utils.test_decorators --settings="tests.test_settings"


@deprecated
def deprecated_function(a, b=0):
    """Adds two numbers."""
    return a + b


class DeprecatedMethodHolder:
    @deprecated
    def deprecated_method(self):
        return self


class DeprecatedDecoratorTests(SimpleTestCase):
    def test_wrapped_function_still_runs(self):
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(deprecated_function(1, b=2), 3)

    def test_warning_message(self):
        with self.assertWarns(DeprecationWarning) as cm:
            deprecated_function(1)

        self.assertEqual(
            str(cm.warning),
            "Call to deprecated function tests.utils.test_decorators.deprecated_function. "
            "It will be removed in the next feature release.",
        )

    def test_warning_is_attributed_to_caller(self):
        with self.assertWarns(DeprecationWarning) as cm:
            deprecated_function(1)

        self.assertEqual(cm.filename, __file__)

    def test_warning_is_logged(self):
        with self.assertLogs("arches.app.utils.deprecation", level="WARNING") as cm:
            with self.assertWarns(DeprecationWarning):
                deprecated_function(1)

        self.assertEqual(len(cm.records), 1)
        self.assertIn("next feature release", cm.records[0].getMessage())

    def test_method_warning_includes_class_name(self):
        holder = DeprecatedMethodHolder()
        with self.assertWarns(DeprecationWarning) as cm:
            self.assertIs(holder.deprecated_method(), holder)

        self.assertIn("DeprecatedMethodHolder.deprecated_method", str(cm.warning))

    def test_metadata_is_preserved(self):
        self.assertEqual(deprecated_function.__name__, "deprecated_function")
        self.assertEqual(deprecated_function.__doc__, "Adds two numbers.")
        self.assertTrue(hasattr(deprecated_function, "__wrapped__"))
