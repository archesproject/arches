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
        prepare_terms_index(create=True)
        prepare_concepts_index(create=True)
        prepare_search_index(create=True)
        for index in settings.ELASTICSEARCH_CUSTOM_INDEXES:
            get_index(index["name"]).prepare_index()

        return ret

    def teardown_databases(self, old_config, **kwargs):
        delete_terms_index()
        delete_concepts_index()
        delete_search_index()
        for index in settings.ELASTICSEARCH_CUSTOM_INDEXES:
            get_index(index["name"]).delete_index()

        super().teardown_databases(old_config, **kwargs)
