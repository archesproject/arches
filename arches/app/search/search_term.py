from django.utils.translation import get_language

from arches.app.models.concept import get_preflabel_from_conceptid
from arches.app.models.models import Node
from arches.app.models.system_settings import settings
from arches.app.search.elasticsearch_dsl_builder import (
    Bool,
    Match,
    Query,
    Term,
    Terms,
    MaxAgg,
    Aggregation,
)
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.utils.permission_backend import (
    user_is_resource_reviewer,
)


class SearchTerm(object):
    def __init__(self, value=None, lang=None):
        self.value = value
        self.lang = lang if lang is not None else get_language()


class ConceptSearch(object):

    @staticmethod
    def search_terms(search_string, lang, user, term_search_type):
        return searchES(
            index=term_search_type["key"],
            searchString=search_string,
            lang=lang,
            user=user,
        )


class TermSearch(object):

    @staticmethod
    def search_terms(search_string, lang, user, term_search_type):
        return searchES(
            index=term_search_type["key"],
            searchString=search_string,
            lang=lang,
            user=user,
        )


def searchES(index, searchString, lang, user):
    i = 0
    se = SearchEngineFactory().create()
    user_is_reviewer = user_is_resource_reviewer(user)
    query = Query(se, start=0, limit=0)
    boolquery = Bool()

    if lang != "*":
        boolquery.must(Term(field="language", term=lang))

    boolquery.should(
        Match(field="value", query=searchString.lower(), type="phrase_prefix")
    )
    boolquery.should(
        Match(field="value.folded", query=searchString.lower(), type="phrase_prefix")
    )
    boolquery.should(
        Match(
            field="value.folded",
            query=searchString.lower(),
            fuzziness="AUTO",
            prefix_length=settings.SEARCH_TERM_SENSITIVITY,
        )
    )
    boolquery.should(
        Match(field="displayname.value", query=searchString, fuzziness=2, boost=2)
    )

    if user_is_reviewer is False and index == "terms":
        boolquery.filter(Terms(field="provisional", terms=["false"]))

    query.add_query(boolquery)
    base_agg = Aggregation(
        name="value_agg",
        type="terms",
        field="value.raw",
        size=settings.SEARCH_DROPDOWN_LENGTH,
        order={"max_score": "desc"},
    )
    nodegroupid_agg = Aggregation(name="nodegroupid", type="terms", field="nodegroupid")
    top_concept_agg = Aggregation(name="top_concept", type="terms", field="top_concept")
    conceptid_agg = Aggregation(name="conceptid", type="terms", field="conceptid")
    max_score_agg = MaxAgg(name="max_score", script="_score")

    top_concept_agg.add_aggregation(conceptid_agg)
    base_agg.add_aggregation(max_score_agg)
    base_agg.add_aggregation(top_concept_agg)
    base_agg.add_aggregation(nodegroupid_agg)
    query.add_aggregation(base_agg)

    ret = []
    results = query.search(index=index)
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
                                "id": index + str(i),
                                "text": result["key"],
                                "value": concept["key"],
                            }
                        )
                    i = i + 1
            else:
                ret.append(
                    {
                        "type": "term",
                        "context": "",
                        "context_label": get_resource_model_label(result),
                        "id": index + str(i),
                        "text": result["key"],
                        "value": result["key"],
                        "nodegroupid": result["nodegroupid"]["buckets"][0]["key"],
                    }
                )
                i = i + 1
    return ret


def get_resource_model_label(result):
    if len(result["nodegroupid"]["buckets"]) > 0:
        for nodegroup in result["nodegroupid"]["buckets"]:
            nodegroup_id = nodegroup["key"]
            node = Node.objects.get(nodeid=nodegroup_id)
            graph = node.graph
        return "{0} - {1}".format(graph.name, node.name)
    else:
        return ""
