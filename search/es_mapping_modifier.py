from arches.app.search.elasticsearch_dsl_builder import (
    Bool,
    Match,
    Nested,
    Terms,
)
from arches.app.search.es_mapping_modifier import EsMappingModifier

from arches_controlled_lists.models import ListItem

REFERENCES_INDEX_PATH = "references"


class ReferencesEsMappingModifier(EsMappingModifier):
    """
    Base class for creating custom sections in the Resource Instance elasticsearch document.
    """

    custom_search_path = REFERENCES_INDEX_PATH

    @staticmethod
    def add_search_filter(
        search_query, term, permitted_nodegroups, include_provisional
    ):
        if term["type"] == "reference":
            item = ListItem.objects.get(pk=term["value"])
            uris = item.get_child_uris(uris=[])
            references_filter = Bool()
            references_filter.filter(Terms(field="references.uri", terms=uris))
            references_filter.filter(
                Terms(field="references.nodegroup_id", terms=permitted_nodegroups)
            )

            if include_provisional is False:
                references_filter.must_not(
                    Match(field="references.provisional", query="true", type="phrase")
                )
            elif include_provisional == "only provisional":
                references_filter.must_not(
                    Match(field="references.provisional", query="false", type="phrase")
                )

            nested_references_filter = Nested(
                path="references", query=references_filter
            )
            if term["inverted"]:
                search_query.must_not(nested_references_filter)
            else:
                search_query.filter(nested_references_filter)

    @staticmethod
    def get_mapping_definition():
        return {
            "type": "nested",
            "properties": {
                "id": {"type": "keyword"},
                "uri": {"type": "keyword"},
                "list_id": {"type": "keyword"},
                "nodegroup_id": {"type": "keyword"},
            },
        }
