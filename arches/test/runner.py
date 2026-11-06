import contextlib
import io
import sys
import warnings

from django.test.runner import DiscoverRunner

from arches.app.models.system_settings import settings
from arches.app.search.base_index import get_index
from arches.app.search.mappings import (
    prepare_terms_index,
    delete_terms_index,
    prepare_concepts_index,
    delete_concepts_index,
    prepare_search_index,
    delete_search_index,
)
from arches.app.utils.context_processors import app_settings


class ArchesTestRunner(DiscoverRunner):
    def __init__(self, *args, **kwargs) -> None:
        kwargs["debug_mode"] = True
        # Unless the user has something other than the Django default, give them
        # what they probably want.
        if kwargs["pattern"] == "test*.py":
            kwargs["pattern"] = "*.py"
        super().__init__(*args, **kwargs)

    def run_suite(self, suite, **kwargs):
        if not self.buffer:
            return super().run_suite(suite, **kwargs)

        # --buffer discards warnings printed during tests, so collect them.
        with warnings.catch_warnings(record=True) as caught:
            result = super().run_suite(suite, **kwargs)

        unique = {}
        for w in caught:
            key = (w.category.__name__, str(w.message), w.filename, w.lineno)
            unique.setdefault(key, w)
        if unique:
            print(f"\nWarnings ({len(unique)} unique):", file=sys.stderr)
            for category, message, filename, lineno in unique:
                first_line = message.strip().splitlines()[0] if message.strip() else ""
                print(
                    f"  {filename}:{lineno}: {category}: {first_line}", file=sys.stderr
                )
        return result

    def _quiet_stdout(self):
        if self.verbosity < 2:
            return contextlib.redirect_stdout(io.StringIO())
        return contextlib.nullcontext()

    def setup_databases(self, **kwargs):
        """Override DiscoverRunner's setup_databases() hook."""
        ret = super().setup_databases(**kwargs)

        # If the collected tests don't involve the database,
        # e.g. subclasses of SimpleTestCase, then "aliases" will
        # test false. Return early before attempting to setup
        # something that doesn't exist.
        if not kwargs.get("aliases"):
            return ret

        app_settings()  # adds languages to system
        if not settings.ELASTICSEARCH_ENABLED:
            return ret

        with self._quiet_stdout():
            prepare_terms_index(create=True)
            prepare_concepts_index(create=True)
            prepare_search_index(create=True)
            for index in settings.ELASTICSEARCH_CUSTOM_INDEXES:
                get_index(index["name"]).prepare_index()

        return ret

    def teardown_databases(self, old_config, **kwargs):
        if settings.ELASTICSEARCH_ENABLED:
            with self._quiet_stdout():
                delete_terms_index()
                delete_concepts_index()
                delete_search_index()
                for index in settings.ELASTICSEARCH_CUSTOM_INDEXES:
                    get_index(index["name"]).delete_index()

        super().teardown_databases(old_config, **kwargs)
