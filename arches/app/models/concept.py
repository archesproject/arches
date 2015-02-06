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
import copy
from operator import itemgetter
from operator import methodcaller
from django.db import transaction, connection
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
        self.nodetype = ''
        self.legacyoid = ''
        self.relationshiptype = ''
        self.values = []
        self.subconcepts = []
        self.parentconcepts = []
        self.relatedconcepts = []
        self.hassubconcepts = False

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
            self.nodetype = value['nodetype'] if 'nodetype' in value else ''
            self.legacyoid = value['legacyoid'] if 'legacyoid' in value else ''
            self.relationshiptype = value['relationshiptype'] if 'relationshiptype' in value else ''            
            if 'values' in value:
                for val in value['values']:
                    self.addvalue(val)
            if 'subconcepts' in value:
                for subconcept in value['subconcepts']:
                    self.addsubconcept(subconcept)
            if 'parentconcepts' in value:
                for parentconcept in value['parentconcepts']:
                    self.addparent(parentconcept)
            if 'relatedconcepts' in value:
                for relatedconcept in value['relatedconcepts']:
                    self.addrelatedconcept(relatedconcept)

        if isinstance(value, models.Concepts):
            self.id = value.pk
            self.nodetype = value.nodetype_id
            self.legacyoid = value.legacyoid

    def get(self, id='', legacyoid='', include_subconcepts=False, include_parentconcepts=False, include_relatedconcepts=False, exclude=[], include=[], depth_limit=None, up_depth_limit=None, lang='en-us', **kwargs):
        if id != '':
            self.load(models.Concepts.objects.get(pk=id))
        elif legacyoid != '':
            self.load(models.Concepts.objects.get(legacyoid=legacyoid))

        if self.id != '':
            nodetype = kwargs.pop('nodetype', self.nodetype)
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

            hassubconcepts = models.ConceptRelations.objects.filter(Q(conceptidfrom = self.id), Q(relationtype__category = 'Semantic Relations'), ~Q(relationtype = 'related'))[0:1]
            if len(hassubconcepts) > 0:
                self.hassubconcepts = True
            if include_subconcepts:
                conceptrealations = models.ConceptRelations.objects.filter(Q(conceptidfrom = self.id), Q(relationtype__category = 'Semantic Relations'), ~Q(relationtype = 'related'))
                if depth_limit == None or downlevel < depth_limit:
                    if depth_limit != None:
                        downlevel = downlevel + 1                
                    for relation in conceptrealations:
                        self.relationshiptype = relation.relationtype.pk
                        self.subconcepts.append(Concept().get(id=relation.conceptidto_id, include_subconcepts=include_subconcepts, 
                            include_parentconcepts=False, include_relatedconcepts=include_relatedconcepts, exclude=exclude, include=include, depth_limit=depth_limit, 
                            up_depth_limit=up_depth_limit, downlevel=downlevel, uplevel=uplevel, nodetype=nodetype))

                    self.subconcepts = sorted(self.subconcepts, key=methodcaller('get_sortkey', lang=lang), reverse=False) 

            if include_parentconcepts:
                if nodetype == 'EntityType':
                    conceptrealations = models.ConceptRelations.objects.filter(conceptidto = self.id, relationtype = 'member')
                else:
                    conceptrealations = models.ConceptRelations.objects.filter(Q(conceptidto = self.id), Q(relationtype__category = 'Semantic Relations'), ~Q(relationtype = 'related'))
                if up_depth_limit == None or uplevel < up_depth_limit:
                    if up_depth_limit != None:
                        uplevel = uplevel + 1          
                    for relation in conceptrealations:
                        self.parentconcepts.append(Concept().get(id=relation.conceptidfrom_id, include_subconcepts=False, 
                            include_parentconcepts=include_parentconcepts, include_relatedconcepts=include_relatedconcepts, 
                            exclude=exclude, include=include, depth_limit=depth_limit, 
                            up_depth_limit=up_depth_limit, downlevel=downlevel, uplevel=uplevel, nodetype=nodetype))

            if include_relatedconcepts:
                conceptrealations = models.ConceptRelations.objects.filter(Q(relationtype = 'related') | Q(relationtype = 'member') | Q(relationtype__category = 'Mapping Properties'), Q(conceptidto = self.id) | Q(conceptidfrom = self.id))
                for relation in conceptrealations:
                    self.relationshiptype = relation.relationtype.pk
                    if relation.conceptidto_id != self.id:
                        self.relatedconcepts.append(Concept().get(relation.conceptidto_id, include=['label']))
                    if relation.conceptidfrom_id != self.id:
                        self.relatedconcepts.append(Concept().get(relation.conceptidfrom_id, include=['label']))

        return self
            
    def save(self):
        self.id = self.id if (self.id != '' and self.id != None) else str(uuid.uuid4())
        concept, created = models.Concepts.objects.get_or_create(pk=self.id, defaults={'legacyoid': self.legacyoid, 'nodetype_id': self.nodetype})

        for value in self.values:
            if not isinstance(value, ConceptValue): 
                value = ConceptValue(value)
            value.conceptid = self.id
            value.save()        

        for parentconcept in self.parentconcepts:
            parentconcept.save()
            conceptrelation = models.ConceptRelations()
            conceptrelation.pk = str(uuid.uuid4())
            conceptrelation.conceptidfrom_id = parentconcept.id 
            conceptrelation.conceptidto_id = self.id
            conceptrelation.relationtype_id = parentconcept.relationshiptype
            conceptrelation.save()

        for subconcept in self.subconcepts:
            subconcept.save()
            conceptrelation = models.ConceptRelations()
            conceptrelation.pk = str(uuid.uuid4())
            conceptrelation.conceptidfrom_id = self.id
            conceptrelation.conceptidto_id = subconcept.id
            conceptrelation.relationtype_id = subconcept.relationshiptype
            conceptrelation.save()

        for relatedconcept in self.relatedconcepts:
            relation = models.ConceptRelations()
            relation.pk = str(uuid.uuid4())
            relation.conceptidfrom_id = self.id
            relation.conceptidto_id = relatedconcept.id
            relation.relationtype_id = relatedconcept.relationshiptype
            relation.save()

        return concept

    def delete(self, delete_self=False):
        for subconcept in self.subconcepts:
            concepts_to_delete = Concept.gather_concepts_to_delete(subconcept)

            for key, concept in concepts_to_delete.iteritems():
                models.Concepts.objects.get(pk=key).delete()

        for parentconcept in self.parentconcepts:
            conceptrelations = models.ConceptRelations.objects.filter(relationtype__category = 'Semantic Relations', conceptidfrom = parentconcept.id, conceptidto = self.id)
            for relation in conceptrelations:
                relation.delete()

        deletedrelatedconcepts = []
        for relatedconcept in self.relatedconcepts:
            conceptrelations = models.ConceptRelations.objects.filter(Q(relationtype = 'related') | Q(relationtype = 'member') | Q(relationtype__category = 'Mapping Properties'), conceptidto = relatedconcept.id, conceptidfrom = self.id)
            for relation in conceptrelations:
                relation.delete()
                deletedrelatedconcepts.append(relatedconcept)

            conceptrelations = models.ConceptRelations.objects.filter(Q(relationtype = 'related') | Q(relationtype = 'member') | Q(relationtype__category = 'Mapping Properties'), conceptidfrom = relatedconcept.id, conceptidto = self.id)
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
    def gather_concepts_to_delete(concept, lang='en-us'):
        """
        Gets a dictionary of all the concepts ids to delete
        The values of the dictionary keys differ somewhat depending on the node type being deleted
        If the nodetype == 'Concept' then return ConceptValue objects keyed to the concept id
        If the nodetype == 'ConceptScheme' or 'ConceptSchemeGroup' then return a ConceptValue object with the value set to any ONE prefLabel keyed to the concept id
        We do this because it takes so long to gather the ids of the concepts when deleting a Scheme or Group

        """

        concepts_to_delete = {}

        # Here we have to worry about making sure we don't delete nodes that have more than 1 parent
        if concept.nodetype == 'Concept':
            concept = Concept().get(id=concept.id, include_subconcepts=True, include_parentconcepts=True, include=['label'], up_depth_limit=1)
            
            def find_concepts(concept):
                if len(concept.parentconcepts) <= 1:
                    concepts_to_delete[concept.id] = concept.get_preflabel(lang=lang)
                    for subconcept in concept.subconcepts:
                        find_concepts(subconcept)

            find_concepts(concept)
            return concepts_to_delete

        # here we can just delete everything and so use a recursive CTE to get the concept ids much more quickly 
        if concept.nodetype == 'ConceptScheme' or concept.nodetype == 'ConceptSchemeGroup':
            rows = Concept().get_child_concepts(concept.id, 'narrower', ['prefLabel'], 'prefLabel')
            for row in rows:
                concepts_to_delete[row[0]] = ConceptValue({'value':row[2]})
                concepts_to_delete[row[1]] = ConceptValue({'value':row[3]})

        return concepts_to_delete

    def get_child_concepts(self, conceptid, relationtype, child_valuetypes, parent_valuetype):
        """
        Recursively builds a list of child concepts for a given concept based on its relationship type and valuetypes. 

        """

        cursor = connection.cursor()
        sql = """WITH RECURSIVE children AS (
                SELECT d.conceptidfrom, d.conceptidto, c2.value, c.value as valueto, c.valuetype, 1 AS depth       ---|NonRecursive Part
                    FROM concepts.relations d
                    JOIN concepts.values c ON(c.conceptid = d.conceptidto) 
                    JOIN concepts.values c2 ON(c2.conceptid = d.conceptidfrom) 
                    WHERE d.conceptidfrom = '{0}'
                    and c2.valuetype = '{3}'
                    and c.valuetype in ('{2}')
                    and d.relationtype = '{1}'
                UNION
                    SELECT a.conceptidfrom, a.conceptidto, v2.value, v.value as valueto, v.valuetype, depth+1      ---|RecursivePart
                    FROM concepts.relations  a
                    JOIN children b ON(b.conceptidto = a.conceptidfrom) 
                    JOIN concepts.values v ON(v.conceptid = a.conceptidto) 
                    JOIN concepts.values v2 ON(v2.conceptid = a.conceptidfrom) 
                    WHERE  v2.valuetype = '{3}'
                    and v.valuetype in ('{2}')
                    and a.relationtype = '{1}'
            ) 
            SELECT conceptidfrom, conceptidto, value, valueto FROM children;""".format(conceptid, relationtype, ("','").join(child_valuetypes), parent_valuetype)

        cursor.execute(sql)
        rows = cursor.fetchall()
        return rows

    def traverse(self, func, direction='down', scope=None):
        """
        Traverses a concept graph from self to leaf (direction='down') or root (direction='up') calling 
        the given function on each node passes an optional scope to each function

        Return a value from the function to prematurely end the traversal

        """

        if scope == None:
            ret = func(self)
        else:
            ret = func(self, scope) 
        
        # break out of the traversal if the function returns a value
        if ret != None:
            return ret    

        if direction == 'down':
            for subconcept in self.subconcepts:
                ret = subconcept.traverse(func, direction, scope)
                if ret != None: 
                    return ret  
        else:
            for parentconcept in self.parentconcepts:
                ret = parentconcept.traverse(func, direction, scope)
                if ret != None: 
                    return ret        

    def get_sortkey(self, lang='en-us'):
        for value in self.values:
            if value.type == 'sortorder':
                return value.value
                
        return self.get_preflabel(lang=lang).value

    def get_preflabel(self, lang='en-us'):
        ret = []
        if self.values == []: 
            concept = Concept().get(id=self.id, include_subconcepts=False, include_parentconcepts=False, include=['label'])
        else:
            concept = self
        for value in concept.values:
            if value.type == 'prefLabel':
                if value.language == lang:
                    return value
                elif value.language == lang.split('-')[0]:
                    ret.insert(0, value)
            elif value.type == 'altLabel':
                if value.language == lang:
                    ret.insert(0, value)
            ret.append(value)
        return ret[0] if len(ret) > 0 else ConceptValue()

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
        elif isinstance(value, models.Values):
            self.values.append(ConceptValue(value))
        else:
            raise Exception('Invalid value definition: %s' % (value))

    def index(self, scheme=None):
        for value in self.values:
            if scheme == None:
                scheme = self.get_context()
            value.index(scheme=scheme)        

        for subconcept in self.subconcepts:
            subconcept.index(scheme=subconcept.get_context())

    def delete_index(self, delete_self=False):
        se = SearchEngineFactory().create()

        for subconcept in self.subconcepts:
            concepts_to_delete = Concept.gather_concepts_to_delete(subconcept)

            for key, concept in concepts_to_delete.iteritems():
                query = Query(se, start=0, limit=10000)
                phrase = Match(field='conceptid', query=key, type='phrase')
                query.add_query(phrase)
                query.delete(index='concept_labels')

        for value in self.values:
            value.delete_index()

    def concept_tree(self, top_concept='00000000-0000-0000-0000-000000000001', lang='en-us'):
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
            temp = Concept()        
            for label in labels:
                temp.addvalue(label)
                # if label.valuetype_id == 'prefLabel':
                #     ret.label = label.value
                #     ret.id = label.conceptid_id
                #     ret.labelid = label.valueid
            label = temp.get_preflabel(lang=lang)
            ret.label = label.value
            ret.id = label.conceptid
            ret.labelid = label.id

            conceptrealations = models.ConceptRelations.objects.filter(Q(conceptidfrom = conceptid), ~Q(relationtype = 'related'), ~Q(relationtype__category = 'Mapping Properties'))
            if depth_limit != None and len(conceptrealations) > 0 and level >= depth_limit:
                ret.load_on_demand = True
            else:
                if depth_limit != None:
                    level = level + 1                
                for relation in conceptrealations:
                    ret.children.append(_findNarrowerConcept(relation.conceptidto_id, depth_limit=depth_limit, level=level))   

            return ret 

        def _findBroaderConcept(conceptid, child_concept, depth_limit=None, level=0):
            conceptrealations = models.ConceptRelations.objects.filter(Q(conceptidto = conceptid), ~Q(relationtype = 'related'), ~Q(relationtype__category = 'Mapping Properties'))
            if len(conceptrealations) > 0 and conceptid != top_concept:
                labels = models.Values.objects.filter(conceptid = conceptrealations[0].conceptidfrom_id)
                ret = concept()          
                temp = Concept()        
                for label in labels:
                    temp.addvalue(label)
                label = temp.get_preflabel(lang=lang)
                ret.label = label.value
                ret.id = label.conceptid
                ret.labelid = label.id

                ret.children.append(child_concept)
                return _findBroaderConcept(conceptrealations[0].conceptidfrom_id, ret, depth_limit=depth_limit, level=level)
            else:
                return child_concept

        graph = []
        #if self.id == None or self.id == '' or self.id == top_concept:
        concepts = models.Concepts.objects.filter(Q(nodetype = 'ConceptSchemeGroup') | Q(nodetype = 'GroupingNode'))
        for conceptmodel in concepts:
            graph.append(_findNarrowerConcept(conceptmodel.pk, depth_limit=1))
        #else:
            #graph = [_findNarrowerConcept(self.id, depth_limit=1)]
            #concepts = _findNarrowerConcept(self.id, depth_limit=1)
            #graph = [_findBroaderConcept(self.id, concepts, depth_limit=1)]

        return graph

    def get_paths(self, lang='en-us'):
        def graph_to_paths(current_concept, path=[], path_list=[]):
            if len(path) == 0:
                current_path = []
            else:
                current_path = path[:]    
                
            current_path.insert(0, {'label': current_concept.get_preflabel(lang=lang).value, 'relationshiptype': current_concept.relationshiptype, 'id': current_concept.id})

            if len(current_concept.parentconcepts) == 0:
                path_list.append(current_path[:])
            else:    
                for parent in current_concept.parentconcepts:   
                    ret = graph_to_paths(parent, current_path, path_list)                    
            
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
            nodes.append({'concept_id': child.id, 'name': child.get_preflabel(lang=lang).value, 'type': 'Descendant' })
            links.append({'source': self.id, 'target': child.id, 'relationship': 'narrower' })

        for related in self.relatedconcepts:
            nodes.append({'concept_id': related.id, 'name': related.get_preflabel(lang=lang).value, 'type': 'Related' })
            links.append({'source': self.id, 'target': related.id, 'relationship': 'related' })

        # get unique node list and assign unique integer ids for each node (required by d3)
        nodes = {node['concept_id']:node for node in nodes}.values()
        for i in range(len(nodes)):
            nodes[i]['id'] = i
            for link in links:
                link['source'] = i if link['source'] == nodes[i]['concept_id'] else link['source']
                link['target'] = i if link['target'] == nodes[i]['concept_id'] else link['target']
        
        return {'nodes': nodes, 'links': links}

    def get_context(self):
        if self.nodetype == 'Concept' or self.nodetype == 'Collection' or self.nodetype == 'EntityType':
            concept = Concept().get(id = self.id, include_parentconcepts = True, include = None)
            print JSONSerializer().serializeToPython(concept)
            def get_scheme_id(concept):
                if concept.nodetype == 'ConceptScheme' or concept.nodetype == 'GroupingNode':
                    return concept

            return concept.traverse(get_scheme_id, direction='up')

        if self.nodetype == 'ConceptScheme' or self.nodetype == 'ConceptSchemeGroup':
            return self

    def get_e55_domain(self, entitytypeid):
        """
        For a given entitytypeid creates a dictionary for each collector node. Each collector dictionary includes
        an array of its child nodes. Returns a list of these collector dictionaries added to a list of nodes that are
        neither collectors nor children of collectors

        """

        domains = list(models.VwEntitytypeDomains.objects.filter(entitytypeid=entitytypeid).order_by('sortorder', 'value').values())
        domains_copy = copy.deepcopy(domains) #Prevents 'recursive dictionary' type from getting created in nested for loop 
        nested_domains = []
        conceptids_in_nested = []
        for domain in domains:
            if domain['valuetype'] == 'collector':
                conceptids_in_nested.append(domain['conceptid'])
                children = [] #(conceptid, relationtype, child_valuetype, parent_valuetype)
                collector_children = Concept().get_child_concepts(domain['conceptid'], 'member', ['prefLabel','collector'], 'collector')
                for child in collector_children:
                    for d in domains_copy:
                        if child[1] == d['conceptid']:
                            children.append(d)
                            conceptids_in_nested.append(d['conceptid'])
                nested_domain = domain
                nested_domain['children'] = sorted(children, key=itemgetter('sortorder'))
                nested_domain['disabled'] = True
                nested_domains.append(nested_domain)
        collectorless_domains = [a for a in domains_copy if a['conceptid'] not in conceptids_in_nested]
        result = sorted(nested_domains + collectorless_domains, key=itemgetter('sortorder')) 
        return result


class ConceptValue(object):
    def __init__(self, *args, **kwargs):
        self.id = ''
        self.conceptid = ''
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
            self.type = value.valuetype.pk
            self.category = value.valuetype.category
            self.value = value.value
            self.language = value.languageid_id

        if isinstance(value, dict):
            self.id = value['id'] if 'id' in value else ''
            self.conceptid = value['conceptid'] if 'conceptid' in value else ''
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

            se.create_mapping('concept_labels', scheme.id, fieldname='conceptid', fieldtype='string', fieldindex='not_analyzed')
            se.index_data('concept_labels', scheme.id, data, 'id')
            # don't create terms for entity type concepts
            if not(scheme.id == '00000000-0000-0000-0000-000000000003' or scheme.id == '00000000-0000-0000-0000-000000000004'):
                se.index_term(self.value, self.id, scheme.id, {'conceptid': self.conceptid})
    
    def delete_index(self):      
        if self.category == 'label':
            se = SearchEngineFactory().create()
            if self.category == '':
                raise Exception('Delete index failed.  Remember to specify a category for your value. %s' % JSONSerializer().serialize(self))
            scheme = self.get_scheme_id()
            if scheme == None:
                raise Exception('Delete label index failed.  Index type (scheme id) could not be derived from the label.')
            se.delete(index='concept_labels', doc_type=scheme, id=self.id)

    def get_scheme_id(self):
        se = SearchEngineFactory().create()
        result = se.search(index='concept_labels', id=self.id)
        if result['found']:
            return Concept(result['_type'])
        else:
            return None