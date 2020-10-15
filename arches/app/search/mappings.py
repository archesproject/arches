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

from arches.app.models import models
from arches.app.search.search_engine_factory import SearchEngineFactory
from django.db.utils import ProgrammingError


CONCEPTS_INDEX = "concepts"
TERMS_INDEX = "terms"
RESOURCES_INDEX = "resources"
RESOURCE_RELATIONS_INDEX = "resource_relations"


def prepare_terms_index(create=False):
    """
    Creates the settings and mappings in Elasticsearch to support term search

    """

    index_settings = {
        "settings": {"analysis": {"analyzer": {"folding": {"tokenizer": "standard", "filter": ["lowercase", "asciifolding"]}}}},
        "mappings": {
            "_doc": {
                "properties": {
                    "nodegroupid": {"type": "keyword"},
                    "tileid": {"type": "keyword"},
                    "nodeid": {"type": "keyword"},
                    "resourceinstanceid": {"type": "keyword"},
                    "provisional": {"type": "boolean"},
                    "value": {
                        "analyzer": "standard",
                        "type": "text",
                        "fields": {"raw": {"type": "keyword"}, "folded": {"analyzer": "folding", "type": "text"}},
                    },
                }
            }
        },
    }

    if create:
        se = SearchEngineFactory().create()
        se.create_index(index=TERMS_INDEX, body=index_settings)

    return index_settings


def prepare_concepts_index(create=False):
    """
    Creates the settings and mappings in Elasticsearch to support term search

    """

    index_settings = {
        "settings": {"analysis": {"analyzer": {"folding": {"tokenizer": "standard", "filter": ["lowercase", "asciifolding"]}}}},
        "mappings": {
            "_doc": {
                "properties": {
                    "top_concept": {"type": "keyword"},
                    "conceptid": {"type": "keyword"},
                    "language": {"type": "keyword"},
                    "id": {"type": "keyword"},
                    "category": {"type": "keyword"},
                    "provisional": {"type": "boolean"},
                    "type": {"type": "keyword"},
                    "value": {
                        "analyzer": "standard",
                        "type": "text",
                        "fields": {"raw": {"type": "keyword"}, "folded": {"analyzer": "folding", "type": "text"}},
                    },
                }
            }
        },
    }

    if create:
        se = SearchEngineFactory().create()
        se.create_index(index=CONCEPTS_INDEX, body=index_settings)

    return index_settings


def delete_terms_index():
    se = SearchEngineFactory().create()
    se.delete_index(index=TERMS_INDEX)


def delete_concepts_index():
    se = SearchEngineFactory().create()
    se.delete_index(index=CONCEPTS_INDEX)


def prepare_search_index(create=False):
    """
    Creates the settings and mappings in Elasticsearch to support resource search

    """

    index_settings = {
        "settings": {
            "analysis": {"analyzer": {"folding": {"tokenizer": "standard", "filter": ["lowercase", "asciifolding"]}}},
            "index.mapping.total_fields.limit": 50000,
            "index.mapping.nested_objects.limit": 50000,
        },
        "mappings": {
            "_doc": {
                "properties": {
                    "graph_id": {"type": "keyword"},
                    "legacyid": {"type": "text", "fields": {"keyword": {"ignore_above": 256, "type": "keyword"}}},
                    "resourceinstanceid": {"type": "keyword"},
                    "root_ontology_class": {"type": "keyword"},
                    "displayname": {"type": "keyword"},
                    "displaydescription": {"type": "keyword"},
                    "map_popup": {"type": "keyword"},
                    "provisional_resource": {"type": "keyword"},
                    "tiles": {
                        "type": "nested",
                        "properties": {
                            "tiles": {"enabled": False},
                            "tileid": {"type": "keyword"},
                            "nodegroup_id": {"type": "keyword"},
                            "parenttile_id": {"type": "keyword"},
                            "resourceinstanceid_id": {"type": "keyword"},
                            "provisionaledits": {"enabled": False},
                            "data": {"properties": {}},
                        },
                    },
                    "permissions": {
                        "type": "nested",
                        "properties": {
                            "users_without_read_perm": {"type": "integer"},
                            "users_without_edit_perm": {"type": "integer"},
                            "users_without_delete_perm": {"type": "integer"},
                            "users_with_no_access": {"type": "integer"},
                        },
                    },
                    "strings": {
                        "type": "nested",
                        "properties": {
                            "string": {
                                "type": "text",
                                "fields": {"raw": {"type": "keyword"}, "folded": {"type": "text", "analyzer": "folding"}},
                            },
                            "nodegroup_id": {"type": "keyword"},
                            "provisional": {"type": "boolean"},
                        },
                    },
                    "ids": {
                        "type": "nested",
                        "properties": {"id": {"type": "keyword"}, "nodegroup_id": {"type": "keyword"}, "provisional": {"type": "boolean"}},
                    },
                    "domains": {
                        "type": "nested",
                        "properties": {
                            "value": {"type": "text", "fields": {"raw": {"type": "keyword"}}},
                            "conceptid": {"type": "keyword"},
                            "valueid": {"type": "keyword"},
                            "nodegroup_id": {"type": "keyword"},
                            "provisional": {"type": "boolean"},
                        },
                    },
                    "geometries": {
                        "type": "nested",
                        "properties": {
                            "geom": {
                                "properties": {
                                    "features": {
                                        "properties": {
                                            "geometry": {"type": "geo_shape"},
                                            "id": {"type": "keyword"},
                                            "type": {"type": "keyword"},
                                            "properties": {"enabled": False},
                                        }
                                    },
                                    "type": {"type": "keyword"},
                                }
                            },
                            "nodegroup_id": {"type": "keyword"},
                            "provisional": {"type": "boolean"},
                        },
                    },
                    "points": {
                        "type": "nested",
                        "properties": {
                            "point": {"type": "geo_point"},
                            "nodegroup_id": {"type": "keyword"},
                            "provisional": {"type": "boolean"},
                        },
                    },
                    "dates": {
                        "type": "nested",
                        "properties": {
                            "date": {"type": "integer"},
                            "nodegroup_id": {"type": "keyword"},
                            "nodeid": {"type": "keyword"},
                            "provisional": {"type": "boolean"},
                        },
                    },
                    "numbers": {
                        "type": "nested",
                        "properties": {
                            "number": {"type": "double"},
                            "nodegroup_id": {"type": "keyword"},
                            "provisional": {"type": "boolean"},
                        },
                    },
                    "date_ranges": {
                        "type": "nested",
                        "properties": {
                            "date_range": {"type": "integer_range"},
                            "nodegroup_id": {"type": "keyword"},
                            "provisional": {"type": "boolean"},
                        },
                    },
                }
            }
        },
    }
    try:
        from arches.app.datatypes.datatypes import DataTypeFactory
        datatype_factory = DataTypeFactory()
        data = index_settings["mappings"]["_doc"]["properties"]["tiles"]["properties"]["data"]["properties"]
        for node in models.Node.objects.all():
            datatype = datatype_factory.get_instance(node.datatype)
            datatype_mapping = datatype.default_es_mapping()
            if datatype_mapping and datatype_factory.datatypes[node.datatype].defaultwidget:
                data[str(node.nodeid)] = datatype_mapping
    except ProgrammingError:
        print("Skipping datatype mappings because the datatypes table is not yet available")

    if create:
        se = SearchEngineFactory().create()
        se.create_index(index=RESOURCES_INDEX, body=index_settings)

    return index_settings


def delete_search_index():
    se = SearchEngineFactory().create()
    se.delete_index(index=RESOURCES_INDEX)


def prepare_resource_relations_index(create=False):
    """
    Creates the settings and mappings in Elasticsearch to support related resources

    """

    index_settings = {
        "mappings": {
            "_doc": {
                "properties": {
                    "resourcexid": {"type": "keyword"},
                    "notes": {"type": "text"},
                    "relationshiptype": {"type": "keyword"},
                    "inverserelationshiptype": {"type": "keyword"},
                    "resourceinstanceidfrom": {"type": "keyword"},
                    "resourceinstancefrom_graphid": {"type": "keyword"},
                    "resourceinstanceidto": {"type": "keyword"},
                    "resourceinstanceto_graphid": {"type": "keyword"},
                    "created": {"type": "keyword"},
                    "modified": {"type": "keyword"},
                    "datestarted": {"type": "date"},
                    "dateended": {"type": "date"},
                    "tileid": {"type": "keyword"},
                    "nodeid": {"type": "keyword"},
                }
            }
        }
    }

    if create:
        se = SearchEngineFactory().create()
        se.create_index(index=RESOURCE_RELATIONS_INDEX, body=index_settings)

    return index_settings


def delete_resource_relations_index():
    se = SearchEngineFactory().create()
    se.delete_index(index=RESOURCE_RELATIONS_INDEX)
