from django.utils.translation import ugettext as _
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.models.system_settings import settings
from arches.app.utils import import_class_from_string


class BaseIndex(object):
    def __init__(self, index_name=None):
        if index_name is None or index_name is '':
            raise SearchIndexError('Index name is not defined')

        self.se = SearchEngineFactory().create()
        self.index_metadata = None
        self.index_name = index_name

    def prepare_index(self):
        if self.index_metadata is not None:
            self.se.create_index(index=self.index_name, body=self.index_metadata)
        else:
            raise SearchIndexError('No index metadata defined.')

    def index_document(self, resourceinstance, tiles):
        raise NotImplementedError

    def bulk_index(self, *args, **kwargs):
        raise NotImplementedError

    def delete_index(self, *args, **kwargs):
        self.se.delete_index(index=self.index_name)


def get_index(name):
    for index in settings.ELASTICSEARCH_CUSTOM_INDEXES:
        if index['name'] == name:
            return import_class_from_string(index['module'])(name)
    raise SearchIndexNotDefinedError(name=name)


class SearchIndexError(Exception):
    def __init__(self, message, code=None):
        self.title = _('Search Index Error:')
        self.message = message
        self.code = code

    def __str__(self):
        return repr(self.message)

class SearchIndexNotDefinedError(Exception):
    def __init__(self, name=None):
        self.title = _('Search Index Not Defined Error:')
        self.message = _('The index "%s" is not defined in settings.ELASTICSEARCH_CUSTOM_INDEXES' % name)

    def __str__(self):
        return repr(self.message)
