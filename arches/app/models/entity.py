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
import types
import copy
import arches.app.models.models as archesmodels
from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.geos import fromstr
from django.db import connection
from django.db import transaction
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer


class Entity(object):
    """ 
    Used for mapping complete entity graph objects to and from the database

    """
    
    def __init__(self, *args, **kwargs):
        self.property = ''
        self.entitytypeid = ''
        self.entityid = ''
        self.value = ''
        self.label = ''
        self.businesstablename = ''
        self.child_entities = [
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
            elif args[0] != None and isinstance(args[0], object):
                self.load(args[0])  

    def __repr__(self):
        return ('%s: %s of type %s with value "%s"') % (self.__class__, self.entityid, self.entitytypeid, self.value)

    def __hash__(self): return hash(JSONSerializer().serialize(self))
    def __eq__(self, x):return hash(self) == hash(x)
    def __ne__(self, x): return hash(self) != hash(x)

    def get(self, pk, parent=None):
        """
        Gets a complete entity graph for a single entity instance given an entity id
        If a parent is given, will attempt to lookup the rule used to relate parent to child

        """

        entity = archesmodels.Entities.objects.get(pk = pk)
        self.entitytypeid = entity.entitytypeid_id
        self.entityid = entity.pk
        self.businesstablename = entity.entitytypeid.businesstablename if entity.entitytypeid.businesstablename else ''

        # get the entity value if any
        if entity.entitytypeid.businesstablename != None:
            themodel = self._get_model(entity.entitytypeid.businesstablename)
            themodelinstance = themodel.objects.get(pk = pk)
            columnname = entity.entitytypeid.getcolumnname()

            if (isinstance(themodelinstance, archesmodels.Domains)): 
                self.value = themodelinstance.getlabelid()
                self.label = themodelinstance.getlabelvalue()
            elif (isinstance(themodelinstance, archesmodels.Files)): 
                self.label = themodelinstance.getname()
                self.value = themodelinstance.geturl() 
            else:
                self.value = getattr(themodelinstance, columnname, 'Entity %s could not be found in the table %s' % (pk, entity.entitytypeid.businesstablename))                   
                self.label = self.value
                
        # get the property that associated parent to child
        if parent is not None:
            relation = archesmodels.Relations.objects.get(entityiddomain =  parent.entityid, entityidrange = entity.entityid)
            self.property = relation.ruleid.propertyid_id                
        
        # get the child entities if any
        child_entities = archesmodels.Relations.objects.filter(entityiddomain = pk)
        for child_entity in child_entities:       
            self.append_child(Entity().get(child_entity.entityidrange_id, entity))

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


        entity = archesmodels.Entities()
        entity.entitytypeid = entitytype
        entity.entityid = self.entityid
        entity.save()


        columnname = entity.entitytypeid.getcolumnname()
        if columnname != None:
            themodel = self._get_model(entity.entitytypeid.businesstablename)
            themodelinstance = themodel()
            themodelinstance.entityid = entity

            if (isinstance(themodelinstance, archesmodels.Files)): 
                # Saving of files must be handled specially
                # Because on subsequent saves of a file resource, we post back the file path url (instead of posting the file like we originally did),
                # we want to prevent the path from being saved back to the database thus screwing up the file save process 
                if isinstance(self.value, (InMemoryUploadedFile, TemporaryUploadedFile)):
                    setattr(themodelinstance, columnname, self.value)
                    themodelinstance.save()
                elif isinstance(self.value, str):
                    setattr(themodelinstance, columnname, self.value)
                    themodelinstance.save()
            else:
                setattr(themodelinstance, columnname, self.value)
                themodelinstance.save()

            self.businesstablename = entity.entitytypeid.businesstablename
            self.label = self.value
            if (isinstance(themodelinstance, archesmodels.Domains)): 
                self.value = themodelinstance.getlabelid()
                self.label = themodelinstance.getlabelvalue()
            elif (isinstance(themodelinstance, archesmodels.Files)): 
                self.value = themodelinstance.geturl()
                self.label = themodelinstance.getname()

        for child_entity in self.child_entities:
            child = child_entity._save()
            try:
                rule = archesmodels.Rules.objects.get(entitytypedomain = entity.entitytypeid, entitytyperange = child.entitytypeid, propertyid = child_entity.property)
                newrelationship = archesmodels.Relations()
                newrelationship.entityiddomain = entity
                newrelationship.entityidrange = child
                newrelationship.ruleid = rule
                newrelationship.save()
            except:
                print 'ERROR in query for the following rule: Domain={0}, Range={1}, Property={2}. Relationship could not be saved'.format(entity.entitytypeid, child.entitytypeid, entity.property)

        return entity

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
                    parent.child_entities.remove(entity)
                    # print 'deleted: %s' % dbentity[0]
                    # print 'parent: %s' % JSONSerializer().serializeToPython(parent, ensure_ascii=True, indent=4)
            
                # now try and remove this entity's parent 
                if len(parent.child_entities) == 0 and parent.value == '' and not parent_is_root:
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
        self.label = E.get('label', '')
        self.businesstablename = E.get('businesstablename', '')
        for entity in E.get('child_entities', []):
            child_entity = Entity()
            self.append_child(child_entity.load(entity))
        return self

    def add_child_entity(self, entitytypeid, property, value, entityid):
        """
        Add a child entity to this entity instance

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
        Append a child entity to this entity instance

        """
        parent = self        
        # if self.entitytypeid == 'PLACE.E53': print 'assigning parent:id:%s -- %s' % (id(self), self)
        # if parent.entitytypeid == 'PLACE.E53': print 'assigning parent2:id:%s -- %s' % (id(parent), parent)
        def func(self):
            # if parent.entitytypeid == 'PLACE.E53': print 'get parent:id:%s -- %s' % (id(parent), parent)
            return parent

        entity.get_parent = types.MethodType(func, entity, Entity)
        if entity not in self.child_entities:
            self.child_entities.append(entity)

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
        if (self.entitytypeid == entitytomerge.entitytypeid and self.property == entitytomerge.property):
            # if the value of each node is not blank then the nodes can't be merged
            # and we simply append entitytomerge node to self's parent node
            if self.value != '' and entitytomerge.value != '':
                self.get_parent().append_child(entitytomerge)
                return self

            # update self.entityid if it makes sense to do so  
            if self.entityid == '' and entitytomerge.entityid != '':
                self.entityid = entitytomerge.entityid

            # update self.value if it makes sense to do so  
            if self.value == '' and entitytomerge.value != '':
                self.value = entitytomerge.value

            child_entitiesmerged = []
            # try to merge any child_entities of self and entitytomerge 
            for child_entitytomerge in entitytomerge.child_entities:
                for child_entity in self.child_entities:
                    if (child_entity.entitytypeid == child_entitytomerge.entitytypeid and child_entity.property == child_entitytomerge.property):   
                        child_entity.merge(child_entitytomerge)
                        child_entitiesmerged.append(child_entitytomerge)

            # append all entitytomerge.child_entities that weren't merged above
            for child_entity in list(set(entitytomerge.child_entities)-set(child_entitiesmerged)):
                self.append_child(child_entity)
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
            for foundEntity in foundEntities[0].child_entities:
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

        ret = {'deleted_nodes':[], 'updated_nodes':[], 'inserted_nodes': []}

        self_flattened = set(self.flatten())
        entitytotest_flattened = set(entitytotest.flatten())

        ret['deleted_nodes'] = list(entitytotest_flattened.difference(self_flattened))
        ret['inserted_nodes'] = list(self_flattened.difference(entitytotest_flattened))

        for inserted_entity in list(self_flattened.difference(entitytotest_flattened)):
            for deleted_entity in list(entitytotest_flattened.difference(self_flattened)):
                if inserted_entity.entityid == deleted_entity.entityid:
                    ret['inserted_nodes'].remove(inserted_entity)
                    ret['deleted_nodes'].remove(deleted_entity)
                    ret['updated_nodes'].append({'from': deleted_entity, 'to': inserted_entity})

        return ret

    def copy(self):
        return copy.deepcopy(self)

    def flatten(self):
        """
        flattens the graph into a list of unordered entities

        """

        ret = []
        def gather_entities(entity):
            if entity.get_rank() != 0:
                entity.parentid = entity.get_parent().entityid
            else:
                entity.parentid = None
            ret.append(entity)

        copiedself = self.copy()
        copiedself.traverse(gather_entities)
        for item in ret:
            item.child_entities = []

        return ret

    def find_entities_by_type_id(self, entitytypeid):
        """
        Gets a list of entities within this instance of a given type

        """
        ret = []
        def appendValue(entity):
            if entity.entitytypeid == entitytypeid:
                ret.append(entity)

        self.traverse(appendValue)
        return ret

    def traverse(self, func, scope=None):
        """
        Traverses a graph from leaf to root calling the given function on each node
        passes an optional scope to each function

        Return a value from the function to prematurely end the traversal

        """

        if scope == None:
            ret = func(self)
        else:
            ret = func(self, scope) 

        # break out of the traversal if the function returns a value
        if ret != None:
            return ret   

        for child_entity in self.child_entities:
            ret = child_entity.traverse(func, scope) 
            if ret != None: 
                return ret   

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

    def create_from_mapping(self, entitytypeid, mappingsteps, leafentitytypeid, leafvalue, leafentityid=''):
        currentEntity = self
        currentEntity.entitytypeid = entitytypeid
        for step in mappingsteps:
            currentEntity.entityid = ''
            value = ''
            if step['entitytyperange'] == leafentitytypeid:
                value = leafvalue
            currentEntity = currentEntity.add_child_entity(step['entitytyperange'], step['propertyid'], value, leafentityid)
        return self

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
            try:
                parent = entity.get_parent()   
                print '\nremoving: %s' % entity         
                parent.child_entities.remove(entity) 
            except:
                if entity.get_rank() == 0:
                    self.clear()
                    return

        self.trim()

    def trim(self):
        """
        recusrsively removes all nodes starting from the leaf that have no child_entities and no value
        these nodes are assumed to be of no material value to the graph

        """

        def func(entity):
            try:
                parent = entity.get_parent()
                if len(entity.child_entities) == 0 and entity.value == '':
                    parent.child_entities.remove(entity)
            except:
                pass
        self.traverse(func)

    def clear(self):
        """
        resets this entity back to a clean state (does not delete the entity from the database)

        """

        self.child_entities = []
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


    def dictify(self, keys=['label']):
        """
        Takes an entity and turns it into recursive lists nested objects
        Uses an in-built algorithm to derive which sub-branches appear to be grouped, and then flattens them out

        A partial example output follows...

        .. code-block:: python
            [
                {
                    "EVALUATION_CRITERIA_ASSIGNMENT_E13": [{
                        "STATUS_E55": [
                            {"STATUS_E55__label": "3D"}, 
                            {"STATUS_E55__label": "3CD"}, 
                            {"STATUS_E55__label": "5D3"}
                        ]
                    }], 
                    "BEGINNING_OF_EXISTENCE_E63": [{
                        "BEGINNING_OF_EXISTENCE_TIME-SPAN_E52": [{
                            "BEGINNING_OF_EXISTENCE_TIME-SPAN_E52__label": "", 
                            "START_DATE_OF_EXISTENCE_E49__label": "1962-01-01T00:00:00"
                        }], 
                        "BEGINNING_OF_EXISTENCE_TYPE_E55": [{
                            "BEGINNING_OF_EXISTENCE_TYPE_E55__label": "Built Date"
                        }]
                    }], 
                    "NAME_E41": [{
                        "NAME_TYPE_E55__label": "Primary", 
                        "NAME_E41__label": "3264 N WRIGHTWOOD DR"
                    }], 
                    "PRODUCTION_E12": [{
                        "PHASE_TYPE_ASSIGNMENT_E17": [
                            {
                                "STYLE_E55": [{
                                        "STYLE_E55__label": "Modern, Mid-Century"
                                }], 
                                "HERITAGE_RESOURCE_TYPE_E55": [{
                                    "HERITAGE_RESOURCE_TYPE_E55__label": "HP02. Single family property"
                                    },{
                                    "HERITAGE_RESOURCE_TYPE_E55__label": "House"
                                }], 
                                "HERITAGE_RESOURCE_USE_TYPE_E55": [{
                                    "HERITAGE_RESOURCE_USE_TYPE_E55__label": "Historic"
                                }]
                            }
                        ]
                    }]
                }
            ]

        """

        data = {}
        for child_entity in self.child_entities:
            if child_entity.businesstablename != '':
                data[child_entity.undotify()] = self.get_nodes(child_entity.entitytypeid, keys=keys)
            else:
                data[child_entity.undotify()] = child_entity.dictify(keys=keys)
        return [data]

    def get_nodes(self, entitytypeid, keys=[]):
        """
        Used by dictify to gather and flatten a single node (by entitytypeid) and all it's children

        for example, a NAME.E41 node with a single child of NAME_TYPE.E55 would be transformed as below
        
        .. code-block:: python

                "NAME_E41": [{
                    "NAME_TYPE_E55__label": "Primary", 
                    "NAME_E41__label": "3264 N WRIGHTWOOD DR"
                }],

        """

        ret = []
        entities = self.find_entities_by_type_id(entitytypeid)
        for entity in entities:
            data = {}

            for entity in entity.flatten():
                data = dict(data.items() + entity.encode(keys=keys).items())
            ret.append(data)
        return ret

    def encode(self, keys=[]):
        """
        Encodes an Entity into a dictionary of keys derived by the entitytypeid of the Entity concatonated wtih property name 

        .. code-block:: python

                {
                    "NAME_TYPE_E55__label": "Primary"
                }

        """

        ret = {}

        for key, value in self.__dict__.items():
            if key in keys:
                ret['%s__%s' % (self.undotify(), key)] = value
        return ret

    def undotify(self):
        return self.undotify_entitytypeid()

    def undotify_entitytypeid(self):
        return self.entitytypeid.replace('.', '_').replace('-', '___');