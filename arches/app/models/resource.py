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

from django.conf import settings
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
    

    def get_form(self, form_id):
        selected_form = None
        forms = [form for group in self.form_groups for form in group['forms']]
        for form in forms:
            if form.id == form_id:
                selected_form = form
        return selected_form(self)


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

            names = []
            for name in self.get_primary_name():
                names.append(name.value)

            primary_display_name = ' '.join(names)
            search_result['primaryname'] = primary_display_name

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

