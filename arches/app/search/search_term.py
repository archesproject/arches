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
    get_nodegroups_by_perm,
)


class SearchTerm(object):
    def __init__(self, value=None, lang=None):
        self.value = value
        self.lang = lang if lang is not None else get_language()


class TermSearch(object):

    @staticmethod
    def search_terms(search_string, lang, user, term_search_type):
        se = SearchEngineFactory().create()
        user_is_reviewer = user_is_resource_reviewer(user)
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

        permitted_nodegroups = get_nodegroups_by_perm(user, "models.read_nodegroup")
        boolquery.filter(
            Terms(field="nodegroupid", terms=[str(ng) for ng in permitted_nodegroups])
        )
        if user_is_reviewer is False:
            boolquery.filter(Terms(field="provisional", terms=["false"]))

        query.add_query(boolquery)
        base_agg = Aggregation(
            name="value_agg",
            type="terms",
            field="value.raw",
            size=settings.SEARCH_DROPDOWN_LENGTH,
            order={"max_score": "desc"},
        )
        nodegroupid_agg = Aggregation(
            name="nodegroupid", type="terms", field="nodegroupid"
        )
        max_score_agg = MaxAgg(name="max_score", script="_score")

        base_agg.add_aggregation(max_score_agg)
        base_agg.add_aggregation(nodegroupid_agg)
        query.add_aggregation(base_agg)

        ret = []
        results = query.search(index=term_search_type["key"])
        if results is not None:
            for index, result in enumerate(
                results["aggregations"]["value_agg"]["buckets"]
            ):
                ret.append(
                    {
                        "type": "term",
                        "context": "",
                        "context_label": get_resource_model_label(result),
                        "id": f'{term_search_type["key"]}{index}',
                        "text": result["key"],
                        "value": result["key"],
                        "nodegroupid": result["nodegroupid"]["buckets"][0]["key"],
                    }
                )
        return ret


def get_resource_model_label(result):
    if len(result["nodegroupid"]["buckets"]) > 0:
        nodegroup = result["nodegroupid"]["buckets"][0]
        nodegroup_id = nodegroup["key"]
        node = Node.objects.select_related("graph").get(nodeid=nodegroup_id)
        graph = node.graph
        return f"{graph.name} - {node.name}"
    return ""
