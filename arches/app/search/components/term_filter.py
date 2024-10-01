import re
import uuid
from arches.app.models.concept import Concept
from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.search.elasticsearch_dsl_builder import (
    Bool,
    Ids,
    Match,
    Nested,
    SimpleQueryString,
    QueryString,
    Terms,
    Term,
)
from arches.app.search.components.base import BaseSearchFilter
from arches.app.search.es_mapping_modifier import EsMappingModifierFactory

details = {
    "searchcomponentid": "",
    "name": "Term Filter",
    "icon": "",
    "modulename": "term_filter.py",
    "classname": "TermFilter",
    "type": "term-filter-type",
    "componentpath": "views/components/search/term-filter",
    "componentname": "term-filter",
    "config": {},
}


class TermFilter(BaseSearchFilter):
    def append_dsl(self, search_query_object, **kwargs):
        permitted_nodegroups = kwargs.get("permitted_nodegroups")
        include_provisional = kwargs.get("include_provisional")
        search_query = Bool()
        querystring_params = kwargs.get("querystring", "[]")
        language = self.request.GET.get("language", "*")
        for term in JSONDeserializer().deserialize(querystring_params):
            if term["type"] == "term" or term["type"] == "string":
                string_filter = Bool()
                if term["type"] == "term":
                    string_filter.must(
                        Match(
                            field="strings.string", query=term["value"], type="phrase"
                        )
                    )
                    if term.get("nodegroupid", None):
                        string_filter.must(
                            Match(
                                field="strings.nodegroup_id", query=term["nodegroupid"]
                            )
                        )
                elif term["type"] == "string":
                    try:
                        uuid.UUID(str(term["value"]))
                        string_filter.must(Ids(ids=term["value"]))
                    except:
                        if language != "*":
                            string_filter.must(
                                Match(
                                    field="strings.language",
                                    query=language,
                                    type="phrase_prefix",
                                )
                            )
                        exact_term = re.search('"(?P<search_string>.*)"', term["value"])
                        if exact_term:
                            search_string = exact_term.group("search_string")
                            string_filter.should(
                                Term(field="strings.string.raw", term=search_string)
                            )
                        elif "?" in term["value"] or "*" in term["value"]:
                            reserved_chars = (
                                '+ - = && || > < ! ( ) { } [ ] ^ " ~ : /'.split(" ")
                            )
                            for rc in reserved_chars:
                                term["value"] = term["value"].replace(rc, f"\\{rc}")
                            string_filter.must(
                                QueryString(
                                    field="strings.string.folded",
                                    default_operator="AND",
                                    query=term["value"],
                                )
                            )
                        elif "|" in term["value"] or "+" in term["value"]:
                            string_filter.must(
                                SimpleQueryString(
                                    field="strings.string",
                                    operator="and",
                                    query=term["value"],
                                )
                            )
                        else:
                            string_filter.should(
                                Match(
                                    field="strings.string",
                                    query=term["value"],
                                    type="phrase_prefix",
                                )
                            )
                            string_filter.should(
                                Match(
                                    field="strings.string.folded",
                                    query=term["value"],
                                    type="phrase_prefix",
                                )
                            )

                if include_provisional is False:
                    string_filter.must_not(
                        Match(field="strings.provisional", query="true", type="phrase")
                    )
                elif include_provisional == "only provisional":
                    string_filter.must_not(
                        Match(field="strings.provisional", query="false", type="phrase")
                    )

                string_filter.filter(
                    Terms(field="strings.nodegroup_id", terms=permitted_nodegroups)
                )
                nested_string_filter = Nested(path="strings", query=string_filter)
                if term["inverted"]:
                    search_query.must_not(nested_string_filter)
                else:
                    search_query.must(nested_string_filter)
                    # need to set min_score because the query returns results with score 0 and those have to be removed, which I don't think it should be doing
                    search_query_object["query"].min_score("0.01")
            elif term["type"] == "concept":
                concept_ids = _get_child_concepts(term["value"])
                conceptid_filter = Bool()
                conceptid_filter.filter(
                    Terms(field="domains.conceptid", terms=concept_ids)
                )
                conceptid_filter.filter(
                    Terms(field="domains.nodegroup_id", terms=permitted_nodegroups)
                )

                if include_provisional is False:
                    conceptid_filter.must_not(
                        Match(field="domains.provisional", query="true", type="phrase")
                    )
                elif include_provisional == "only provisional":
                    conceptid_filter.must_not(
                        Match(field="domains.provisional", query="false", type="phrase")
                    )

                nested_conceptid_filter = Nested(path="domains", query=conceptid_filter)
                if term["inverted"]:
                    search_query.must_not(nested_conceptid_filter)
                else:
                    search_query.filter(nested_conceptid_filter)

            # Add additional search query if configured
            for (
                custom_search_class
            ) in EsMappingModifierFactory.get_es_mapping_modifier_classes():
                custom_search_class.add_search_filter(search_query, term)

        search_query_object["query"].add_query(search_query)


def _get_child_concepts(conceptid):
    ret = {conceptid}
    for row in Concept().get_child_concepts(conceptid, ["prefLabel"]):
        ret.add(row[0])
    return list(ret)
