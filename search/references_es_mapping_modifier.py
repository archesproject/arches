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

    custom_search_path = REFERENCES_INDEX_PATH

    @staticmethod
    def get_mapping_property():
        return REFERENCES_INDEX_PATH

    @staticmethod
    def add_search_filter(
        search_query, term, permitted_nodegroups, include_provisional
    ):
        if term["type"] == "reference":
            item = (
                ListItem.objects.filter(pk=term["value"])
                .prefetch_related("__".join(["children"] * 10))
                .get()
            )
            uris = item.get_child_uris(uris=[])
            references_filter = Bool()
            references_filter.filter(
                Terms(field=f"{REFERENCES_INDEX_PATH}.uri", terms=uris)
            )
            references_filter.filter(
                Terms(
                    field=f"{REFERENCES_INDEX_PATH}.nodegroup_id",
                    terms=permitted_nodegroups,
                )
            )

            if include_provisional is False:
                references_filter.must_not(
                    Match(
                        field=f"{REFERENCES_INDEX_PATH}.provisional",
                        query="true",
                        type="phrase",
                    )
                )
            elif include_provisional == "only provisional":
                references_filter.must_not(
                    Match(
                        field=f"{REFERENCES_INDEX_PATH}.provisional",
                        query="false",
                        type="phrase",
                    )
                )

            nested_references_filter = Nested(
                path=REFERENCES_INDEX_PATH, query=references_filter
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
                "provisional": {"type": "boolean"},
            },
        }
