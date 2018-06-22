'''
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
'''

from arches.app.utils.betterJSONSerializer import JSONSerializer
from arches.app.search.search_engine_factory import SearchEngineFactory

def prepare_term_index(create=False):
    """
    Creates the settings and mappings in Elasticsearch to support term search

    """

    index_settings = {
        'settings': {
            'analysis': {
                'analyzer': {
                    'folding': {
                        'tokenizer': 'standard',
                        'filter': [ 'lowercase', 'asciifolding' ]
                    }
                }
            }
        },
        'mappings': {
            'term': {
                'properties': {
                    'nodegroupid': {'type': 'keyword'},
                    'tileid': {'type': 'keyword'},
                    'nodeid': {'type': 'keyword'},
                    'resourceinstanceid': {'type': 'keyword'},
                    'provisional': {'type': 'boolean'},
                    'value': {
                        'analyzer': 'standard',
                        'type': 'text',
                        'fields': {
                            'raw': {'type': 'keyword'},
                            'folded': {
                                'analyzer': 'folding',
                                'type': 'text'
                            }
                        }
                    }
                }
            },
            'concept': {
                'properties': {
                    'top_concept': {'type': 'keyword'},
                    'conceptid': {'type': 'keyword'},
                    'language': {'type': 'keyword'},
                    'id': {'type': 'keyword'},
                    'category': {'type': 'keyword'},
                    'provisional': {'type': 'boolean'},
                    'type': {'type': 'keyword'},
                    'value': {
                        'analyzer': 'standard',
                        'type': 'text',
                        'fields': {
                            'raw': {'type': 'keyword'},
                            'folded': {
                                'analyzer': 'folding',
                                'type': 'text'
                            }
                        }
                    }
                }
            }
        }
    }

    if create:
        se = SearchEngineFactory().create()
        se.create_index(index='strings', body=index_settings)

    return index_settings

def delete_term_index():
    se = SearchEngineFactory().create()
    se.delete_index(index='strings')

def prepare_search_index(resource_model_id, create=False):
    """
    Creates the settings and mappings in Elasticsearch to support resource search

    """

    index_settings = {
        'settings': {
            'analysis': {
                'analyzer': {
                    'folding': {
                        'tokenizer': 'standard',
                        'filter':  [ 'lowercase', 'asciifolding' ]
                    }
                }
            }
        },
        'mappings': {
            resource_model_id : {
                'properties' : {
                    'graphid': {'type': 'keyword'},
                    'resourceinstanceid': {'type': 'keyword'},
                    'root_ontology_class': {'type':'keyword'},
                    'displayname': {'type': 'keyword'},
                    'displaydescription': {'type': 'keyword'},
                    'map_popup': {'type': 'keyword'},
                    'provisional_resource': {'type': 'keyword'},
                    'tiles' : {
                        'type' : 'nested',
                        'properties' : {
                            "tiles": {'enabled': False},
                            'tileid' : {'type': 'keyword'},
                            'nodegroup_id' : {'type': 'keyword'},
                            'parenttile_id' : {'type': 'keyword'},
                            'resourceinstanceid_id' : {'type': 'keyword'},
                            'provisionaledits': {'enabled': False}
                        }
                    },
                    'strings' : {
                        'type' : 'nested',
                        'properties': {
                            'string': {
                                'type' : 'text',
                                'index' : 'analyzed',
                                'fields' : {
                                    'raw' : {'type': 'keyword'},
                                    'folded': { 'type': 'text', 'analyzer': 'folding'}
                                }
                            },
                            'nodegroup_id' : {'type': 'keyword'},
                            'provisional': {'type': 'boolean'}
                        }
                    },
                    'domains' : {
                        'type' : 'nested',
                        'properties' : {
                            'value' : {
                                'type' : 'text',
                                'index' : 'analyzed',
                                'fields' : {
                                    'raw' : {'type': 'keyword'}
                                }
                            },
                            'conceptid' : {'type': 'keyword'},
                            'valueid' : {'type': 'keyword'},
                            'nodegroup_id' : {'type': 'keyword'},
                            'provisional': {'type': 'boolean'}
                        }
                    },
                    'geometries' : {
                        'type' : 'nested',
                        'properties': {
                            'geom': {
                                'properties': {
                                    'features': {
                                        'properties': {
                                            'geometry': {'type': 'geo_shape'},
                                            'id': {'type': 'keyword'},
                                            'type': {'type': 'keyword'},
                                            'properties': {
                                                 'enabled': False
                                            }
                                        }
                                    },
                                    'type': {'type': 'keyword'}
                                }
                            },
                            'nodegroup_id' : {'type': 'keyword'},
                            'provisional': {'type': 'boolean'}
                        }
                    },
                    'points': {
                        'type' : 'nested',
                        'properties' : {
                            'point' : {'type': 'geo_point'},
                            'nodegroup_id' : {'type': 'keyword'},
                            'provisional': {'type': 'boolean'}
                        }
                    },
                    'dates' : {
                        'type' : 'nested',
                        'properties' : {
                            'date' : {'type': 'float'},
                            'nodegroup_id' : {'type': 'keyword'},
                            'nodeid' : {'type': 'keyword'},
                            'provisional': {'type': 'boolean'}
                        }
                    },
                    'numbers' : {
                        'type' : 'nested',
                        'properties' : {
                            'number' : {'type': 'double'},
                            'nodegroup_id' : {'type': 'keyword'},
                            'provisional': {'type': 'boolean'}
                        }
                    },
                    'date_ranges': {
                        'type' : 'nested',
                        'properties' : {
                            'date_range' : {'type': 'float_range'},
                            'nodegroup_id' : {'type': 'keyword'},
                            'provisional': {'type': 'boolean'}
                        }
                    }
                }
            }
        }
    }

    if create:
        se = SearchEngineFactory().create()
        try:
            se.create_index(index='resource', body=index_settings)
        except:
            index_settings = index_settings['mappings']
            se.create_mapping(index='resource', doc_type=resource_model_id, body=index_settings)

    return index_settings


def delete_search_index():
    se = SearchEngineFactory().create()
    se.delete_index(index='resource')


def prepare_resource_relations_index(create=False):
    """
    Creates the settings and mappings in Elasticsearch to support related resources

    """

    index_settings = {
        'mappings': {
            'all': {
                'properties': {
                    'resourcexid': {'type': 'keyword'},
                    'notes': {'type': 'text'},
                    'relationshiptype': {'type': 'keyword'},
                    'resourceinstanceidfrom': {'type': 'keyword'},
                    'resourceinstanceidto': {'type': 'keyword'},
                    'created': {'type': 'keyword'},
                    'modified': {'type': 'keyword'}
                }
            }
        }
    }

    if create:
        se = SearchEngineFactory().create()
        se.create_index(index='resource_relations', body=index_settings, ignore=400)

    return index_settings

def delete_resource_relations_index():
    se = SearchEngineFactory().create()
    se.delete_index(index='resource_relations')
