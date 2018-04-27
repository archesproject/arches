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

import json
import couchdb
from urlparse import urlparse, urljoin
from arches.app.models import models
from arches.app.models.mobile_survey import MobileSurvey
from arches.app.models.system_settings import settings
from django.utils.translation import ugettext as _
from arches.app.utils.response import JSONResponse
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from django.http import HttpRequest, HttpResponseNotFound
import arches.app.views.search as search


def clear_associated_surveys():
    surveys = [str(msm['id']) for msm in models.MobileSurveyModel.objects.values("id")]
    uri=urlparse(settings.COUCHDB_URL)
    couchserver = couchdb.Server(settings.COUCHDB_URL)
    couchdbs = [dbname for dbname in couchserver]
    for db in couchdbs:
        survey_id = db[-36:]
        if survey_id in surveys:
            print 'Deleting associated db:', db
            del couchserver[db]
        else:
            print 'Keeping unassociated db:', db

def clear_unassociated_surveys():
    surveys = [str(msm['id']) for msm in models.MobileSurveyModel.objects.values("id")]
    uri=urlparse(settings.COUCHDB_URL)
    couchserver = couchdb.Server(settings.COUCHDB_URL)
    couchdbs = [dbname for dbname in couchserver]
    for db in couchdbs:
        survey_id = db[-36:]
        if survey_id not in surveys:
            if 'project' in db:
                print 'deleting unassociated db:', db
                del couchserver[db]
            else:
                print 'keeping system db:', db
        else:
            print 'keeping associated db:', db

def create_associated_surveys():
    uri=urlparse(settings.COUCHDB_URL)
    couchserver = couchdb.Server(settings.COUCHDB_URL)
    for mobile_survey in models.MobileSurveyModel.objects.all():
        print "Creating", mobile_survey
        create_survey(mobile_survey)

def create_survey(mobile_survey):
    try:
        couch = couchdb.Server(settings.COUCHDB_URL)
        connection_error = False
        try:
            if 'project_' + str(mobile_survey.id) not in couch:
                print 'Creating project_', str(mobile_survey.id)
                db = couch.create('project_' + str(mobile_survey.id))
            else:
                print 'Found project_', str(mobile_survey.id)
                db = couch['project_' + str(mobile_survey.id)]
            survey = JSONSerializer().serializeToPython(mobile_survey, exclude='cards')
            survey['type'] = 'metadata'
            db.save(survey)
            load_data_into_couch(mobile_survey, db, mobile_survey.lasteditedby)

        except Exception as e:
            error_title = _('CouchDB Service Unavailable')
            error_message =  _('Connection to CouchDB failed. Please confirm your CouchDB service is running on: ' + settings.COUCHDB_URL)
            connection_error = JSONResponse({'success':False,'message': '{0}: {1}'.format(error_message, str(e)),'title': error_title}, status=500)
            print connection_error
            return connection_error

    except Exception as e:
        if 'project_' + str(mobile_survey.id) in couch:
            del couch['project_' + str(mobile_survey.id)]
        if connection_error == False:
            error_title = _('Unable to save survey')
            error_message = e
            connection_error = JSONResponse({'success':False,'message': error_message,'title': error_title}, status=500)
        print connection_error
        return connection_error

def collect_resource_instances_for_couch(mobile_survey, user):
    """
    Uses the data definition configs of a mobile survey object to search for
    resource instances relevant to a mobile survey. Takes a user object which
    is required for search.
    """

    query = mobile_survey.datadownloadconfig['custom']
    resource_types = mobile_survey.datadownloadconfig['resources']
    instances = {}
    if query in ('', None) and len(resource_types) == 0:
        print "No resources or data query defined"
    else:
        request = HttpRequest()
        request.user = user
        request.GET['mobiledownload'] = True
        if query in ('', None):
            if len(mobile_survey.bounds.coords) == 0:
                default_bounds = settings.DEFAULT_BOUNDS
                default_bounds['features'][0]['properties']['inverted'] = False
                request.GET['mapFilter'] = json.dumps(default_bounds)
            else:
                request.GET['mapFilter'] = json.dumps({u'type': u'FeatureCollection', 'features':[{'geometry': json.loads(mobile_survey.bounds.json)}]})
            request.GET['typeFilter'] = json.dumps([{'graphid': resourceid, 'inverted': False } for resourceid in mobile_survey.datadownloadconfig['resources']])
        else:
            parsed = urlparse.urlparse(query)
            urlparams = urlparse.parse_qs(parsed.query)
            for k, v in urlparams.iteritems():
                request.GET[k] = v[0]
        search_res_json = search.search_results(request)
        search_res = JSONDeserializer().deserialize(search_res_json.content)
        try:
            instances = {hit['_source']['resourceinstanceid']: hit['_source'] for hit in search_res['results']['hits']['hits']}
        except KeyError:
            print 'no instances found in', search_res
    return instances

def load_tiles_into_couch(mobile_survey, db, instances):
    """
    Takes a mobile survey object, a couch database instance, and a dictionary
    of resource instances to identify eligible tiles and load them into the
    database instance
    """
    cards = mobile_survey.cards.all()
    for card in cards:
        tiles = models.TileModel.objects.filter(nodegroup=card.nodegroup_id)
        tiles_serialized = json.loads(JSONSerializer().serialize(tiles))
        for tile in tiles_serialized:
            if str(tile['resourceinstance_id']) in instances:
                try:
                    tile['type'] = 'tile'
                    couch_record = db.get(tile['tileid'])
                    if couch_record == None:
                        db[tile['tileid']] = tile
                    else:
                        if couch_record['data'] != tile['data']:
                            couch_record['data'] = tile['data']
                            db[tile['tileid']] = couch_record
                except Exception as e:
                    print e, tile

def load_instances_into_couch(mobile_survey, db, instances):
    """
    Takes a mobile survey object, a couch database instance, and a dictionary
    of resource instances and loads them into the database instance.
    """
    for instanceid, instance in instances.iteritems():
        try:
            instance['type'] = 'resource'
            couch_record = db.get(instanceid)
            if couch_record == None:
                db[instanceid] = instance
        except Exception as e:
            print e, instance

def load_data_into_couch(mobile_survey, db, user):
    """
    Takes a mobile survey, a couch database intance and a django user and loads
    tile and resource instance data into the couch instance.
    """

    instances = collect_resource_instances_for_couch(mobile_survey, user)
    load_tiles_into_couch(mobile_survey, db, instances)
    load_instances_into_couch(mobile_survey, db, instances)

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
                    'provisional': {'type': 'keyword'},
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
                    'provisional': {'type': 'keyword'},
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
                    'provisional': {'type': 'keyword'},
                    'tiles' : {
                        'type' : 'nested',
                        'properties' : {
                            "tiles": {'enabled': False},
                            'tileid' : {'type': 'keyword'},
                            'nodegroup_id' : {'type': 'keyword'},
                            'parenttile_id' : {'type': 'keyword'},
                            'resourceinstanceid_id' : {'type': 'keyword'}
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
                            'provisional': {'type': 'keyword'}
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
                            'provisional': {'type': 'keyword'}
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
                            'provisional': {'type': 'keyword'}
                        }
                    },
                    'points': {
                        'type' : 'nested',
                        'properties' : {
                            'point' : {'type': 'geo_point'},
                            'nodegroup_id' : {'type': 'keyword'},
                            'provisional': {'type': 'keyword'}
                        }
                    },
                    'dates' : {
                        'type' : 'nested',
                        'properties' : {
                            'date' : {'type': 'float'},
                            'nodegroup_id' : {'type': 'keyword'},
                            'nodeid' : {'type': 'keyword'},
                            'provisional': {'type': 'keyword'}
                        }
                    },
                    'numbers' : {
                        'type' : 'nested',
                        'properties' : {
                            'number' : {'type': 'double'},
                            'nodegroup_id' : {'type': 'keyword'},
                            'provisional': {'type': 'keyword'}
                        }
                    },
                    'date_ranges': {
                        'type' : 'nested',
                        'properties' : {
                            'date_range' : {'type': 'float_range'},
                            'nodegroup_id' : {'type': 'keyword'},
                            'provisional': {'type': 'keyword'}
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
