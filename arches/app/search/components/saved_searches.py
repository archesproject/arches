from arches.app.models.system_settings import settings
from arches.app.search.components.base import BaseSearchFilter

details = {
    "searchcomponentid": "",
    "name": "Saved",
    "icon": "fa fa-bookmark",
    "modulename": "saved_searches.py",
    "classname": "SavedSearches",
    "type": "saved-searches-type",
    "componentpath": "views/components/search/saved-searches",
    "componentname": "saved-searches",
    "config": {},
}


class SavedSearches(BaseSearchFilter):
    def view_data(self):
        ret = {}
        ret[self.componentname] = settings.SAVED_SEARCHES

        return ret
