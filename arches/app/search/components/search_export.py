from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONSerializer
from arches.app.search.components.base import BaseSearchFilter

details = {
    "searchcomponentid": "",
    "name": "Search Export",
    "icon": "fa fa-download",
    "modulename": "search_export.py",
    "classname": "SearchExport",
    "type": "popup",
    "componentpath": "views/components/search/search-export",
    "componentname": "search-export",
    "sortorder": "3",
    "enabled": True,
}


class SearchExport(BaseSearchFilter):
    def view_data(self):
        return None
