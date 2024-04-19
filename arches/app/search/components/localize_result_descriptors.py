from arches.app.models.system_settings import settings
from arches.app.search.components.base import BaseSearchFilter
from django.utils.translation import get_language, gettext as _

details = {
    "searchcomponentid": "ada062d9-092d-400c-bcf7-94a931d1f271",
    "name": "Localize Result Descriptors",
    "icon": "",
    "modulename": "localize_result_descriptors.py",
    "classname": "LocalizeResultDescriptors",
    "type": "",
    "componentpath": "",
    "componentname": "localize-descriptors",
    "sortorder": "0",
    "enabled": True,
}

class LocalizeResultDescriptors(BaseSearchFilter):
    def view_data(self):
        pass

    def post_search_hook(self, search_results_object, response_object, permitted_nodegroups, request):
        
        def get_localized_descriptor(resource, descriptor_type, language_codes):
            descriptor = resource["_source"][descriptor_type]
            result = descriptor[0] if len(descriptor) > 0 else None
            for language_code in language_codes:
                for entry in descriptor:
                    if entry["language"] == language_code and entry["value"] != "":
                        return entry
            return result
        
        descriptor_types = ("displaydescription", "displayname")
        active_and_default_language_codes = (get_language(), settings.LANGUAGE_CODE)

        for resource in response_object["results"]["hits"]["hits"]:
            for descriptor_type in descriptor_types:
                descriptor = get_localized_descriptor(resource, descriptor_type, active_and_default_language_codes)
                if descriptor:
                    resource["_source"][descriptor_type] = descriptor["value"]
                    if descriptor_type == "displayname":
                        resource["_source"]["displayname_language"] = descriptor["language"]
                else:
                    resource["_source"][descriptor_type] = _("Undefined")
