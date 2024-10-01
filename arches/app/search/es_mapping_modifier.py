from arches.app.models.system_settings import settings
from arches.app.utils import import_class_from_string


class EsMappingModifierFactory:
    def __init__(self):
        pass

    @staticmethod
    def get_es_mapping_modifier_classes():
        return (
            [
                import_class_from_string(classname)
                for classname in settings.ES_MAPPING_MODIFIER_CLASSES
            ]
            if settings.setting_exists("ES_MAPPING_MODIFIER_CLASSES")
            and settings.ES_MAPPING_MODIFIER_CLASSES
            else []
        )


class EsMappingModifier:
    """
    Base class for creating custom sections in the Resource Instance elasticsearch document.
    """

    custom_search_path = "custom_values"

    def __init__(self):
        pass

    @staticmethod
    def get_mapping_property():
        """
        Identifies the document key where the custom ES document section is located.

        :return: ES document key
        :rtype String
        """
        return EsMappingModifier.custom_search_path

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
    def get_mapping_definition():
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
