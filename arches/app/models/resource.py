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

import uuid
from datetime import datetime
from django.conf import settings
from django.contrib.gis.geos import fromstr
import arches.app.models.models as archesmodels
from django.db.models import Q
from arches.app.models.entity import Entity
from arches.app.models.concept import Concept
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from django.utils.translation import ugettext as _
from django.forms.models import model_to_dict
from django.contrib.gis.geos import GEOSGeometry

class Resource(Entity):
    """ 
    Used for managing Resource type entities

    This class will return an instance of the class defined in settings.RESOURCE_MODEL
    The class defined in settings.ENTITY_MODEL must be a subclass of this class (arches.app.models.resource.Resource)

    """
    def __new__(cls, *args, **kwargs):
        modulename = kwargs.get('mod', 'default')
        if modulename == '':
            return super(Resource, cls).__new__(cls)
        else:
            fully_qualified_modulename = settings.RESOURCE_MODEL.get(modulename)
            if fully_qualified_modulename == 'arches.app.models.resource.Resource' or fully_qualified_modulename == '':
                return super(Entity, cls).__new__(cls)
            components = fully_qualified_modulename.split('.')
            classname = components[len(components)-1]
            modulename = ('.').join(components[0:len(components)-1])
            kwargs['mod'] = ''
            mod = __import__(modulename, globals(), locals(), [classname], -1)
            if issubclass(getattr(mod, classname), Resource):
                return getattr(mod, classname)(*args, **kwargs)
            else:
                raise Exception('The class "%s" defined in settings.RESOURCE_MODEL must be a subclass of arches.app.models.resource.Resource' % fully_qualified_modulename)


    def __init__(self, *args, **kwargs):
        super(Resource, self).__init__(*args, **kwargs)

        self.form_groups = []

    def save(self, user={}, note=''):
        """
        Saves a resource back to the db 

        """

        newentity = False
        timestamp = datetime.now()

        if self.entityid != '':
            entity_pre_save = Entity().get(self.entityid)
        else:
            newentity = True

        self._save() 

        if not newentity:
            diff = self.diff(entity_pre_save)
            for entity in diff['deleted_nodes']:
                if entity.label != '' or entity.value != '':
                    edit = archesmodels.EditLog()        
                    edit.editlogid = str(uuid.uuid4())
                    edit.resourceentitytypeid = self.entitytypeid
                    edit.resourceid = self.entityid
                    edit.userid = getattr(user, 'id', '')
                    edit.user_email = getattr(user, 'email', '')
                    edit.user_firstname = getattr(user, 'first_name', '')
                    edit.user_lastname = getattr(user, 'last_name', '')
                    edit.note = note
                    edit.timestamp = timestamp
                    edit.attributeentitytypeid = entity.entitytypeid
                    edit.edittype = 'delete'
                    edit.oldvalue = entity.label if entity.label != '' else entity.value
                    edit.save()             
                entity._delete(delete_root=True)

            for entity in diff['updated_nodes']:
                if entity['from'].label != '' or entity['to'].label != '' or entity['from'].value != '' or entity['to'].value != '':
                    edit = archesmodels.EditLog()        
                    edit.editlogid = str(uuid.uuid4())
                    edit.resourceentitytypeid = self.entitytypeid
                    edit.resourceid = self.entityid
                    edit.userid = getattr(user, 'id', '')
                    edit.user_email = getattr(user, 'email', '')
                    edit.user_firstname = getattr(user, 'first_name', '')
                    edit.user_lastname = getattr(user, 'last_name', '')
                    edit.note = note
                    edit.timestamp = timestamp
                    edit.attributeentitytypeid = entity['from'].entitytypeid
                    edit.edittype = 'update'
                    edit.oldvalue = entity['from'].label if entity['from'].label != '' else entity['from'].value 
                    edit.newvalue = entity['to'].label if entity['to'].label != '' else entity['to'].value 
                    edit.save()    

            for entity in diff['inserted_nodes']:
                if entity.label != '' or entity.value != '':
                    edit = archesmodels.EditLog()        
                    edit.editlogid = str(uuid.uuid4())
                    edit.resourceentitytypeid = self.entitytypeid
                    edit.resourceid = self.entityid
                    edit.userid = getattr(user, 'id', '')
                    edit.user_email = getattr(user, 'email', '')
                    edit.user_firstname = getattr(user, 'first_name', '')
                    edit.user_lastname = getattr(user, 'last_name', '')
                    edit.note = note
                    edit.timestamp = timestamp
                    edit.attributeentitytypeid = entity.entitytypeid
                    edit.edittype = 'insert'
                    edit.oldvalue = None
                    edit.newvalue = entity.label if entity.label != '' else entity.value
                    edit.save()      

        else:
            for entity in self.flatten():
                if entity.label != '' or entity.value != '':
                    edit = archesmodels.EditLog()        
                    edit.editlogid = str(uuid.uuid4())
                    edit.resourceentitytypeid = self.entitytypeid
                    edit.resourceid = self.entityid
                    edit.userid = getattr(user, 'id', '')
                    edit.user_email = getattr(user, 'email', '')
                    edit.user_firstname = getattr(user, 'first_name', '')
                    edit.user_lastname = getattr(user, 'last_name', '')
                    edit.note = note
                    edit.timestamp = timestamp
                    edit.attributeentitytypeid = entity.entitytypeid
                    edit.edittype = 'create'
                    edit.oldvalue = None
                    edit.newvalue = entity.label if entity.label != '' else entity.value
                    edit.save()

        return self

    def delete(self, user={}, note=''):
        """
        Deltes a resource from the db
        
        """

        timestamp = datetime.now()
        for entity in self.flatten():
            edit = archesmodels.EditLog()        
            edit.editlogid = str(uuid.uuid4())
            edit.resourceentitytypeid = self.entitytypeid
            edit.resourceid = self.entityid
            edit.userid = getattr(user, 'id', '')
            edit.user_email = getattr(user, 'email', '')
            edit.user_firstname = getattr(user, 'first_name', '')
            edit.user_lastname = getattr(user, 'last_name', '') 
            edit.note = note                               
            edit.timestamp = timestamp
            edit.attributeentitytypeid = entity.entitytypeid
            edit.edittype = 'delete'
            edit.oldvalue = entity.label if entity.label != '' else entity.value
            edit.newvalue = None
            edit.save()

        self._delete(delete_root=True)

    def get_form(self, form_id):
        selected_form = None
        forms = [form for group in self.form_groups for form in group['forms']]
        for form in forms:
            if form['id'] == form_id:
                selected_form = form
        return selected_form['class'](self)

    def get_type_name(self):
        return settings.RESOURCE_TYPE_CONFIGS()[self.entitytypeid]['name']

    def get_primary_name(self):
        if self.entityid == '':
            return _('New Resource')
        return _('Unnamed Resource')

    def get_names(self):
        return []

    def create_resource_relationship(self, related_resource_id, notes=None, date_started=None, date_ended=None, relationship_type_id=None):
        """
        Creates a relationship between resources 
        
        """

        relationship = archesmodels.RelatedResource(
            entityid1 = self.entityid,
            entityid2 = related_resource_id,
            notes = notes,
            relationshiptype = relationship_type_id,
            datestarted = date_started,
            dateended = date_ended,
        )

        relationship.save()

    def delete_all_resource_relationships(self):
        """
        Deletes all relationships to other resources. 
        
        """     

        relationships = archesmodels.RelatedResource.objects.filter( Q(entityid2=self.entityid)|Q(entityid1=self.entityid) )

        for relationship in relationships:
            relationship.delete()

    def delete_resource_relationship(self, related_resource_id, relationship_type_id=None):
        """
        Deletes the relationships from this entity to another entity. 
        
        """        

        if relationship_type:
            relationships = archesmodels.RelatedResource.objects.filter( Q(entityid2=self.entityid)|Q(entityid1=self.entityid), Q(entityid2=related_resource_id)|Q(entityid1=related_resource_id), Q(relationshiptype=relationship_type_id))
        else:
            relationships = archesmodels.RelatedResource.objects.filter( Q(entityid2=self.entityid)|Q(entityid1=self.entityid), Q(entityid2=related_resource_id)|Q(entityid1=related_resource_id) )

        for relationship in relationships:
            relationship.delete()

    def get_related_resources(self, entitytypeid=None, relationship_type_id=None, return_entities=True):
        """
        Gets a list of entities related to this entity, optionaly filters on entitytypeid and/or relationship type. 
        Setting return_entities to False will return the relationship records 
        rather than the related entities. 
        """

        ret = []

        if self.entityid:
            if relationship_type_id:
                relationships = archesmodels.RelatedResource.objects.filter(Q(entityid2=self.entityid)|Q(entityid1=self.entityid), Q(relationshiptype=relationship_type_id))
            else:
                relationships = archesmodels.RelatedResource.objects.filter(Q(entityid2=self.entityid)|Q(entityid1=self.entityid))
      
            for relationship in relationships: 
                related_resource_id = relationship.entityid1 if relationship.entityid1 != self.entityid else relationship.entityid2
                entity_obj = archesmodels.Entities.objects.get(pk = related_resource_id)
                if (entitytypeid == None or entity_obj.entitytypeid_id == entitytypeid) and (relationship_type_id == None or relationship_type_id == relationship.relationshiptype):
                    if return_entities == True:
                        related_entity = Resource().get(related_resource_id)
                        ret.append(related_entity)
                    else:
                        ret.append(relationship)
        return ret   

    def get_alternate_names(self):
        """
        Gets the human readable name to display for entity instances

        """

        pass

    def bulk_index(self, resources=[]):
        report_documents = []
        search_documents = []
        geojson_documents = []
        terms = []

        for resource in resources:
            report_documents = report_documents + resource.prepare_documents_for_report_index()
            search_documents = search_documents + resource.prepare_documents_for_search_index()
            geojson_documents = geojson_documents + resource.prepare_documents_for_map_index(geom_entities=document['geometries'])


    def index(self):
        """
        Indexes all the nessesary documents related to resources to support the map, search, and reports

        """

        se = SearchEngineFactory().create()

        search_documents = self.prepare_documents_for_search_index()
        for document in search_documents:
            se.index_data('entity', self.entitytypeid, document, id=self.entityid)

            report_documents = self.prepare_documents_for_report_index(geom_entities=document['geometries'])
            for report_document in report_documents:
                se.index_data('resource', self.entitytypeid, report_document, id=self.entityid)

            geojson_documents = self.prepare_documents_for_map_index(geom_entities=document['geometries'])
            for geojson in geojson_documents:
                se.index_data('maplayers', self.entitytypeid, geojson, idfield='id')

        for term in self.prepare_terms_for_search_index():
           se.index_term(term['term'], term['entityid'], term['context'], term['options'])

    def prepare_documents_for_search_index(self):
        """
        Generates a list of specialized resource based documents to support resource search

        """

        document = Entity()
        document.property = self.property
        document.entitytypeid = self.entitytypeid
        document.entityid = self.entityid
        document.value = self.value
        document.label = self.label
        document.businesstablename = self.businesstablename
        document.primaryname = self.get_primary_name()
        document.child_entities = []
        document.dates = []
        document.domains = []
        document.geometries = []

        for entity in self.flatten():
            if entity.entityid != self.entityid:
                if entity.businesstablename == 'domains':
                    value = archesmodels.Values.objects.get(pk=entity.value)
                    entity_copy = entity.copy()
                    entity_copy.conceptid = value.conceptid_id
                    document.domains.append(entity_copy)
                elif entity.businesstablename == 'dates':
                    document.dates.append(entity)
                elif entity.businesstablename == 'geometries':
                    entity.value = JSONDeserializer().deserialize(fromstr(entity.value).json)
                    document.geometries.append(entity)
                else:
                    document.child_entities.append(entity)

        return [JSONSerializer().serializeToPython(document)]

    def prepare_documents_for_map_index(self, geom_entities=[]):
        """
        Generates a list of geojson documents to support the display of resources on a map

        """

        document = []
        if len(geom_entities) > 0:
            geojson_geom = {
                'type': 'GeometryCollection',
                'geometries': [geom_entity['value'] for geom_entity in geom_entities]
            }
            geom = GEOSGeometry(JSONSerializer().serialize(geojson_geom), srid=4326)
             
            document = [{
                'type': 'Feature',
                'id': self.entityid,
                'geometry':  geojson_geom,
                'properties': {
                    'entitytypeid': self.entitytypeid,
                    'primaryname': self.get_primary_name(),
                    'centroid': JSONDeserializer().deserialize(geom.centroid.json),
                    'extent': geom.extent
                }
            }]

        return document

    def prepare_terms_for_search_index(self):
        """
        Generates a list of term objects with composed of any string less then the length of settings.WORDS_PER_SEARCH_TERM  
        long and any concept associated with a resource to support term search  

        """

        terms = []

        def gather_entities(entity):
            if entity.businesstablename == '':
                pass
            elif entity.businesstablename == 'strings':
                if settings.WORDS_PER_SEARCH_TERM == None or (len(entity.value.split(' ')) < settings.WORDS_PER_SEARCH_TERM):
                    entitytype = archesmodels.EntityTypes.objects.get(pk=entity.entitytypeid)
                    terms.append({'term': entity.value, 'entityid': entity.entityid, 'context': entitytype.conceptid_id, 'options': {}})
            elif entity.businesstablename == 'domains':
                pass
            elif entity.businesstablename == 'geometries':
                pass
            elif entity.businesstablename == 'dates':
                pass
            elif entity.businesstablename == 'numbers':
                pass
            elif entity.businesstablename == 'files':
                pass

        self.traverse(gather_entities)
        return terms

    def prepare_documents_for_report_index(self, geom_entities=[]):
        """
        Generates a list of specialized resource based documents to support resource reports

        """

        geojson_geom = None
        if len(geom_entities) > 0:
            geojson_geom = {
                'type': 'GeometryCollection',
                'geometries': [geom_entity['value'] for geom_entity in geom_entities]
            }

        entity_dict = Entity()
        entity_dict.property = self.property
        entity_dict.entitytypeid = self.entitytypeid
        entity_dict.entityid = self.entityid
        entity_dict.primaryname = self.get_primary_name()
        entity_dict.geometry = geojson_geom
        
        entity_dict.graph = self.dictify(keys=['label', 'value'])
        return [JSONSerializer().serializeToPython(entity_dict)]

    def delete_index(self):
        """
        removes an entity from the search index

        """

        se = SearchEngineFactory().create()
        se.delete(index='entity', doc_type=self.entitytypeid, id=self.entityid)
        se.delete(index='resource', doc_type=self.entitytypeid, id=self.entityid)        
        se.delete(index='maplayers', doc_type=self.entitytypeid, id=self.entityid)

        def delete_indexes(entity):
            if entity.businesstablename == 'strings' or entity.businesstablename == 'domains':
                se.delete_terms(entity)

        entity = Entity().get(self.entityid)
        entity.traverse(delete_indexes)

    def prepare_search_index(self, resource_type_id, create=False):
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
                resource_type_id : {
                    'properties' : {
                        'entityid' : {'type' : 'string', 'index' : 'not_analyzed'},
                        'parentid' : {'type' : 'string', 'index' : 'not_analyzed'},
                        'property' : {'type' : 'string', 'index' : 'not_analyzed'},
                        'entitytypeid' : {'type' : 'string', 'index' : 'not_analyzed'},
                        'businesstablename' : {'type' : 'string', 'index' : 'not_analyzed'},
                        'value' : {'type' : 'string', 'index' : 'not_analyzed'},
                        'label' : {'type' : 'string', 'index' : 'not_analyzed'},
                        'primaryname': {'type' : 'string', 'index' : 'not_analyzed'},
                        'child_entities' : { 
                            'type' : 'nested', 
                            'index' : 'analyzed',
                            'properties' : {
                                'entityid' : {'type' : 'string', 'index' : 'not_analyzed'},
                                'parentid' : {'type' : 'string', 'index' : 'not_analyzed'},
                                'property' : {'type' : 'string', 'index' : 'not_analyzed'},
                                'entitytypeid' : {'type' : 'string', 'index' : 'not_analyzed'},
                                'businesstablename' : {'type' : 'string', 'index' : 'not_analyzed'},
                                'label' : {'type' : 'string', 'index' : 'not_analyzed'},
                                'value' : {
                                    'type' : 'string',
                                    'index' : 'analyzed',
                                    'fields' : {
                                        'raw' : { 'type' : 'string', 'index' : 'not_analyzed'},
                                        'folded': { 'type': 'string', 'analyzer': 'folding'}
                                    }
                                }
                            }
                        },
                        'domains' : { 
                            'type' : 'nested', 
                            'index' : 'analyzed',
                            'properties' : {
                                'entityid' : {'type' : 'string', 'index' : 'not_analyzed'},
                                'parentid' : {'type' : 'string', 'index' : 'not_analyzed'},
                                'property' : {'type' : 'string', 'index' : 'not_analyzed'},
                                'entitytypeid' : {'type' : 'string', 'index' : 'not_analyzed'},
                                'businesstablename' : {'type' : 'string', 'index' : 'not_analyzed'},
                                'label' : {'type' : 'string', 'index' : 'not_analyzed'},
                                'value' : {
                                    'type' : 'string',
                                    'index' : 'analyzed',
                                    'fields' : {
                                        'raw' : { 'type' : 'string', 'index' : 'not_analyzed'}
                                    }
                                },
                                'conceptid' : {'type' : 'string', 'index' : 'not_analyzed'},
                            }
                        },
                        'geometries' : { 
                            'type' : 'nested', 
                            'index' : 'analyzed',
                            'properties' : {
                                'entityid' : {'type' : 'string', 'index' : 'not_analyzed'},
                                'parentid' : {'type' : 'string', 'index' : 'not_analyzed'},
                                'property' : {'type' : 'string', 'index' : 'not_analyzed'},
                                'entitytypeid' : {'type' : 'string', 'index' : 'not_analyzed'},
                                'businesstablename' : {'type' : 'string', 'index' : 'not_analyzed'},
                                'label' : {'type' : 'string', 'index' : 'not_analyzed'},
                                'value' : {
                                    "type": "geo_shape"
                                }
                            }
                        },
                        'dates' : { 
                            'type' : 'nested', 
                            'index' : 'analyzed',
                            'properties' : {
                                'entityid' : {'type' : 'string', 'index' : 'not_analyzed'},
                                'parentid' : {'type' : 'string', 'index' : 'not_analyzed'},
                                'property' : {'type' : 'string', 'index' : 'not_analyzed'},
                                'entitytypeid' : {'type' : 'string', 'index' : 'not_analyzed'},
                                'businesstablename' : {'type' : 'string', 'index' : 'not_analyzed'},
                                'label' : {'type' : 'string', 'index' : 'not_analyzed'},
                                'value' : {
                                    "type" : "date"
                                }
                            }
                        }
                    }
                }
            }
        }

        if create:
            se = SearchEngineFactory().create()
            try:
                se.create_index(index='entity', body=index_settings)
            except:
                index_settings = index_settings['mappings']
                se.create_mapping(index='entity', doc_type=resource_type_id, body=index_settings)

        return index_settings

    def prepare_term_index(self, create=False):
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

    def prepare_resource_relations_index(self, create=False):
        """
        Creates the settings and mappings in Elasticsearch to support related resources

        """

        index_settings = { 
            'mappings':{
                'all': {
                    'properties': {
                        'resourcexid': {'type': 'long'},
                        'notes': { 'type': 'string'},
                        'relationshiptype': {'type': 'string', 'index' : 'not_analyzed'},
                        'entityid2': {'type': 'string', 'index' : 'not_analyzed'},
                        'entityid1': {'type': 'string', 'index' : 'not_analyzed'}
                    }  
                }
            }
        }    

        if create:
            se = SearchEngineFactory().create()
            se.create_index(index='resource_relations', body=index_settings, ignore=400)

        return index_settings
           
    @staticmethod
    def get_report(resourceid):
        return {
            'id': None,
            'data': None
        }
