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
from operator import methodcaller
from django.db import transaction
from django.db.models import Q
from arches.app.models import models
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Match, Query
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer

CORE_CONCEPTS = (
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000002',
    '00000000-0000-0000-0000-000000000003'
)

class Concept(object):
    def __init__(self, *args, **kwargs):
        self.id = ''
        self.legacyoid = ''
        self.relationshiptype = ''
        self.values = []
        self.subconcepts = []
        self.parentconcepts = []
        self.relatedconcepts = []

        if len(args) != 0:
            if isinstance(args[0], basestring):
                try:
                    uuid.UUID(args[0])
                    self.get(args[0])
                except(ValueError):
                    self.load(JSONDeserializer().deserialize(args[0]))  
            elif isinstance(args[0], dict):
                self.load(args[0])  
            elif isinstance(args[0], object):
                self.load(args[0])  

    def __unicode__(self):
        return ('%s - %s') % (self.get_preflabel().value, self.id)
    
    def load(self, value):
        if isinstance(value, dict):
            self.id = value['id'] if 'id' in value else ''
            self.legacyoid = value['legacyoid'] if 'legacyoid' in value else ''
            self.relationshiptype = value['relationshiptype'] if 'relationshiptype' in value else ''            
            if 'values' in value:
                for value in value['values']:
                    self.addvalue(value)
            if 'subconcepts' in value:
                for subconcept in value['subconcepts']:
                    self.addsubconcept(subconcept)
            if 'parentconcepts' in value:
                for parentconcept in value['parentconcepts']:
                    self.addparent(parentconcept)
            if 'relatedconcepts' in value:
                for relatedconcept in value['relatedconcepts']:
                    self.addrelatedconcept(relatedconcept)

    def get(self, id='', legacyoid='', include_subconcepts=False, include_parentconcepts=False, include_relatedconcepts=False, exclude=[], include=[], depth_limit=None, up_depth_limit=None, **kwargs):
        self.id = id if id != '' else self.id
        if self.id != '' or legacyoid != '':
            self.legacyoid = legacyoid
            uplevel = kwargs.pop('uplevel', 0)
            downlevel = kwargs.pop('downlevel', 0)
            depth_limit = depth_limit if depth_limit == None else int(depth_limit)
            up_depth_limit = up_depth_limit if up_depth_limit == None else int(up_depth_limit)

            if include != None:
                if len(include) > 0 and len(exclude) > 0:
                    raise Exception('Only include values for include or exclude, but not both')
                include = include if len(include) != 0 else models.ValueTypes.objects.distinct('category').values_list('category', flat=True)
                include = set(include).difference(exclude)
                exclude = []

                if len(include) > 0:
                    values = models.Values.objects.filter(conceptid = self.id)
                    for value in values:
                        if value.valuetype.category in include:
                            self.values.append(ConceptValue(value))

            if include_subconcepts:
                conceptrealations = models.ConceptRelations.objects.filter(Q(conceptidfrom = self.id), Q(relationtype__category = 'Semantic Relations'), ~Q(relationtype = 'related'))
                if depth_limit == None or downlevel < depth_limit:
                    if depth_limit != None:
                        downlevel = downlevel + 1                
                    for relation in conceptrealations:
                        self.relationshiptype = relation.relationtype.pk
                        self.subconcepts.append(Concept().get(id=relation.conceptidto_id, include_subconcepts=include_subconcepts, 
                            include_parentconcepts=include_parentconcepts, include_relatedconcepts=include_relatedconcepts, exclude=exclude, include=include, depth_limit=depth_limit, 
                            up_depth_limit=up_depth_limit, downlevel=downlevel, uplevel=uplevel))

                    self.subconcepts = sorted(self.subconcepts, key=methodcaller('get_sortkey', lang='en-us'), reverse=False) 

            if include_parentconcepts:
                conceptrealations = models.ConceptRelations.objects.filter(Q(conceptidto = self.id), Q(relationtype__category = 'Semantic Relations'))
                if up_depth_limit == None or uplevel < up_depth_limit:
                    if up_depth_limit != None:
                        uplevel = uplevel + 1          
                    for relation in conceptrealations:
                        self.parentconcepts.append(Concept().get(id=relation.conceptidfrom_id, include_subconcepts=False, 
                            include_parentconcepts=include_parentconcepts, include_relatedconcepts=include_relatedconcepts, 
                            exclude=exclude, include=include, depth_limit=depth_limit, 
                            up_depth_limit=up_depth_limit, downlevel=downlevel, uplevel=uplevel))

            if include_relatedconcepts:
                conceptrealations = models.ConceptRelations.objects.filter(Q(relationtype = 'related') | Q(relationtype__category = 'Mapping Properties'), Q(conceptidto = self.id) | Q(conceptidfrom = self.id))
                for relation in conceptrealations:
                    if relation.conceptidto_id != self.id:
                        self.relatedconcepts.append(Concept().get(relation.conceptidto_id, include=['label']).get_preflabel())
                    if relation.conceptidfrom_id != self.id:
                        self.relatedconcepts.append(Concept().get(relation.conceptidfrom_id, include=['label']).get_preflabel())

        return self
            
    def save(self):
        with transaction.atomic():
            self.id = self.id if (self.id != '' and self.id != None) else str(uuid.uuid4())
            concept, created = models.Concepts.objects.get_or_create(pk=self.id, defaults={'legacyoid': self.legacyoid})

            for parentconcept in self.parentconcepts:
                parentconcept.save()
                conceptrelation = models.ConceptRelations()
                conceptrelation.pk = str(uuid.uuid4())
                conceptrelation.conceptidfrom_id = parentconcept.id 
                conceptrelation.conceptidto = concept
                conceptrelation.relationtype_id = parentconcept.relationshiptype
                conceptrelation.save()

            for subconcept in self.subconcepts:
                subconcept.save()
                conceptrelation = models.ConceptRelations()
                conceptrelation.pk = str(uuid.uuid4())
                conceptrelation.conceptidfrom = concept
                conceptrelation.conceptidto_id = subconcept.id
                conceptrelation.relationtype_id = subconcept.relationshiptype
                conceptrelation.save()

            for relatedconcept in self.relatedconcepts:
                relation = models.ConceptRelations()
                relation.pk = str(uuid.uuid4())
                relation.conceptidfrom_id = self.id
                relation.conceptidto_id = relatedconcept.id
                relation.relationtype_id = 'related'
                relation.save()

            for value in self.values:
                if not isinstance(value, ConceptValue): 
                    value = ConceptValue(value)
                value.conceptid = self.id
                value.save()

            return concept

    def delete(self, delete_self=False):
        with transaction.atomic():
            for subconcept in self.subconcepts:
                concepts_to_delete = Concept.gather_concepts_to_delete(subconcept.id)
                
                for concept in concepts_to_delete:
                    models.Concepts.objects.get(pk=concept.conceptid).delete()

            for parentconcept in self.parentconcepts:
                conceptrelations = models.ConceptRelations.objects.filter(relationtype__category = 'Semantic Relations', conceptidfrom = parentconcept.id, conceptidto = self.id)
                for relation in conceptrelations:
                    relation.delete()

            for relatedconcept in self.relatedconcepts:
                deletedrelatedconcepts = []
                for relatedconcept in self.relatedconcepts:
                    conceptrelations = models.ConceptRelations.objects.filter(Q(relationtype = 'related') | Q(relationtype__category = 'Mapping Properties'), conceptidto = relatedconcept.id, conceptidfrom = self.id)
                    for relation in conceptrelations:
                        relation.delete()
                        deletedrelatedconcepts.append(relatedconcept)

                    conceptrelations = models.ConceptRelations.objects.filter(Q(relationtype = 'related') | Q(relationtype__category = 'Mapping Properties'), conceptidfrom = relatedconcept.id, conceptidto = self.id)
                    for relation in conceptrelations:
                        relation.delete()
                        deletedrelatedconcepts.append(relatedconcept)

                for deletedrelatedconcept in deletedrelatedconcepts:
                    if deletedrelatedconcept in self.relatedconcepts:
                        self.relatedconcepts.remove(deletedrelatedconcept)

            for value in self.values:
                if not isinstance(value, ConceptValue): 
                    value = ConceptValue(value)
                value.delete()

            if delete_self:
                models.Concepts.objects.get(pk=self.id).delete()
        return

    @staticmethod
    def gather_concepts_to_delete(conceptid):
        concepts_to_delete = []
        concept = Concept().get(id=conceptid, include_subconcepts=True, include_parentconcepts=True, include=['label'], up_depth_limit=1)
        
        def find_concepts(concept):
            if len(concept.parentconcepts) <= 1:
                concepts_to_delete.append(concept.get_preflabel())
                for subconcept in concept.subconcepts:
                    find_concepts(subconcept)

        find_concepts(concept)
        return concepts_to_delete

    def traverse(self, func, scope=None):
        """
        Traverses a graph from leaf to root calling the given function on each node
        passes an optional scope to each function

        Return False from the function to prematurely end the traversal

        """

        if scope == None:
            ret = func(self)
        else:
            ret = func(self, scope) 
        
        # break out of the traversal if the function returns False
        if ret == False:
            return False    

        for subconcept in self.subconcepts:
            if subconcept.traverse(func, scope) == False: 
                break

    def get_sortkey(self, lang='en-us'):
        for value in self.values:
            if value.type == 'sortorder':
                return value.value
                
        return self.get_preflabel(lang=lang).value

    def get_auth_doc_concept(self, lang='en-us'):
        scheme_collections = [collection.id for collection in Concept.get_scheme_collections()]
        concept = Concept().get(id=self.id, include_subconcepts=False, include_parentconcepts=True)
       
        def find_auth_doc(concept):
            for parentconcept in concept.parentconcepts:
                if parentconcept.id in scheme_collections:
                    return concept

            for parentconcept in concept.parentconcepts:
                return find_auth_doc(parentconcept)

        auth_doc = find_auth_doc(concept)
        return auth_doc

    def get_preflabel(self, lang='en-us'):
        ret = ConceptValue()       
        if self.values == []: 
            concept = Concept().get(id=self.id, include_subconcepts=False, include_parentconcepts=False, include=['label'])
        else:
            concept = self
        for value in concept.values:
            ret = value.value
            if value.type == 'prefLabel':
                ret = value.value
                if value.language == lang:
                    return value
        return ret

    def flatten(self, ret=None):
        """
        Flattens the graph into a unordered list of concepts

        """

        if ret == None:
            ret = []

        ret.append(self)
        for subconcept in self.subconcepts:
            subconcept.flatten(ret)
            
        return ret

    def addparent(self, value):
        if isinstance(value, dict):
            self.parentconcepts.append(Concept(value))
        elif isinstance(value, Concept):
            self.parentconcepts.append(value)
        else:
            raise Exception('Invalid parent concept definition: %s' % (value))

    def addsubconcept(self, value):
        if isinstance(value, dict):
            self.subconcepts.append(Concept(value))
        elif isinstance(value, Concept):
            self.subconcepts.append(value)
        else:
            raise Exception('Invalid subconcept definition: %s' % (value))

    def addrelatedconcept(self, value):
        if isinstance(value, dict):
            self.relatedconcepts.append(Concept(value))
        elif isinstance(value, Concept):
            self.relatedconcepts.append(value)
        else:
            raise Exception('Invalid related concept definition: %s' % (value))

    def addvalue(self, value):
        if isinstance(value, dict):
            value['conceptid'] = self.id
            self.values.append(ConceptValue(value))
        elif isinstance(value, ConceptValue):
            self.values.append(value)
        else:
            raise Exception('Invalid value definition: %s' % (value))

    def index(self, scheme=''):
        for value in self.values:
            value.index(scheme=scheme)        

        for subconcept in self.subconcepts:
            if subconcept.is_scheme():
                subconcept.index(scheme=subconcept.id)
            else:
                if scheme == '':
                    scheme = self.get_auth_doc_concept().id
                subconcept.index(scheme=scheme)

    def delete_index(self, delete_self=False):
        se = SearchEngineFactory().create()
        
        for subconcept in self.subconcepts:
            concepts_to_delete = Concept.gather_concepts_to_delete(subconcept.id)

            for concept in concepts_to_delete:
                query = Query(se, start=0, limit=10000)
                phrase = Match(field='conceptid', query=concept.conceptid, type='phrase')
                query.add_query(phrase)
                query.delete(index='concept_labels')

        for value in self.values:
            value.delete_index()

    def concept_tree(self, top_concept='00000000-0000-0000-0000-000000000001'):
        class concept(object):
            def __init__(self, *args, **kwargs):
                self.label = ''
                self.labelid = ''
                self.id = ''
                self.load_on_demand = False
                self.children = []    

        def _findNarrowerConcept(conceptid, depth_limit=None, level=0):
            labels = models.Values.objects.filter(conceptid = conceptid)
            ret = concept()          
            for label in labels:
                if label.valuetype_id == 'prefLabel':
                    ret.label = label.value
                    ret.id = label.conceptid_id
                    ret.labelid = label.valueid

            conceptrealations = models.ConceptRelations.objects.filter(Q(conceptidfrom = conceptid), ~Q(relationtype = 'has related concept'))
            if depth_limit != None and len(conceptrealations) > 0 and level >= depth_limit:
                ret.load_on_demand = True
            else:
                if depth_limit != None:
                    level = level + 1                
                for relation in conceptrealations:
                    ret.children.append(_findNarrowerConcept(relation.conceptidto_id, depth_limit=depth_limit, level=level))   

            return ret 

        def _findBroaderConcept(conceptid, child_concept, depth_limit=None, level=0):
            conceptrealations = models.ConceptRelations.objects.filter(Q(conceptidto = conceptid), ~Q(relationtype = 'has related concept'))
            if len(conceptrealations) > 0 and conceptid != top_concept:
                labels = models.Values.objects.filter(conceptid = conceptrealations[0].conceptidfrom_id)
                ret = concept()          
                for label in labels:
                    if label.valuetype_id == 'prefLabel':
                        ret.label = label.value
                        ret.id = label.conceptid_id
                        ret.labelid = label.valueid

                ret.children.append(child_concept)
                return _findBroaderConcept(conceptrealations[0].conceptidfrom_id, ret, depth_limit=depth_limit, level=level)
            else:
                return child_concept
        
        if self.id == None or self.id == '' or self.id == top_concept:
            concepts = [_findNarrowerConcept(top_concept, depth_limit=1)]
        else:
            concepts = _findNarrowerConcept(self.id, depth_limit=1)
            concepts = [_findBroaderConcept(self.id, concepts, depth_limit=1)]

        return concepts

    def get_paths(self, lang='en-us'):
        def graph_to_paths(current_concept, path=[], path_list=[[]]):
            parents = current_concept.parentconcepts
            for parent in parents:
                current_path = path[:]
                if len(parent.parentconcepts) == 0:
                    path_list.append(current_path)
                current_path.insert(0, {'label': parent.get_preflabel(lang=lang).value, 'relationshiptype': parent.relationshiptype, 'id': parent.id})
                graph_to_paths(parent, current_path, path_list)
            return path_list

        return graph_to_paths(self)

    def get_node_and_links(self, lang='en-us'):
        nodes = [{'concept_id': self.id, 'name': self.get_preflabel(lang=lang).value,'type': 'Current'}]
        links = []

        def get_parent_nodes_and_links(current_concept):
            parents = current_concept.parentconcepts
            for parent in parents:
                nodes.append({'concept_id': parent.id, 'name': parent.get_preflabel(lang=lang).value, 'type': 'Root' if len(parent.parentconcepts) == 0 else 'Ancestor'})
                links.append({'target': current_concept.id, 'source': parent.id, 'relationship': 'broader' })
                get_parent_nodes_and_links(parent)

        get_parent_nodes_and_links(self)
        for child in self.subconcepts:
            nodes.append({'concept_id': child.id, 'name': child.get_preflabel(lang=lang).value,'type': 'Descendant' })
            links.append({'source': self.id, 'target': child.id, 'relationship': 'narrower' })

        # get unique node list and assign unique integer ids for each node (required by d3)
        nodes = {node['concept_id']:node for node in nodes}.values()
        for i in range(len(nodes)):
            nodes[i]['id'] = i
            for link in links:
                link['source'] = i if link['source'] == nodes[i]['concept_id'] else link['source']
                link['target'] = i if link['target'] == nodes[i]['concept_id'] else link['target']
        
        return {'nodes': nodes, 'links': links}
 
    def is_scheme(self):
        scheme_collection_ids = []
        for concept in Concept.get_scheme_collections(depth=2):
            for subconcepts in concept.subconcepts:
                scheme_collection_ids.append(subconcepts.id)

        if self.id in scheme_collection_ids:
            return True
        else:
            return False

    @staticmethod
    def get_scheme_collections(include=None, depth=1):
        return Concept().get(id='00000000-0000-0000-0000-000000000003', include_subconcepts=True, depth_limit=depth, include=include).subconcepts

class ConceptValue(object):
    def __init__(self, *args, **kwargs):
        self.id = ''
        self.conceptid = ''
        self.datatype = ''
        self.type = ''
        self.category = ''
        self.value = ''
        self.language = ''  

        if len(args) != 0:
            if isinstance(args[0], basestring):
                try:
                    uuid.UUID(args[0])
                    self.get(args[0])
                except(ValueError):
                    self.load(JSONDeserializer().deserialize(args[0]))  
            elif isinstance(args[0], object):
                self.load(args[0])  


    def get(self, id=''):
        self.load(models.Values.objects.get(pk = id))
        return self

    def save(self):
        self.id = self.id if (self.id != '' and self.id != None) else str(uuid.uuid4())
        value = models.Values()
        value.pk = self.id
        value.value = self.value
        value.conceptid_id = self.conceptid # models.Concepts.objects.get(pk=self.conceptid)
        value.valuetype_id = self.type # models.ValueTypes.objects.get(pk=self.type)
        value.datatype = self.datatype
        if self.language != '':
            value.languageid_id = self.language # models.DLanguages.objects.get(pk=self.language)
        value.save()

    def delete(self):
        if self.id != '':
            newvalue = models.Values.objects.get(pk=self.id)
            newvalue.delete()
            self = ConceptValue()
            return self
    
    def load(self, value):
        if isinstance(value, models.Values):
            self.id = value.pk
            self.conceptid = value.conceptid.pk
            self.datatype = value.datatype
            self.type = value.valuetype.pk
            self.category = value.valuetype.category
            self.value = value.value
            self.language = value.languageid_id

        if isinstance(value, dict):
            self.id = value['id'] if 'id' in value else ''
            self.conceptid = value['conceptid'] if 'conceptid' in value else ''
            self.datatype = value['datatype'] if 'datatype' in value else ''
            self.type = value['type'] if 'type' in value else ''
            self.category = value['category'] if 'category' in value else ''
            self.value = value['value'] if 'value' in value else ''
            self.language = value['language'] if 'language' in value else ''

    def index(self, scheme=None):
        if self.category == 'label':
            se = SearchEngineFactory().create()
            data = JSONSerializer().serializeToPython(self)          
            if scheme == None:
                scheme = self.get_scheme_id()
            if scheme == None:
                raise Exception('Index of label failed.  Index type (scheme id) could not be derived from the label.')
            se.index_data('concept_labels', scheme, data, 'id')
    
    def delete_index(self):      
        if self.category == 'label':
            se = SearchEngineFactory().create()
            if self.category == '':
                raise Exception('Delete index failed.  Remember to specify a category for your value. %s' % JSONSerializer().serialize(self))
            scheme = self.get_scheme_id()
            if scheme == None:
                raise Exception('Delete label index failed.  Index type (scheme id) could not be derived from the label.')
            se. ht9km (index='concept_labels', type=scheme, id=self.id)

    def get_scheme_id(self):
        se = SearchEngineFactory().create()
        result = se.search(index='concept_labels', id=self.id)
        if not result['found']:
            return None
        else:
            return result['_type']