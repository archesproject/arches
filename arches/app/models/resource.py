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
        resource_name = ''
        for resource_type in self.get_resource_types():
            if resource_type['resourcetypeid'] == self.entitytypeid:
                return resource_type['name']
        return resource_name


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

    def index_old(self):
        """
        Gets a SearchResult object for a given resource
        Used for populating the search index with searchable entity information

        """

        if self.get_rank() == 0:
            se = SearchEngineFactory().create()
            search_result = {}
            search_result['entityid'] = self.entityid
            search_result['entitytypeid'] = self.entitytypeid  
            search_result['strings'] = []
            search_result['geometries'] = []
            search_result['concepts'] = []

            term_entities = []

            names = self.get_names()
            primary_display_name = self.get_primary_name()

            for enititytype in settings.SEARCHABLE_ENTITY_TYPES:
                for entity in self.find_entities_by_type_id(enititytype):
                    search_result['strings'].append(entity.value)
                    term_entities.append(entity)

            for geom_entity in self.find_entities_by_type_id(settings.ENTITY_TYPE_FOR_MAP_DISPLAY):
                search_result['geometries'].append(fromstr(geom_entity.value).json)
                mapfeature = MapFeature()
                mapfeature.geomentityid = geom_entity.entityid
                mapfeature.entityid = self.entityid
                mapfeature.entitytypeid = self.entitytypeid
                mapfeature.primaryname = primary_display_name
                mapfeature.geometry = geom_entity.value
                data = JSONSerializer().serializeToPython(mapfeature, ensure_ascii=True, indent=4)
                se.index_data('maplayers', self.entitytypeid, data, idfield='geomentityid')

            def to_int(s):
                try:
                    return int(s)
                except ValueError:
                    return ''

            def inspect_node(entity):
                if entity.entitytypeid in settings.ADV_SEARCHABLE_ENTITY_TYPES or entity.entitytypeid in settings.SEARCHABLE_ENTITY_TYPES:
                    if entity.entitytypeid not in search_result:
                        search_result[entity.entitytypeid] = []

                    if entity.entitytypeid in settings.ENTITY_TYPE_FOR_MAP_DISPLAY:
                        search_result[entity.entitytypeid].append(JSONDeserializer().deserialize(fromstr(entity.value).json))
                    else:
                        search_result[entity.entitytypeid].append(entity.value)

            self.traverse(inspect_node)

            for entitytype, value in search_result.iteritems():
                if entitytype in settings.ADV_SEARCHABLE_ENTITY_TYPES or entitytype in settings.SEARCHABLE_ENTITY_TYPES:
                    if entitytype in settings.ENTITY_TYPE_FOR_MAP_DISPLAY:
                        se.create_mapping('entity', self.entitytypeid, entitytype, 'geo_shape') 
                    else:                   
                        try:
                            uuid.UUID(value[0])
                            # SET FIELDS WITH UUIDS TO BE "NOT ANALYZED" IN ELASTIC SEARCH
                            se.create_mapping('entity', self.entitytypeid, entitytype, 'string', 'not_analyzed')
                        except(ValueError):
                            pass

                        search_result[entitytype] = list(set(search_result[entitytype]))

            data = JSONSerializer().serializeToPython(search_result, ensure_ascii=True, indent=4)
            se.index_data('entity', self.entitytypeid, data, idfield=None, id=self.entityid)
            se.create_mapping('term', 'value', 'entityids', 'string', 'not_analyzed')
            se.index_terms(term_entities)

            return search_result   

    def index(self):
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
                    'value' : {'type' : 'string', 'index' : 'analyzed'},
                    'relatedentities' : { 
                        'type' : 'nested', 
                        'index' : 'analyzed',
                        'properties' : {
                            'entityid' : {'type' : 'string', 'index' : 'not_analyzed'},
                            'parentid' : {'type' : 'string', 'index' : 'not_analyzed'},
                            'property' : {'type' : 'string', 'index' : 'not_analyzed'},
                            'entitytypeid' : {'type' : 'string', 'index' : 'not_analyzed'},
                            'businesstablename' : {'type' : 'string', 'index' : 'not_analyzed'},
                            'value' : {
                                'type' : 'string',
                                'index' : 'analyzed',
                                'fields' : {
                                    'raw' : { 'type' : 'string', 'index' : 'not_analyzed'}
                                }
                            }
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
                            'value' : {
                                "type" : "date"
                            }
                        }
                    }
                }
            }
        }
        se.create_mapping('entity', self.entitytypeid, mapping=mapping)

        def gather_entities(entity):
            dbentity = archesmodels.Entities.objects.get(pk=entity.entityid)
            # businesstablename = dbentity.entitytypeid.businesstablename
            # entity.businesstablename = businesstablename
            if entity.businesstablename == 'strings':
                if len(entity.value.split(' ')) < 10:
                    se.index_term(entity.value, entity.entityid, options={'context': entity.entitytypeid})
            elif entity.businesstablename == 'domains':
                # domain = archesmodels.Domains.objects.get(pk=dbentity.entityid)
                # if domain.val:
                #     concept = Concept({'id': domain.val.conceptid.pk}).get(inlude=['label'])
                #     if concept:
                #         auth_pref_label = ''
                #         auth_doc_concept = concept.get_auth_doc_concept()
                #         if auth_doc_concept:
                #             auth_pref_label = auth_doc_concept.get_preflabel().value
                #         se.index_term(concept.get_preflabel().value, entity.entityid, options={'context': auth_pref_label, 'conceptid': domain.val.conceptid_id})
                pass
            elif entity.businesstablename == 'geometries':
                geojson = {
                    'type': 'Feature',
                    'id': entity.entityid,
                    'geometry': JSONDeserializer().deserialize(fromstr(entity.value).json),
                    'properties': {
                        'resourceid': self.entityid,
                        'entitytypeid': self.entitytypeid,
                        'primaryname': self.get_primary_name(),
                    }
                }
                se.index_data('maplayers', self.entitytypeid, geojson, idfield='id')
            elif entity.businesstablename == 'dates':
                pass
            elif entity.businesstablename == 'numbers':
                pass
            elif entity.businesstablename == 'files':
                pass
            return entity.businesstablename




        flattend_entity = self.flatten()
        # root_entity = self
        # root_entity.district = district
        # root_entity.relatedentities = []
        # root_entity.dates = []
        # root_entity.geometries = []
        for entity in flattend_entity:
            businesstablename = gather_entities(entity)
        #     if entity.entityid != self.entityid:
        #         try:
        #             del entity.relatedentities
        #         except: pass
        #         if businesstablename == 'dates':
        #             root_entity.dates.append(entity)
        #         elif businesstablename == 'geometries':
        #             root_entity.geometries.append(entity)
        #         else:
        #             root_entity.relatedentities.append(entity)

        # se.index_data('entity', root_entity.entitytypeid, JSONSerializer().serializeToPython(root_entity, ensure_ascii=True), idfield=None, id=root_entity.entityid)

    def delete_index(self):
        """
        removes an entity from the search index
        assumes that self is a resource

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


    @staticmethod
    def get_resource_types():
        raise NotImplementedError



# # Here's what I'd like to be able to do

# resource = Resource('0538a60a-2816-3b0b-9415-124e2aad65cd') # a heritage resource guid, populates the Resource with data from the db
# resource = Resource(Entity({entitytypeid: 'HeritageResource.E32'})) # a heritage resource type id, returns a blank resource
# # now we have a resource that "knows" it's a heritage resource
# # forms aren't populated until we access them

# # resource has specific methods to perform CRUD on specific portions of itself as view models (for forms etc..)
# summary_form = resource.forms.get('summary')
# resource.forms.set('summary', formdata)
# resource.save() # this method calls save on the forms themselves


# class Form(object):
#     self.icon = ''
#     self.displayname = ''
#     ....
#     pass


# class SummaryForm(Form):  # this form is specific to a certain resource graph shape (could be used across multiple entitytypes)
#     def __init__(self, *args, **kwargs):
#         self.names = []
#         self.importantdates = []
#         self.subjects = []
#         self.resource = None
    
#     def get():
#         # populates itself based on its Entity
#         # here's where we parse a enitty into it's constitutant parts
#         return self

#     def set(data):
#         pass

# class DescriptionForm(Form):  # this form is specific to a certain resource graph shape (could be used across multiple entitytypes)
#     def __init__(self, *args, **kwargs):
#         self.description = []
    
#     def get():
#         # populates itself based on its Entity
#         # here's where we parse a enitty into it's constitutant parts
#         for item in self.find_entities_by_type_id('DESCRIPTION.E83')
#             self.description['type'] = item.get_entity_value # here's where we populate the actual value
#             self.description['description'] = item.get_entity_value
#         return self

#     def set(data):
#         pass

# class InformationResourceSummaryForm(Form):
#     pass

# class FormManager():
#     def get(formname):
#         form = self.forms[formname]
#         return form.get()

#     def set(formname, data):
#         form = self.forms[formname]
#         form.set(data)
#         return form


# class HeritageDistrictForms(FormManager):
#     forms = {
#         'summary': SummaryForm(),
#         'description': DescriptionForm(),
#         ....
#     }

# class ActorForms(FormManager):
#     forms = {
#         'summary': ActorSummaryForm(),
#         'description': DescriptionForm(),
#         ....
#     }

