from arches.app.models.concept import get_preflabel_from_conceptid
from arches.app.models.system_settings import settings
from arches.app.search.elasticsearch_dsl_builder import (
    Bool,
    Match,
    Query,
    Term,
    MaxAgg,
    Aggregation,
)
from arches.app.search.search_engine_factory import SearchEngineFactory


class ConceptSearch(object):

    @staticmethod
    def search_terms(search_string, lang, user, term_search_type):
        se = SearchEngineFactory().create()
        query = Query(se, start=0, limit=0)
        boolquery = Bool()

        if lang != "*":
            boolquery.must(Term(field="language", term=lang))

        boolquery.should(
            Match(field="value", query=search_string.lower(), type="phrase_prefix")
        )
        boolquery.should(
            Match(
                field="value.folded", query=search_string.lower(), type="phrase_prefix"
            )
        )
        boolquery.should(
            Match(
                field="value.folded",
                query=search_string.lower(),
                fuzziness="AUTO",
                prefix_length=settings.SEARCH_TERM_SENSITIVITY,
            )
        )

        query.add_query(boolquery)
        base_agg = Aggregation(
            name="value_agg",
            type="terms",
            field="value.raw",
            size=settings.SEARCH_DROPDOWN_LENGTH,
            order={"max_score": "desc"},
        )
        top_concept_agg = Aggregation(
            name="top_concept", type="terms", field="top_concept"
        )
        conceptid_agg = Aggregation(name="conceptid", type="terms", field="conceptid")
        max_score_agg = MaxAgg(name="max_score", script="_score")

        top_concept_agg.add_aggregation(conceptid_agg)
        base_agg.add_aggregation(max_score_agg)
        base_agg.add_aggregation(top_concept_agg)
        query.add_aggregation(base_agg)

        ret = []
        results = query.search(index=term_search_type["key"])
        index = 0
        if results is not None:
            for result in results["aggregations"]["value_agg"]["buckets"]:
                if len(result["top_concept"]["buckets"]) > 0:
                    for top_concept in result["top_concept"]["buckets"]:
                        top_concept_id = top_concept["key"]
                        top_concept_label = get_preflabel_from_conceptid(
                            top_concept["key"], lang=lang if lang != "*" else None
                        )["value"]
                        for concept in top_concept["conceptid"]["buckets"]:
                            ret.append(
                                {
                                    "type": "concept",
                                    "context": top_concept_id,
                                    "context_label": top_concept_label,
                                    "id": f'{term_search_type["key"]}{index}',
                                    "text": result["key"],
                                    "value": concept["key"],
                                }
                            )
                        index += 1
        return ret
