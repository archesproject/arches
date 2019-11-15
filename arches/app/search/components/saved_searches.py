from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONSerializer
from arches.app.search.components.base import BaseSearchFilter

details = {
    "searchcomponentid": "",
    "name": "Saved",
    "icon": "fa fa-bookmark",
    "modulename": "saved_searches.py",
    "classname": "SavedSearches",
    "type": "popup",
    "componentpath": "views/components/search/saved-searches",
    "componentname": "saved-searches",
    "sortorder": "2",
    "enabled": True,
}


class SavedSearches(BaseSearchFilter):
    def view_data(self):
        ret = {}
        ret["saved_searches"] = settings.SAVED_SEARCHES

        return ret
