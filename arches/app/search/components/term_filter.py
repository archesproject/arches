from arches.app.models.concept import Concept
from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.search.elasticsearch_dsl_builder import Bool, Match, Nested, Terms
from arches.app.search.components.base import BaseSearchFilter

details = {
    "searchcomponentid": "",
    "name": "Term Filter",
    "icon": "",
    "modulename": "term_filter.py",
    "classname": "TermFilter",
    "type": "text-input",
    "componentpath": "views/components/search/term-filter",
    "componentname": "term-filter",
    "sortorder": "0",
    "enabled": True,
}


class TermFilter(BaseSearchFilter):
    def append_dsl(self, search_results_object, permitted_nodegroups, include_provisional):
        search_query = Bool()
        querysting_params = self.request.GET.get(details["componentname"], "")
        for term in JSONDeserializer().deserialize(querysting_params):
            if term["type"] == "term" or term["type"] == "string":
                string_filter = Bool()
                if term["type"] == "term":
                    string_filter.must(Match(field="strings.string", query=term["value"], type="phrase"))
                elif term["type"] == "string":
                    string_filter.should(Match(field="strings.string", query=term["value"], type="phrase_prefix"))
                    string_filter.should(Match(field="strings.string.folded", query=term["value"], type="phrase_prefix"))

                if include_provisional is False:
                    string_filter.must_not(Match(field="strings.provisional", query="true", type="phrase"))
                elif include_provisional == "only provisional":
                    string_filter.must_not(Match(field="strings.provisional", query="false", type="phrase"))

                string_filter.filter(Terms(field="strings.nodegroup_id", terms=permitted_nodegroups))
                nested_string_filter = Nested(path="strings", query=string_filter)
                if term["inverted"]:
                    search_query.must_not(nested_string_filter)
                else:
                    search_query.must(nested_string_filter)
                    # need to set min_score because the query returns results with score 0 and those have to be removed, which I don't think it should be doing
                    search_results_object["query"].min_score("0.01")
            elif term["type"] == "concept":
                concept_ids = _get_child_concepts(term["value"])
                conceptid_filter = Bool()
                conceptid_filter.filter(Terms(field="domains.conceptid", terms=concept_ids))
                conceptid_filter.filter(Terms(field="domains.nodegroup_id", terms=permitted_nodegroups))

                if include_provisional is False:
                    conceptid_filter.must_not(Match(field="domains.provisional", query="true", type="phrase"))
                elif include_provisional == "only provisional":
                    conceptid_filter.must_not(Match(field="domains.provisional", query="false", type="phrase"))

                nested_conceptid_filter = Nested(path="domains", query=conceptid_filter)
                if term["inverted"]:
                    search_query.must_not(nested_conceptid_filter)
                else:
                    search_query.filter(nested_conceptid_filter)

        search_results_object["query"].add_query(search_query)


def _get_child_concepts(conceptid):
    ret = {conceptid}
    for row in Concept().get_child_concepts(conceptid, ["prefLabel"]):
        ret.add(row[0])
    return list(ret)
