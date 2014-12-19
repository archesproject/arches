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
        Deltes a resource from the db wrapped in a transaction 
        
        """

        timestamp = datetime.now()
        for entity in self.flatten():
            if not delete_root and entity.entitytypeid != self.entitytypeid:
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

        #super(Resource, self).delete(delete_root=delete_root)
        self._delete(delete_root=delete_root)

    def get_form(self, form_id):
        selected_form = None
        forms = [form for group in self.form_groups for form in group['forms']]
        for form in forms:
            if form['id'] == form_id:
                selected_form = form
        return selected_form['class'](self)

    def get_type_name(self):
        return settings.RESOURCE_TYPE_CONFIGS[self.entitytypeid]['name']

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
                        related_entity = Entity().get(related_resource_id)
                        ret.append(related_entity)
                    else:
                        ret.append(relationship)
        return ret   


    def get_alternate_names(self):
        """
        Gets the human readable name to display for entity instances

        """

        pass

    def index(self):
        """
        Indexes all the nessesary documents related to resources to support the map, search, and reports

        """

        se = SearchEngineFactory().create()

        se.create_mapping('term', 'value', 'ids', 'string', 'not_analyzed')
        
        mapping =  { 
            self.entitytypeid : {
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
                                    'raw' : { 'type' : 'string', 'index' : 'not_analyzed'}
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

        se.create_mapping('entity', self.entitytypeid, mapping=mapping)

        geometries = []

        def gather_entities(entity):
            if entity.businesstablename == 'strings':
                if len(entity.value.split(' ')) < 10:
                    se.index_term(entity.value, entity.entityid, options={'context': entity.entitytypeid})
            elif entity.businesstablename == 'domains':
                domain = archesmodels.Domains.objects.get(pk=entity.entityid)
                if domain.val:
                    concept = Concept(domain.val.conceptid).get(include=['label'])
                    entity.conceptid = domain.val.conceptid_id
                    if concept:
                        scheme_pref_label = concept.get_context().get_preflabel().value
                        se.index_term(concept.get_preflabel().value, entity.entityid, options={'context': scheme_pref_label, 'conceptid': domain.val.conceptid_id})
            elif entity.businesstablename == 'geometries':
                entity.value = JSONDeserializer().deserialize(fromstr(entity.value).json)
                geometries.append(entity.value)
            elif entity.businesstablename == 'dates':
                pass
            elif entity.businesstablename == 'numbers':
                pass
            elif entity.businesstablename == 'files':
                pass
            return entity.businesstablename
        
        root_entity = self.copy()
        root_entity.primaryname = self.get_primary_name()
        root_entity.child_entities = []
        root_entity.dates = []
        root_entity.domains = []
        root_entity.geometries = []
        del root_entity.form_groups

        for entity in self.flatten():
            businesstablename = gather_entities(entity)
            if entity.entityid != self.entityid:
                if businesstablename == 'domains':
                    root_entity.domains.append(entity)
                elif businesstablename == 'dates':
                    root_entity.dates.append(entity)
                elif businesstablename == 'geometries':
                    root_entity.geometries.append(entity)
                else:
                    root_entity.child_entities.append(entity)


        if len(geometries) > 0:
            geojson = {
                'type': 'Feature',
                'id': self.entityid,
                'geometry':  { 
                    'type': 'GeometryCollection',
                    'geometries': geometries
                },
                'properties': {
                    'entitytypeid': self.entitytypeid,
                    'primaryname': self.get_primary_name(),
                }
            }
            se.index_data('maplayers', self.entitytypeid, geojson, idfield='id')
        se.index_data('resource', self.entitytypeid, self.dictify(), id=self.entityid)
        se.index_data('entity', root_entity.entitytypeid, JSONSerializer().serializeToPython(root_entity), id=root_entity.entityid)

    def delete_index(self):
        """
        removes an entity from the search index

        """

        if self.get_rank() == 0:
            se = SearchEngineFactory().create()
            def delete_indexes(entity):
                if entity.get_rank() == 0:
                    se.delete(index='entity', type=entity.entitytypeid, id=entity.entityid)

                if entity.entitytypeid in settings.ENTITY_TYPE_FOR_MAP_DISPLAY:
                    se.delete(index='maplayers', type=self.entitytypeid, id=entity.entityid)

                if entity.entitytypeid in settings.SEARCHABLE_ENTITY_TYPES:
                    se.delete_terms(entity)

            entity = Entity().get(self.entityid)
            entity.traverse(delete_indexes)

    @staticmethod
    def get_report(resourceid):
        return {
            'id': None,
            'data': None
        }
