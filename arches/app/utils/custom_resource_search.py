from arches.app.search.elasticsearch_dsl_builder import Bool, Match, Nested


class CustomResourceSearchValue:
    custom_search_path = "custom_value"

    def __init__(self):
        pass

    @staticmethod
    def add_search_terms(resourceinstance, document, terms):
        if CustomResourceSearchValue.custom_search_path not in document:
            document[CustomResourceSearchValue.custom_search_path] = []

        document[CustomResourceSearchValue.custom_search_path].append(
            {"custom_value": "business-specific search value"}
        )

    def create_nested_custom_filter(term, original_element):
        if "nested" not in original_element:
            return original_element
        # print("Original element: %s" % original_element)
        document_key = CustomResourceSearchValue.custom_search_path
        custom_filter = Bool()
        custom_filter.should(
            Match(
                field="%s.custom_value" % document_key,
                query=term["value"],
                type="phrase_prefix",
            )
        )
        custom_filter.should(
            Match(
                field="%s.custom_value.folded" % document_key,
                query=term["value"],
                type="phrase_prefix",
            )
        )
        nested_custom_filter = Nested(path=document_key, query=custom_filter)
        new_must_element = Bool()
        new_must_element.should(original_element)
        new_must_element.should(nested_custom_filter)
        new_must_element.dsl["bool"]["minimum_should_match"] = 1
        return new_must_element

    @staticmethod
    def add_search_filter(search_query, term):
        # print("Search query before: %s" % search_query)
        original_must_filter = search_query.dsl["bool"]["must"]
        search_query.dsl["bool"]["must"] = []
        for must_element in original_must_filter:
            search_query.must(CustomResourceSearchValue.create_nested_custom_filter(term, must_element))

        original_must_filter = search_query.dsl["bool"]["must_not"]
        search_query.dsl["bool"]["must_not"] = []
        for must_element in original_must_filter:
            search_query.must_not(CustomResourceSearchValue.create_nested_custom_filter(term, must_element))
        # print("Search query after: %s" % search_query)

    @staticmethod
    def get_custom_search_config():
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
