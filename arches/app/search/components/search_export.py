from arches.app.search.components.base import BaseSearchFilter

details = {
    "searchcomponentid": "",
    "name": "Search Export",
    "icon": "fa fa-download",
    "modulename": "search_export.py",
    "classname": "SearchExport",
    "type": "search-export-type",
    "componentpath": "views/components/search/search-export",
    "componentname": "search-export",
    "config": {},
}


class SearchExport(BaseSearchFilter):
    def view_data(self):
        return None
