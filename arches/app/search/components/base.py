
details = {
    "searchcomponentid": "",  # leave blank for the system to generate a uuid
    "name": "",  # the name that shows up in the UI
    "icon": "",  # the icon class to use
    "modulename": "base.py",  # the name of this file
    "classname": "BaseSearchFilter",  # the classname below",
    "type": "filter",  # 'filter' if you want the component to show up dynamically
    "componentpath": "views/components/search/...",  # path to ko component
    "componentname": "advanced-search",  # lowercase unique name
    "config": {},  # config values to pass to the component
    "sortorder": "0",  # order in which to display dynamically added filters to the UI
    "enabled": True  # True to enable in the system
}


class BaseSearchFilter():

    def append_dsl(self, querysting_params, query_dsl, permitted_nodegroups, include_provisional):
        """
        used to append ES query dsl to the search request

        """

        pass

    def view_data(self):
        """
        data that the view should gather to pass to the front end

        """

        pass
