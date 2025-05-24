from arches.app.models.system_settings import settings
from arches.app.search.base_index import get_index
from arches.test.runner import ArchesTestRunner


class ArchesControlledListsTestRunner(ArchesTestRunner):
    def setup_databases(self, **kwargs):
        ret = super().setup_databases(**kwargs)

        for index in settings.ELASTICSEARCH_CUSTOM_INDEXES:
            get_index(index["name"]).prepare_index()

        return ret

    def teardown_databases(self, old_config, **kwargs):
        super().teardown_databases(old_config, **kwargs)

        for index in settings.ELASTICSEARCH_CUSTOM_INDEXES:
            get_index(index["name"]).delete_index()
