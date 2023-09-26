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

from SPARQLWrapper import SPARQLWrapper, JSON
from arches.app.models import models
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer


class Abstract_Provider(SPARQLWrapper):
    def __init__(self, endpoint, **kwargs):
        super(Abstract_Provider, self).__init__(endpoint, **kwargs)
        self.name = "abstract_provider"
        self.allowed_languages = models.Language.objects.values_list("code", flat=True)

    def get_concepts(self, uris):
        """
        Returns a list of concepts given a list of identifiers

        """

        pass

    def search_for_concepts(self, terms):
        """
        Searches the provider for concepts that match the given terms, returns a dictionary in the following format

        {
            "head" : {
                "vars" : [ "Subject", "Term", "ScopeNote"]
            },
            "results" : {
                "bindings" : [ {
                    "Subject" : {
                        "type" : "uri",
                        "value" : "http://vocab.getty.edu/aat/300380087"
                    },
                    "Term" : {
                        "xml:lang" : "en",
                        "type" : "literal",
                        "value" : "Dryopteris (genus)"
                    },
                    "ScopeNote" : {
                        "xml:lang" : "en",
                        "type" : "literal",
                        "value" : "Genus containing about 250 species of fern. "
                    }
                }]
            }
        }


        """

        pass

    def perform_sparql_query(self, query):
        """
        Simple wrapper around the SPARQLWrapper.queryAndConvert method

        """

        self.setQuery(query)
        # print query
        return self.queryAndConvert()
