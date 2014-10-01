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

from datetime import datetime
import uuid
import types
import arches.app.models.models as archesmodels
from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.geos import fromstr
from django.db import connection
from django.db import transaction
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from arches.app.models.search import SearchResult, MapFeature
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer

class Entity(object):
    """ 
    Used for mapping complete entity graph objects to and from the database

    This class will return an instance of the class defined in settings.ENTITY_MODEL
    The class defined in settings.ENTITY_MODEL must be a subclass of this class (arches.app.models.entity.Entity)

    """
    def __new__(cls, *args, **kwargs):
        modulename = kwargs.get('mod', 'default')
        if modulename == '':
            return super(Entity, cls).__new__(cls)
        else:
            fully_qualified_modulename = settings.ENTITY_MODEL.get(modulename)
            components = fully_qualified_modulename.split('.')
            classname = components[len(components)-1]
            modulename = ('.').join(components[0:len(components)-1])
            kwargs['mod'] = ''
            mod = __import__(modulename, globals(), locals(), [classname], -1)
            if issubclass(getattr(mod, classname), Entity):
                return getattr(mod, classname)(*args, **kwargs)
            else:
                raise Exception('The class "%s" defined in settings.ENTITY_MODEL must be a subclass of arches.app.models.entity.Entity' % fully_qualified_modulename)

    def __init__(self, *args, **kwargs):
        self.property = ''
        self.entitytypeid = ''
        self.entityid = ''
        self.value = ''
        self.relatedentities = [
            # contains an array of other entities
        ]      

        if len(args) != 0:
            if isinstance(args[0], basestring):
                try:
                    uuid.UUID(args[0])
                    self.get(args[0])
                except(ValueError):
                    self.load(JSONDeserializer().deserialize(args[0]))  
            elif isinstance(args[0], Entity):
                self = args[0]
            elif isinstance(args[0], object):
                self.load(args[0])  
        #print self

    def __repr__(self):
        return ('%s: %s of type %s with value "%s"') % (self.__class__, self.entityid, self.entitytypeid, self.value)

    def get(self, pk, parent=None, showlabels=False):
        """
        Gets a complete entity graph for a single entity instance given an entity id
        If a parent is given, will attempt to lookup the rule used to relate parent to child

        if showlabels = True, then concept uuids and related asset uuids will be replaced with their
        labels or primary display names respectively

        """

        entity = archesmodels.Entities.objects.get(pk = pk)
        self.entitytypeid = entity.entitytypeid_id
        self.entityid = entity.pk
        
        # get the entity value if any
        if entity.entitytypeid.businesstablename != None:
            themodel = self._get_model(entity.entitytypeid.businesstablename)
            themodelinstance = themodel.objects.get(pk = pk)
            columnname = entity.entitytypeid.getcolumnname()

            if (isinstance(themodelinstance, archesmodels.Domains)): 
                if showlabels:             
                    self.value = themodelinstance.getlabelvalue()  
                else:
                    self.value = themodelinstance.getlabelid() 
            else:
                self.value = getattr(themodelinstance, columnname, 'Entity %s could not be found in the table %s' % (pk, entity.entitytypeid.businesstablename))                   
                
        # get the property that related parent to child
        if parent is not None:
            relation = archesmodels.Relations.objects.get(entityiddomain =  parent.entityid, entityidrange = entity.entityid)
            self.property = relation.ruleid.propertyid_id                
        
        # get the related entities if any
        relatedentities = archesmodels.Relations.objects.filter(entityiddomain = pk)
        for relatedentity in relatedentities:       
            self.append_child(Entity().get(relatedentity.entityidrange_id, entity, showlabels))

        return self

    @transaction.commit_on_success
    def save(self, username=''):
        """
        Saves an entity back to the db wrapped in a transaction
        We can't simply apply the decorator to the _save method 
        because of the recursive nature of the save process

        """
        now = datetime.now()
        # first we remove any entities from the current entity graph that have been deleted
        if self.entityid != '':
            entity_pre_save = Entity().get(self.entityid)
            diff = entity_pre_save.diff(self)

            for entity in diff['deleted_nodes']:             
                entity.delete()

        self._save()
        return self

    def _save(self):
        """
        Saves an entity back to the db, returns a DB model instance, not an instance of self

        """

        entitytype = archesmodels.EntityTypes.objects.get(pk = self.entitytypeid)
        try:
            uuid.UUID(self.entityid)
        except(ValueError):
            self.entityid = str(uuid.uuid4())

        domainentity = archesmodels.Entities()
        domainentity.createtms = datetime.now()
        domainentity.entitytypeid = entitytype
        domainentity.entityid = self.entityid
        domainentity.save()

        columnname = domainentity.entitytypeid.getcolumnname()
        if columnname != None:
            themodel = self._get_model(domainentity.entitytypeid.businesstablename)
            themodelinstance = themodel()
            themodelinstance.entityid = domainentity
            if(domainentity.entitytypeid.businesstablename == 'files'):
                # Saving of files must be handled specially
                # Because on subsequent saves of a file resource, we post back the file path url (instead of posting the file like we originally did),
                # we want to prevent the path from being saved back to the database thus screwing up the file save process 
                if isinstance(self.value, (InMemoryUploadedFile, TemporaryUploadedFile)):
                    setattr(themodelinstance, columnname, self.value)
                    themodelinstance.save()
                    self.value = themodelinstance.geturl()
            else:
                setattr(themodelinstance, columnname, self.value)
                themodelinstance.save()
            if(domainentity.entitytypeid.businesstablename == 'domains'):
                self.value = themodelinstance.getlabelid()

        for entity in self.relatedentities:
            rangeentity = entity._save()
            rule = archesmodels.Rules.objects.get(entitytypedomain = domainentity.entitytypeid, entitytyperange = rangeentity.entitytypeid, propertyid = entity.property)
            newrelationship = archesmodels.Relations()
            newrelationship.entityiddomain = domainentity
            newrelationship.entityidrange = rangeentity
            newrelationship.ruleid = rule
            newrelationship.save()

        return domainentity

    @transaction.commit_on_success
    def delete(self, delete_root=False):
        """
        Deltes an entity from the db wrapped in a transaction 
        """

        self._delete(delete_root)

    def _delete(self, delete_root=False):
        """
        Deletes this entity and all it's children.  
        Also attempts to delete the highest parent (and any nodes on the way) of this node when I'm the only child and 
        my parent has no value.

        if delete_root is False prevent the root node from deleted

        """

        nodes_to_delete = []

        # gather together a list of all entities that includes self and all its children
        def gather_entities(entity):
            nodes_to_delete.append(entity)
        self.traverse(gather_entities)
        
        # delete the remaining entities
        for entity in nodes_to_delete:
            self_is_root = entity.get_rank() == 0

            if self_is_root and delete_root:
                dbentity = archesmodels.Entities.objects.get(pk = entity.entityid)
                #print 'deleting root: %s' % dbentity
                dbentity.delete()
            else:
                parent = entity.get_parent()
                parent_is_root = parent.get_rank() == 0              
                # print 'deleting: %s' % JSONSerializer().serializeToPython(entity, ensure_ascii=True, indent=4)
                dbentity = archesmodels.Entities.objects.filter(pk = entity.entityid)
                if len(dbentity) == 1:
                    dbentity[0].delete()
                    parent.relatedentities.remove(entity)
                    # print 'deleted: %s' % dbentity[0]
                    # print 'parent: %s' % JSONSerializer().serializeToPython(parent, ensure_ascii=True, indent=4)
            
                # now try and remove this entity's parent 
                if len(parent.relatedentities) == 0 and parent.value == '' and not parent_is_root:
                    #print 'trying to delete parent node'
                    parent._delete()  

    def load(self, E):
        """
        Populate an Entity instance from a generic python object 

        """

        self.property = E.get('property', '')
        self.entitytypeid = E.get('entitytypeid', '')
        self.entityid = E.get('entityid', '')
        self.value = E.get('value', '')
        for entity in E.get('relatedentities', []):
            relatedentity = Entity()
            if entity['entitytypeid'] == 'PLACE.E53': print 'in load'
            self.append_child(relatedentity.load(entity))
        return self

    def add_related_entity(self, entitytypeid, property, value, entityid):
        """
        Add a related entity to this entity instance

        """     

        node = Entity()
        node.property = property
        node.entitytypeid = entitytypeid
        node.value = value
        node.entityid = entityid
        # if entitytypeid == 'PLACE.E53': print 'in add related entity'
        self.append_child(node)
        return node

    def append_child(self, entity):
        """
        Append a related entity to this entity instance

        """
        parent = self        
        # if self.entitytypeid == 'PLACE.E53': print 'assigning parent:id:%s -- %s' % (id(self), self)
        # if parent.entitytypeid == 'PLACE.E53': print 'assigning parent2:id:%s -- %s' % (id(parent), parent)
        def func(self):
            # if parent.entitytypeid == 'PLACE.E53': print 'get parent:id:%s -- %s' % (id(parent), parent)
            return parent

        entity.get_parent = types.MethodType(func, entity, Entity)
        if entity not in self.relatedentities:
            self.relatedentities.append(entity)

    def equals(self, entitytocompare, strict=False):
        """
        Test to compare if 2 entities are equal, if strict=True then compare node values as well

        """
        if (self.entitytypeid == entitytocompare.entitytypeid and self.entityid == entitytocompare.entityid and self.property == entitytocompare.property):
            if strict:
                if self.value == entitytocompare.value:
                    return True
            else:
                return True
        return False

    def merge(self, entitytomerge):
        """
        Merge an entity graph into this instance at the lowest common node

        """        

        # if the nodes are equal attempt a merge otherwise don't bother
        if (self.entitytypeid == entitytomerge.entitytypeid and self.property == entitytomerge.property and entitytomerge.entityid == ''):
            # if the value of each node is not blank then the nodes can't be merged
            # and we simply append entitytomerge node to self's parent node
            if self.value != '' and entitytomerge.value != '':
                self.get_parent().append_child(entitytomerge)
                return self

            # update self.value if it makes sense to do so  
            if self.value == '' and entitytomerge.value != '':
                self.value = entitytomerge.value

            relatedentitiesmerged = []
            # try to merge any relatedentities of self and entitytomerge 
            for relatedentitytomerge in entitytomerge.relatedentities:
                for relatedentity in self.relatedentities:
                    if (relatedentity.entitytypeid == relatedentitytomerge.entitytypeid and relatedentity.property == relatedentitytomerge.property and relatedentitytomerge.entityid == ''):   
                        relatedentity.merge(relatedentitytomerge)
                        relatedentitiesmerged.append(relatedentitytomerge)

            # append all entitytomerge.relatedentities that weren't merged above
            for relatedentity in list(set(entitytomerge.relatedentities)-set(relatedentitiesmerged)):
                self.append_child(relatedentity)
        else:
            self.get_parent().append_child(entitytomerge)
        return self

    def merge_at(self, entitytomerge, entitytypeid):
        """
        Merge an entity graph into this instance at the node type specified
        If the node can't be found in self then merge the entity graph at Root

        """

        selfEntities = self.find_entities_by_type_id(entitytypeid)
        foundEntities = entitytomerge.find_entities_by_type_id(entitytypeid)
        if len(selfEntities) == 1 and len(foundEntities) == 1:
            for foundEntity in foundEntities[0].relatedentities:
                selfEntities[0].append_child(foundEntity)
        
        # if you can't find the merge node in self then just merge at Root
        if len(selfEntities) == 0 and len(foundEntities) == 1:
            self.merge_at(entitytomerge, self.entitytypeid)

        return self

    def diff(self, entitytotest):
        """
        Find all the entities in self that don't exist in entitytotest 
        (this represents entities that have effectively been deleted from entitytotest 
        when entitytotest is a version of self)

        """
        
        ret = {'deleted_nodes':[], 'updated_nodes':[]}

        def find_diffs(self_entity):
            found_nodes = []
            updated_nodes = []
            
            def find_matching_entity(entitytotest_entity):
                if self_entity.entityid == entitytotest_entity.entityid: 
                    found_nodes.append(self_entity.entityid)
                    if self_entity.value != entitytotest_entity.value: 
                        updated_nodes.append({'from': self_entity, 'to': entitytotest_entity})
                    return False

            entitytotest.traverse(find_matching_entity)
            if len(found_nodes) == 0: # meaning it wasn't found
                ret['deleted_nodes'].append(self_entity)
            if len(updated_nodes) == 1: # meaning it was updated
                ret['updated_nodes'].append(updated_nodes[0])

        self.traverse(find_diffs)
        return ret

    def flatten(self):
        """
        flattens the graph into a list of unordered entities

        """
        ret = []
        def gather_entities(entity):
            entity.relatedentities = []
            if entity.get_rank() != 0:
                entity.parentid = entity.get_parent().entityid
            else:
                entity.parentid = None
            ret.append(entity)

        self.traverse(gather_entities)
        return ret

    def find_entities_by_type_id(self, entitytypeid):
        """
        Gets a list of entities within this instance of a given type

        """
        ret = []
        def appendValue(entity):
            if entity.entitytypeid == entitytypeid:
                ret.append(entity)
                
        if self.valid_entity_type_id(entitytypeid):
            self.traverse(appendValue)
        return ret

    def traverse(self, func, scope=None):
        """
        Traverses a graph from leaf to root calling the given function on each node
        passes an optional scope to each function

        Return False from the function to prematurely end the traversal

        """

        for relatedentity in self.relatedentities:
            if relatedentity.traverse(func, scope) == False: 
                break

        if scope == None:
            ret = func(self)
        else:
            ret = func(self, scope) 
        
        # break out of the traversal if the function returns False
        if ret == False:
            return False        

    def valid_entity_type_id(self, entitytypeid):
        """
        Test to determine if this entity has a properly formed type id

        """
        if isinstance(entitytypeid, basestring):
            if '.' in entitytypeid:
                return True
        raise Exception('Invalid entitytypeid: %s' % (entitytypeid))

    def get_rank(self, rank=0):
        """
        Get the rank of this instance (root is 0)

        """
        if hasattr(self, 'get_parent'):
            return self.get_parent().get_rank(rank+1)
        return rank

    def get_root(self):
        """
        Get the root node of this instance

        """
        if hasattr(self, 'get_parent'):
            return self.get_parent().get_root()
        return self

    def set_entity_value(self, entitytypeid, value, append=False):
        """

        """

        entities = self.find_entities_by_type_id(entitytypeid)

        if append or len(entities) == 0:
            schema = Entity.get_mapping_schema(self.entitytypeid)
            entity = Entity()
            entity.create_from_mapping(self.entitytypeid, schema[entitytypeid]['steps'], entitytypeid, value)
            self.merge_at(entity, schema[entitytypeid]['mergenodeid'])
            return entity

        if len(entities) == 1:
            entities[0].value = value 
            return entities[0]

    def create_from_mapping(self, entitytypeid, mappingsteps, leafentitytypeid, leafvalue):
        currentEntity = self
        currentEntity.entitytypeid = entitytypeid
        for step in mappingsteps:
            currentEntity.entityid = ''
            value = ''
            if step['entitytyperange'] == leafentitytypeid:
                value = leafvalue
            currentEntity = currentEntity.add_related_entity(step['entitytyperange'], step['propertyid'], value, '')

    @classmethod
    def get_mapping_schema(cls, entitytypeid):
        """
        Gets a complete entity schema graph for a single entity type given an entity type id

        """

        ret = {}
        mappings = archesmodels.Mappings.objects.filter(entitytypeidfrom = entitytypeid)

        for mapping in mappings:
            if mapping.entitytypeidto.pk not in ret:
                ret[mapping.entitytypeidto.pk] = {'steps':[], 'mergenodeid': mapping.mergenodeid}

            ret[mapping.entitytypeidto.pk]['steps'] = (Entity._get_mappings(mapping.pk))

        return ret

    @classmethod
    def _get_mappings(cls, mappingid):
        """
        Gets a single mapping given an mapping id

        """

        ret = []
        cursor = connection.cursor()
        cursor.execute("""
            SELECT 
              rules.entitytypedomain, 
              rules.entitytyperange, 
              rules.propertyid, 
              mapping_steps."order", 
              mappings.entitytypeidfrom, 
              mappings.entitytypeidto, 
              mapping_steps.mappingid
            FROM 
              ontology.rules, 
              ontology.mapping_steps, 
              ontology.mappings
            WHERE 
              mapping_steps.ruleid = rules.ruleid AND
              mappings.mappingid = '%s' AND
              mappings.mappingid = mapping_steps.mappingid
            ORDER BY
              mappings.entitytypeidfrom ASC, 
              mappings.entitytypeidto ASC, 
              mappings.mappingid ASC, 
              mapping_steps."order" ASC;
        """ % (mappingid))
        mapping_steps = cursor.fetchall()

        for mapping_step in mapping_steps:
            rule = {}
            rule['entitytypedomain'] = mapping_step[0]
            rule['entitytyperange'] = mapping_step[1]
            rule['propertyid'] = mapping_step[2]

            ret.append(rule)

        return ret

    def get_primary_display_name(self):
        """
        Gets the human readable name to display for entity instances

        """
        pass

    def get_alternate_display_names(self):
        """
        Gets the human readable name to display for entity instances

        """

        pass

    def index(self):
        """
        Gets a SearchResult object for a given asset entity
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
            for name in self.get_primary_display_name():
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
        assumes that self is an asset entity

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

    def prune(self, entitytypes, action='disallow'):
        """
        entitytypes is a list of entitytypeids allowed or dissallowed in the graph

        if action=disallow (the default) then prune will remove all entities and their children from the entity graph that match the list of provided entitytypes
        if action=allow then prune will pass through all entities and their parents from the entity graph that match the list of provided entitytypes

        .. code-block:: python

            # simple example of prunning a graph
            entity.prune(['ARCHES RECORD.E31', 'PHASE TYPE ASSIGNMENT.E17', 'SPATIAL COORDINATES_GEOMETRY.E47', 'NAME.E41'])
            
            # a more fully formed example of prunning a graph based on user permissions
            fullgraph = set(entity.flatten())
            from django.contrib.auth.models import User
            user = User.objects.get(pk=1)
            print user
            if not user.is_superuser:
                permissions = user.get_all_permissions()
                entitytypes = []
                for permission in permissions:
                    if permission.startswith('%s.read_' % entity.entitytypeid):
                        print permission.split('%s.read_' % entity.entitytypeid)[1]
                        entitytypes.append(permission.split('%s.read_' % entity.entitytypeid)[1])

                entity.prune(entitytypes, action='allow')
                prunedgraph = set(entity.flatten())
                print fullgraph.intersection(prunedgraph)
                print fullgraph.issuperset(prunedgraph)
                print fullgraph.symmetric_difference(prunedgraph)

        """

        parent_entitytypes = set()
        flattened_graph = self.flatten()
        entities_to_prune = set()        

        def gather_parent_entitytypes(entity):
            if entity.get_rank() == 0:
                return
            parent_entity = entity.get_parent()
            parent_entitytypes.add(parent_entity.entitytypeid)
            gather_parent_entitytypes(parent_entity)

        if action == 'disallow':
            for entity in flattened_graph:
                if entity.entitytypeid in entitytypes:
                    entities_to_prune.add(entity)

        else:
            # if you passed in no entitytypes then you're basically saying remove all information from the graph
            if len(entitytypes) == 0:
                self.clear()
                return

            # first we need to loop through the graph to all the parents of entity to the list of allowed entitytypes
            for entity in flattened_graph:
                if entity.entitytypeid in entitytypes:
                    gather_parent_entitytypes(entity)

            entitytypes = entitytypes + list(parent_entitytypes)
            for entity in flattened_graph:
                if entity.entitytypeid not in entitytypes:
                    entities_to_prune.add(entity)
    
        # prune the remaining entities
        print 'entities to prune: %s' % entities_to_prune
        for entity in entities_to_prune:
            print entity
            try:
                parent = entity.get_parent()   
                print '\nremoving: %s' % entity         
                parent.relatedentities.remove(entity) 
            except:
                if entity.get_rank() == 0:
                    self.clear()
                    return

        self.trim()

    def trim(self):
        """
        recusrsively removes all nodes starting from the leaf that have no relatedentities and no value
        these nodes are assumed to be of no material value to the graph

        """

        def func(entity):
            try:
                parent = entity.get_parent()
                if len(entity.relatedentities) == 0 and entity.value == '':
                    parent.relatedentities.remove(entity)
            except:
                pass
        self.traverse(func)

    def clear(self):
        """
        resets this entity back to a clean state (does not delete the entity from the database)

        """

        self.relatedentities = []
        self.entitytypeid = ''
        self.entityid = ''
        self.value = ''

    @staticmethod
    def _get_model(tablename):
        """
        Helper to look up a model from a table name.

        """

        try:
            model_identifier = str('models.' + tablename)
            Model = models.get_model(*model_identifier.split("."))
        except TypeError:
            Model = None
        if Model is None:
            raise TypeError(u"Invalid model identifier: '%s'" % model_identifier)
        return Model