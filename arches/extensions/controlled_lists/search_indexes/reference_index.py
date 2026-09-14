from arches.app.search.base_index import BaseIndex
from arches.app.search.elasticsearch_dsl_builder import (
    Bool,
    Query,
    Term,
    Match,
    Aggregation,
    MaxAgg,
)
from arches.app.search.search_engine_factory import SearchEngineInstance
from arches.app.models.system_settings import settings

from arches_controlled_lists.models import List


class ReferenceIndex(BaseIndex):
    def __init__(self, index_name=None):
        super(ReferenceIndex, self).__init__(index_name=index_name)
        self.index_metadata = {
            "settings": {
                "analysis": {
                    "analyzer": {
                        "folding": {
                            "tokenizer": "whitespace",
                            "filter": ["lowercase", "asciifolding"],
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "item_id": {"type": "keyword"},
                    "uri": {"type": "keyword"},
                    "label_id": {"type": "keyword"},
                    "label": {
                        "analyzer": "whitespace",
                        "type": "text",
                        "fields": {
                            "raw": {"type": "keyword"},
                            "folded": {"analyzer": "folding", "type": "text"},
                        },
                    },
                    "label_type": {"type": "keyword"},
                    "language": {"type": "keyword"},
                    "list_id": {"type": "keyword"},
                    "list_name": {"type": "keyword"},
                }
            },
        }

    def get_documents_to_index(self, resourceinstance, tiles):
        return None, None

    @staticmethod
    def search_terms(
        search_string,
        lang,
        user=None,
        term_search_type="reference",
    ):
        index = settings.REFERENCES_INDEX_NAME
        i = 0
        query = Query(SearchEngineInstance, start=0, limit=0)
        boolquery = Bool()

        if lang != "*":
            boolquery.must(Term(field="language", term=lang))

        boolquery.should(
            Match(field="label", query=search_string.lower(), type="phrase_prefix")
        )
        boolquery.should(
            Match(
                field="label.folded", query=search_string.lower(), type="phrase_prefix"
            )
        )
        boolquery.should(
            Match(
                field="label.folded",
                query=search_string.lower(),
                fuzziness="AUTO",
                prefix_length=settings.SEARCH_TERM_SENSITIVITY,
            )
        )

        query.add_query(boolquery)

        base_agg = Aggregation(
            name="label_agg",
            type="terms",
            field="label.raw",
            size=settings.SEARCH_DROPDOWN_LENGTH,
            order={"max_score": "desc"},
        )
        list_name_agg = Aggregation(
            name="list_name_agg", type="terms", field="list_name"
        )
        item_id_agg = Aggregation(name="item_agg", type="terms", field="item_id")
        max_score_agg = MaxAgg(name="max_score", script="_score")

        list_name_agg.add_aggregation(item_id_agg)
        base_agg.add_aggregation(max_score_agg)
        base_agg.add_aggregation(list_name_agg)
        base_agg.add_aggregation(max_score_agg)
        query.add_aggregation(base_agg)

        term_results = []
        results = query.search(index=index)
        if results is not None:
            for result in results["aggregations"]["label_agg"]["buckets"]:
                label = result["key"]
                for list_name_agg in result["list_name_agg"]["buckets"]:
                    list_name = list_name_agg["key"]
                    for item in list_name_agg["item_agg"]["buckets"]:
                        term_results.append(
                            {
                                "type": "reference",
                                "context": "",
                                "context_label": list_name,
                                "id": f"references-{i}",
                                "text": label,
                                "value": item["key"],
                            }
                        )
                        i = i + 1
        return term_results

    def reindex(
        self,
        clear_index=True,
        batch_size=settings.BULK_IMPORT_BATCH_SIZE,
        quiet=False,
    ):
        if clear_index:
            self.delete_index()
            self.prepare_index()

        for list in List.objects.filter(searchable=True):
            list.index()
