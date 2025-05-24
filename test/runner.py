from arches.app.models.system_settings import settings
from arches.test.runner import ArchesTestRunner

from arches_controlled_lists.search_indexes.reference_index import ReferenceIndex


class ArchesControlledListsTestRunner(ArchesTestRunner):
    def setup_databases(self, **kwargs):
        ret = super().setup_databases(**kwargs)
        ReferenceIndex(index_name=settings.REFERENCES_INDEX_NAME).prepare_index()
        return ret

    def teardown_databases(self, old_config, **kwargs):
        ReferenceIndex(index_name=settings.REFERENCES_INDEX_NAME).delete_index()
        super().teardown_databases(old_config, **kwargs)
