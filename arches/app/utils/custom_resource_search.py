from arches.app.search.elasticsearch_dsl_builder import Bool, Match, Nested


class CustomResourceSearchValue:
    custom_search_path = "custom_values"

    def __init__(self):
        pass

    @staticmethod
    def add_search_terms(resourceinstance, document, terms):
        document[CustomResourceSearchValue.custom_search_path].append(
            {"custom_value": "business-specific search value"})

    @staticmethod
    def add_search_filter(search_query, term):

        # Move the "must" part of the query to "should" so the custom document can be searched on as well
        search_query.dsl["bool"]["should"] = search_query.dsl["bool"]["must"]
        search_query.dsl["bool"]["must"] = []
        search_query.dsl["bool"]["minimum_should_match"] = 1

        document_key = CustomResourceSearchValue.custom_search_path
        custom_filter = Bool()
        custom_filter.should(Match(field="%s.custom_value" % document_key, query=term["value"], type="phrase_prefix"))
        custom_filter.should(
            Match(field="%s.custom_value.folded" % document_key, query=term["value"], type="phrase_prefix"))
        nested_custom_filter = Nested(path=document_key, query=custom_filter)
        # return nested_custom_filter
        if term["inverted"]:
            search_query.must_not(nested_custom_filter)
        else:
            search_query.should(nested_custom_filter)

    @staticmethod
    def get_custom_search_config():
        return {"type": "nested",
                "properties": {
                    "custom_value": {"type": "text",
                                     "fields": {
                                         "raw": {"type": "keyword", "ignore_above": 256},
                                         "folded": {"type": "text", "analyzer": "folding"}
                                     },
                                     }
                }
                }
