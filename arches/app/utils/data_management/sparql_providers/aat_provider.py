"""
ARCHES - a program developed to inventory and manage immovable cultural heritage.
Copyright (C) 2013 J. Paul Getty Trust and World Monuments Fund

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import urllib.request, urllib.error, urllib.parse
from django.utils.translation import gettext as _
from arches.app.models.models import DValueType
from arches.app.models.concept import Concept, ConceptValue
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from SPARQLWrapper import SPARQLWrapper, JSON
from .abstract_provider import Abstract_Provider
from rdflib.namespace import SKOS, DCTERMS


class AAT_Provider(Abstract_Provider):
    def __init__(self, **kwargs):
        super(AAT_Provider, self).__init__(
            "http://vocab.getty.edu/sparql.json", **kwargs
        )

        self.name = _("Getty AAT")
        self.setReturnFormat(JSON)

    def get_concepts(self, uris):
        """
        Get a list of concepts given a list of AAT uris like http://vocab.getty.edu/aat/300380087

        """

        default_lang = settings.LANGUAGE_CODE
        dcterms_identifier_type = DValueType.objects.get(
            valuetype=str(DCTERMS.identifier).replace(str(DCTERMS), ""),
            namespace="dcterms",
        )

        concepts = []
        langs = []
        for lang in self.allowed_languages:
            # the AAT expects language codes to be all lower case
            langs.append('"%s"' % (lang.lower()))
        for uri in uris.split(","):
            query = """
                SELECT ?value ?type WHERE {
                  {
                    <%s> skos:prefLabel ?value .
                    BIND('prefLabel' AS ?type)
                  }
                  UNION
                  {
                    <%s> skos:scopeNote [rdf:value ?value] .
                    BIND('scopeNote' AS ?type)
                  }
                  FILTER (lang(?value) in (%s)) 
                }""" % (
                uri,
                uri,
                ",".join(langs),
            )
            results = self.perform_sparql_query(query)

            if len(results["results"]["bindings"]) > 0:
                concept = Concept()
                concept.nodetype = "Concept"
                for result in results["results"]["bindings"]:
                    concept.addvalue(
                        {
                            "type": result["type"]["value"],
                            "value": result["value"]["value"],
                            "language": result["value"]["xml:lang"],
                        }
                    )
                concept.addvalue(
                    {
                        "value": uri,
                        "language": settings.LANGUAGE_CODE,
                        "type": dcterms_identifier_type.valuetype,
                        "category": dcterms_identifier_type.category,
                    }
                )
                concepts.append(concept)
            else:
                raise Exception(
                    _(
                        "<strong>Error in SPARQL query:</strong><br>Test this query directly by pasting the query below into the Getty's \
                        own SPARQL endpoint at <a href='http://vocab.getty.edu/sparql' target='_blank'>http://vocab.getty.edu/sparql</a> \
                        <i><pre>%s</pre></i>Query returned 0 results, please check the query for errors.  \
                        You may need to add the appropriate languages into the database for this query to work<br><br>"
                    )
                    % (query.replace("<", "&lt").replace(">", "&gt"))
                )

        return concepts

    def search_for_concepts(self, terms):
        query = """PREFIX dct: <http://purl.org/dc/terms/>
            PREFIX gvp: <http://vocab.getty.edu/ontology#>
            PREFIX gvp_lang: <http://vocab.getty.edu/language/>
            PREFIX luc: <http://www.ontotext.com/owlim/lucene#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX skosxl: <http://www.w3.org/2008/05/skos-xl#>
            SELECT ?Subject ?Term ?ScopeNote {
                ?Subject luc:term '%s*'; a skos:Concept; skos:inScheme aat:.
                #?Subject rdf:type c.
                #?typ rdfs:subClassOf gvp:Subject; rdfs:label ?Type.
                optional {?Subject (gvp:prefLabelGVP | skos:prefLabel) [skosxl:literalForm ?Term]}
                #optional {?Subject gvp:parentStringAbbrev ?Parents}
                optional {?Subject skos:scopeNote [dct:language gvp_lang:en; rdf:value ?ScopeNote]}}""" % (
            terms
        )

        results = self.perform_sparql_query(query)
        return results

    def perform_sparql_query(self, query):
        self.setQuery(query)

        # print query
        # return HttpResponse(self.endpoint + '?' + self._getRequestEncodedParameters(("query", self.queryString)))

        req = urllib.request.Request(
            self.endpoint
            + "?"
            + self._getRequestEncodedParameters(("query", self.queryString))
        )
        req.add_header("Accept", "application/sparql-results+json")
        f = urllib.request.urlopen(req)
        return JSONDeserializer().deserialize(f.read())
