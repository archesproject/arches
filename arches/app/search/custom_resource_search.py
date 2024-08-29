from arches.app.models.system_settings import settings
from arches.app.utils import import_class_from_string


class CustomResourceSearchFactory:
    def __init__(self):
        pass

    @staticmethod
    def get_custom_search_classes():
        return (
            [
                import_class_from_string(classname)
                for classname in settings.CUSTOM_SEARCH_CLASSES
            ]
            if settings.setting_exists("CUSTOM_SEARCH_CLASSES")
            and settings.CUSTOM_SEARCH_CLASSES
            else []
        )


class CustomResourceSearch:
    """
    Base class for creating custom sections in the Resource Instance elasticsearch document.
    """

    custom_search_path = "custom_values"

    def __init__(self):
        pass

    @staticmethod
    def get_custom_search_path():
        """
        Identifies the document key where the custom ES document section is located.

        :return: ES document key
        :rtype String
        """
        return CustomResourceSearch.custom_search_path

    @staticmethod
    def add_search_terms(resourceinstance, document, terms):
        """
        Adds the custom ES search document section for the resource instance.
        :param resourceinstance: resource instance being indexed
        :param document: Original ES document for the Resource Instance
        :param terms: ES terms in the document
        """
        pass

    @staticmethod
    def add_search_filter(search_query, term):
        """
        Adds to or modifies the term search_query to include the custom search document section as part of the search
        :param search_query: The original search term query
        :param term: The search term
        """
        pass

    @staticmethod
    def get_custom_search_config():
        """
        Defines the ES structure of the custom search document section. Called when the initial ES resources index is created.

        :return: dict of the custom document section
        :rtype dict
        """
        return {
            "type": "nested",
            "properties": {
                "custom_value": {
                    "type": "text",
                    "fields": {
                        "raw": {"type": "keyword", "ignore_above": 256},
                        "folded": {"type": "text", "analyzer": "folding"},
                    },
                }
            },
        }
