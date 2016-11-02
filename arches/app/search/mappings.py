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

from arches.app.search.search_engine_factory import SearchEngineFactory

def prepare_term_index(create=False):
    """
    Creates the settings and mappings in Elasticsearch to support term search

    """

    index_settings = {
        'settings':{
            'analysis': {
                'analyzer': {
                    'folding': {
                        'tokenizer': 'standard',
                        'filter':  [ 'lowercase', 'asciifolding' ]
                    }
                }
            }
        },
        'mappings':{
            'value':{
                'properties': {
                    'ids':{'type': 'string', 'index' : 'not_analyzed'},
                    'context':{'type': 'string', 'index' : 'not_analyzed'},
                    'term': { 
                        'type': 'string',
                        'analyzer': 'standard',
                        'fields': {
                            'folded': { 
                                'type': 'string',
                                'analyzer': 'folding'
                            }
                        }
                    }
                }            
            }            
        }
    }

    if create:
        se = SearchEngineFactory().create()
        se.create_index(index='term', body=index_settings, ignore=400)

    return index_settings

def prepare_search_index(resource_model_id, create=False):
    """
    Creates the settings and mappings in Elasticsearch to support resource search

    """

    index_settings = { 
        'settings':{
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
                'tiles' : { 
                    'type' : 'nested',
                    'properties' : {
                        'tileid' : {'type' : 'string', 'index' : 'not_analyzed'},
                        'nodegroupid' : {'type' : 'string', 'index' : 'not_analyzed'},
                        'parenttileid' : {'type' : 'string', 'index' : 'not_analyzed'},
                        'resourceinstanceid' : {'type' : 'string', 'index' : 'not_analyzed'}
                    }
                }
            }
        }
    }
    #                 'entityid' : {'type' : 'string', 'index' : 'not_analyzed'},
    #                 'parentid' : {'type' : 'string', 'index' : 'not_analyzed'},
    #                 'property' : {'type' : 'string', 'index' : 'not_analyzed'},
    #                 'entitytypeid' : {'type' : 'string', 'index' : 'not_analyzed'},
    #                 'businesstablename' : {'type' : 'string', 'index' : 'not_analyzed'},
    #                 'value' : {'type' : 'string', 'index' : 'not_analyzed'},
    #                 'label' : {'type' : 'string', 'index' : 'not_analyzed'},
    #                 'primaryname': {'type' : 'string', 'index' : 'not_analyzed'},
    #                 'child_entities' : { 
    #                     'type' : 'nested',
    #                     'properties' : {
    #                         'entityid' : {'type' : 'string', 'index' : 'not_analyzed'},
    #                         'parentid' : {'type' : 'string', 'index' : 'not_analyzed'},
    #                         'property' : {'type' : 'string', 'index' : 'not_analyzed'},
    #                         'entitytypeid' : {'type' : 'string', 'index' : 'not_analyzed'},
    #                         'businesstablename' : {'type' : 'string', 'index' : 'not_analyzed'},
    #                         'label' : {'type' : 'string', 'index' : 'not_analyzed'},
    #                         'value' : {
    #                             'type' : 'string',
    #                             'index' : 'analyzed',
    #                             'fields' : {
    #                                 'raw' : { 'type' : 'string', 'index' : 'not_analyzed'},
    #                                 'folded': { 'type': 'string', 'analyzer': 'folding'}
    #                             }
    #                         }
    #                     }
    #                 },
    #                 'domains' : { 
    #                     'type' : 'nested',
    #                     'properties' : {
    #                         'entityid' : {'type' : 'string', 'index' : 'not_analyzed'},
    #                         'parentid' : {'type' : 'string', 'index' : 'not_analyzed'},
    #                         'property' : {'type' : 'string', 'index' : 'not_analyzed'},
    #                         'entitytypeid' : {'type' : 'string', 'index' : 'not_analyzed'},
    #                         'businesstablename' : {'type' : 'string', 'index' : 'not_analyzed'},
    #                         'label' : {'type' : 'string', 'index' : 'not_analyzed'},
    #                         'value' : {
    #                             'type' : 'string',
    #                             'index' : 'analyzed',
    #                             'fields' : {
    #                                 'raw' : { 'type' : 'string', 'index' : 'not_analyzed'}
    #                             }
    #                         },
    #                         'conceptid' : {'type' : 'string', 'index' : 'not_analyzed'},
    #                     }
    #                 },
    #                 'geometries' : { 
    #                     'type' : 'nested',
    #                     'properties' : {
    #                         'entityid' : {'type' : 'string', 'index' : 'not_analyzed'},
    #                         'parentid' : {'type' : 'string', 'index' : 'not_analyzed'},
    #                         'property' : {'type' : 'string', 'index' : 'not_analyzed'},
    #                         'entitytypeid' : {'type' : 'string', 'index' : 'not_analyzed'},
    #                         'businesstablename' : {'type' : 'string', 'index' : 'not_analyzed'},
    #                         'label' : {'type' : 'string', 'index' : 'not_analyzed'},
    #                         'value' : {
    #                             "type": "geo_shape"
    #                         }
    #                     }
    #                 },
    #                 'dates' : { 
    #                     'type' : 'nested',
    #                     'properties' : {
    #                         'entityid' : {'type' : 'string', 'index' : 'not_analyzed'},
    #                         'parentid' : {'type' : 'string', 'index' : 'not_analyzed'},
    #                         'property' : {'type' : 'string', 'index' : 'not_analyzed'},
    #                         'entitytypeid' : {'type' : 'string', 'index' : 'not_analyzed'},
    #                         'businesstablename' : {'type' : 'string', 'index' : 'not_analyzed'},
    #                         'label' : {'type' : 'string', 'index' : 'not_analyzed'},
    #                         'value' : {
    #                             "type" : "date"
    #                         }
    #                     }
    #                 }
    #             }
    #         }
    #     }
    # }

    if create:
        se = SearchEngineFactory().create()
        try:
            se.create_index(index='entity', body=index_settings)
        except:
            index_settings = index_settings['mappings']
            se.create_mapping(index='entity', doc_type=resource_type_id, body=index_settings)

    return index_settings
