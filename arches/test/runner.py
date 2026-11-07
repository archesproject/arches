import contextlib
import gc
import io
import re
import sys
import warnings

from django.conf import settings as django_settings
from django.test import runner as django_runner
from django.test.runner import DiscoverRunner, ParallelTestSuite

from arches.app.models.system_settings import settings
from arches.app.search.base_index import get_index
from arches.app.search.search import SearchEngine
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.mappings import (
    prepare_terms_index,
    delete_terms_index,
    prepare_concepts_index,
    delete_concepts_index,
    prepare_search_index,
    delete_search_index,
)
from arches.app.utils.context_processors import app_settings


def _prepare_search_indexes():
    prepare_terms_index(create=True)
    prepare_concepts_index(create=True)
    prepare_search_index(create=True)
    for index in settings.ELASTICSEARCH_CUSTOM_INDEXES:
        get_index(index["name"]).prepare_index()


def _worker_prefix(base_prefix, worker_id):
    return f"{base_prefix}_w{worker_id}"


def _init_parallel_worker(
    counter,
    initial_settings=None,
    serialized_contents=None,
    process_setup=None,
    process_setup_args=None,
    debug_mode=None,
    used_aliases=None,
):
    """Django's worker init, then give the worker its own ES indexes.

    Workers share one Elasticsearch, so each one gets a distinct index prefix
    (e.g. test_w1) in place of the shared one.
    """
    django_runner._init_worker(
        counter,
        initial_settings,
        serialized_contents,
        process_setup,
        process_setup_args,
        debug_mode,
        used_aliases,
    )
    if (used_aliases is not None and not used_aliases) or (
        not settings.ELASTICSEARCH_ENABLED
    ):
        return

    prefix = _worker_prefix(settings.ELASTICSEARCH_PREFIX, django_runner._worker_id)
    # arches' settings proxy wraps its own copy, separate from django.conf.settings
    settings.ELASTICSEARCH_PREFIX = prefix
    django_settings.ELASTICSEARCH_PREFIX = prefix
    # Engines created at import time (and factory defaults) captured the old prefix.
    defaults = list(SearchEngineFactory.create.__defaults__)
    defaults[1] = prefix
    SearchEngineFactory.create.__defaults__ = tuple(defaults)
    for obj in gc.get_objects():
        if isinstance(obj, SearchEngine):
            obj.prefix = prefix.lower()

    app_settings()
    with contextlib.redirect_stdout(io.StringIO()):
        _prepare_search_indexes()


class ArchesParallelTestSuite(ParallelTestSuite):
    init_worker = _init_parallel_worker


class ArchesTestRunner(DiscoverRunner):
    parallel_test_suite = ArchesParallelTestSuite

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

        # Group by message; remember one example location and how many sites.
        grouped = {}
        for w in caught:
            message = str(w.message).strip()
            first_line = message.splitlines()[0] if message else ""
            entry = grouped.setdefault(
                (w.category.__name__, first_line), {"sites": set(), "example": None}
            )
            site = (w.filename, w.lineno)
            if entry["example"] is None:
                entry["example"] = site
            entry["sites"].add(site)
        if grouped:
            print(f"\nWarnings ({len(grouped)} unique):", file=sys.stderr)
            for (category, first_line), entry in grouped.items():
                filename, lineno = entry["example"]
                extra = len(entry["sites"]) - 1
                more = f" (+{extra} more locations)" if extra else ""
                print(
                    f"  {category}: {first_line} [{filename}:{lineno}]{more}",
                    file=sys.stderr,
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
            _prepare_search_indexes()

        return ret

    def teardown_databases(self, old_config, **kwargs):
        if settings.ELASTICSEARCH_ENABLED:
            with self._quiet_stdout():
                delete_terms_index()
                delete_concepts_index()
                delete_search_index()
                for index in settings.ELASTICSEARCH_CUSTOM_INDEXES:
                    get_index(index["name"]).delete_index()
            if self.parallel > 1:
                self._delete_worker_indexes()

        super().teardown_databases(old_config, **kwargs)

    def _delete_worker_indexes(self):
        es = SearchEngineFactory().create().es.options(ignore_status=[404])
        base = re.escape(settings.ELASTICSEARCH_PREFIX.lower())
        worker_index = re.compile(rf"^{base}_w\d+_")
        for name in es.indices.get(index=f"{base}_w*"):
            if worker_index.match(name):
                es.indices.delete(index=name)
