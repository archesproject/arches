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
from django.conf import settings
from arches.app.models import models
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Term, Query, Bool, Match, Terms
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from django.utils.translation import ugettext as _
from django.db import IntegrityError
import logging


logger = logging.getLogger(__name__)

CORE_CONCEPTS = (
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000004',
    '00000000-0000-0000-0000-000000000005',
    '00000000-0000-0000-0000-000000000006'
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

    def __hash__(self):
        return hash(self.id)
    def __eq__(self, x):
        return hash(self) == hash(x)
    def __ne__(self, x):
        return hash(self) != hash(x)

    def load(self, value):
        if isinstance(value, dict):
            self.id = str(value['id']) if 'id' in value else ''
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

        if isinstance(value, models.Concept):
            self.id = str(value.pk)
            self.nodetype = value.nodetype_id
            self.legacyoid = value.legacyoid

    def get(self, id='', legacyoid='', include_subconcepts=False, include_parentconcepts=False,
        include_relatedconcepts=False, exclude=[], include=[], depth_limit=None, up_depth_limit=None,
        lang=settings.LANGUAGE_CODE, semantic=True, pathway_filter=None, **kwargs):

        if id != '':
            self.load(models.Concept.objects.get(pk=id))
        elif legacyoid != '':
            self.load(models.Concept.objects.get(legacyoid=legacyoid))

        _cache = kwargs.pop('_cache', {})
        _cache[self.id] = self.__class__({
            "id": self.id,
            "nodetype": self.nodetype,
            "legacyoid": self.legacyoid,
            "relationshiptype": self.relationshiptype
        })

        if semantic == True:
            pathway_filter = pathway_filter if pathway_filter else Q(relationtype__category = 'Semantic Relations') | Q(relationtype__category = 'Properties')
        else:
            pathway_filter = pathway_filter if pathway_filter else Q(relationtype = 'member') | Q(relationtype = 'hasCollection')

        if self.id != '':
            nodetype = kwargs.pop('nodetype', self.nodetype)
            uplevel = kwargs.pop('uplevel', 0)
            downlevel = kwargs.pop('downlevel', 0)
            depth_limit = depth_limit if depth_limit == None else int(depth_limit)
            up_depth_limit = up_depth_limit if up_depth_limit == None else int(up_depth_limit)

            if include != None:
                if len(include) > 0 and len(exclude) > 0:
                    raise Exception('Only include values for include or exclude, but not both')
                include = include if len(include) != 0 else models.DValueType.objects.distinct('category').values_list('category', flat=True)
                include = set(include).difference(exclude)
                exclude = []

                if len(include) > 0:
                    values = models.Value.objects.filter(concept = self.id)
                    for value in values:
                        if value.valuetype.category in include:
                            self.values.append(ConceptValue(value))

            hassubconcepts = models.Relation.objects.filter(Q(conceptfrom = self.id), pathway_filter, ~Q(relationtype = 'related'))[0:1]
            if len(hassubconcepts) > 0:
                self.hassubconcepts = True

            if include_subconcepts:
                conceptrealations = models.Relation.objects.filter(Q(conceptfrom = self.id), pathway_filter, ~Q(relationtype = 'related'))
                if depth_limit == None or downlevel < depth_limit:
                    if depth_limit != None:
                        downlevel = downlevel + 1
                    for relation in conceptrealations:
                        subconcept = _cache[str(relation.conceptto_id)] if str(relation.conceptto_id) in _cache else self.__class__().get(id=relation.conceptto_id,
                            include_subconcepts=include_subconcepts,include_parentconcepts=include_parentconcepts,
                            include_relatedconcepts=include_relatedconcepts, exclude=exclude, include=include,
                            depth_limit=depth_limit, up_depth_limit=up_depth_limit, downlevel=downlevel, uplevel=uplevel,
                            nodetype=nodetype, semantic=semantic, pathway_filter=pathway_filter, _cache=_cache.copy(), lang=lang)
                        subconcept.relationshiptype = relation.relationtype.pk
                        self.subconcepts.append(subconcept)

                    self.subconcepts = sorted(self.subconcepts, key=methodcaller('get_sortkey', lang=lang), reverse=False)

            if include_parentconcepts:
                conceptrealations = models.Relation.objects.filter(Q(conceptto = self.id), pathway_filter, ~Q(relationtype = 'related'))
                if up_depth_limit == None or uplevel < up_depth_limit:
                    if up_depth_limit != None:
                        uplevel = uplevel + 1
                    for relation in conceptrealations:
                        parentconcept = _cache[str(relation.conceptfrom_id)] if str(relation.conceptfrom_id) in _cache else self.__class__().get(id=relation.conceptfrom_id,
                            include_subconcepts=False,include_parentconcepts=include_parentconcepts,
                            include_relatedconcepts=include_relatedconcepts,exclude=exclude, include=include,
                            depth_limit=depth_limit, up_depth_limit=up_depth_limit, downlevel=downlevel, uplevel=uplevel,
                            nodetype=nodetype, semantic=semantic, pathway_filter=pathway_filter, _cache=_cache.copy(), lang=lang)
                        parentconcept.relationshiptype = relation.relationtype.pk
                        self.parentconcepts.append(parentconcept)

            if include_relatedconcepts:
                conceptrealations = models.Relation.objects.filter(Q(relationtype = 'related') | Q(relationtype__category = 'Mapping Properties'), Q(conceptto = self.id) | Q(conceptfrom = self.id))
                for relation in conceptrealations:
                    if relation.conceptto_id != self.id:
                        relatedconcept = self.__class__().get(relation.conceptto_id, include=['label'], lang=lang)
                        relatedconcept.relationshiptype = relation.relationtype.pk
                        self.relatedconcepts.append(relatedconcept)
                    if relation.conceptfrom_id != self.id:
                        relatedconcept = self.__class__().get(relation.conceptfrom_id, include=['label'], lang=lang)
                        relatedconcept.relationshiptype = relation.relationtype.pk
                        self.relatedconcepts.append(relatedconcept)

        return self

    def save(self):
        self.id = self.id if (self.id != '' and self.id != None) else str(uuid.uuid4())
        concept, created = models.Concept.objects.get_or_create(pk=self.id, defaults={'legacyoid': self.legacyoid if self.legacyoid != '' else self.id, 'nodetype_id': self.nodetype})

        for value in self.values:
            if not isinstance(value, ConceptValue):
                value = ConceptValue(value)
            value.conceptid = self.id
            value.save()

        for parentconcept in self.parentconcepts:
            parentconcept.save()
            parentconcept.add_relation(self, parentconcept.relationshiptype)

        for subconcept in self.subconcepts:
            subconcept.save()
            self.add_relation(subconcept, subconcept.relationshiptype)

        for relatedconcept in self.relatedconcepts:
            self.add_relation(relatedconcept, relatedconcept.relationshiptype)

            if relatedconcept.relationshiptype == 'member':
                child_concepts = relatedconcept.get(include_subconcepts=True)
                def applyRelationship(concept):
                    for subconcept in concept.subconcepts:
                        concept.add_relation(subconcept, relatedconcept.relationshiptype)
                child_concepts.traverse(applyRelationship)


        return concept

    def delete(self, delete_self=False):
        """
        Deletes any subconcepts associated with this concept and additionally this concept if 'delete_self' is True
        If any parentconcepts or relatedconcepts are included then it will only delete the relationship to those concepts but not the concepts themselves
        If any values are passed, then those values as well as the relationship to those values will be deleted

        Note, django will automatically take care of deleting any db models that have a foreign key relationship to the model being deleted
        (eg: deleting a concept model will also delete all values and relationships), but because we need to manage deleting
        parent concepts and related concepts and values we have to do that here too

        """

        for subconcept in self.subconcepts:
            concepts_to_delete = Concept.gather_concepts_to_delete(subconcept)
            for key, concept in concepts_to_delete.iteritems():
                models.Concept.objects.get(pk=key).delete()

        for parentconcept in self.parentconcepts:
            conceptrelations = models.Relation.objects.filter(relationtype__category = 'Semantic Relations', conceptfrom = parentconcept.id, conceptto = self.id)
            for relation in conceptrelations:
                relation.delete()

        deletedrelatedconcepts = []
        for relatedconcept in self.relatedconcepts:
            conceptrelations = models.Relation.objects.filter(Q(relationtype = 'related') | Q(relationtype = 'member') | Q(relationtype__category = 'Mapping Properties'), conceptto = relatedconcept.id, conceptfrom = self.id)
            for relation in conceptrelations:
                relation.delete()
                deletedrelatedconcepts.append(relatedconcept)

            conceptrelations = models.Relation.objects.filter(Q(relationtype = 'related') | Q(relationtype = 'member') | Q(relationtype__category = 'Mapping Properties'), conceptfrom = relatedconcept.id, conceptto = self.id)
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
            concepts_to_delete = Concept.gather_concepts_to_delete(self)
            for key, concept in concepts_to_delete.iteritems():
                # delete only member relationships if the nodetype == Collection
                if concept.nodetype == 'Collection':
                    concept = Concept().get(id=concept.id, include_subconcepts=True, include_parentconcepts=True, include=['label'], up_depth_limit=1, semantic=False)
                    def find_concepts(concept):
                        if len(concept.parentconcepts) <= 1:
                            for subconcept in concept.subconcepts:
                                conceptrelation = models.Relation.objects.get(conceptfrom=concept.id, conceptto=subconcept.id, relationtype='member')
                                conceptrelation.delete()
                                find_concepts(subconcept)

                    find_concepts(concept)

                models.Concept.objects.get(pk=key).delete()
        return

    def add_relation(self, concepttorelate, relationtype):
        """
        Relates this concept to 'concepttorelate' via the relationtype

        """

        # relation = models.Relation()
        # relation.pk = str(uuid.uuid4())
        # relation.conceptfrom_id = self.id
        # relation.conceptto_id = concepttorelate.id
        # relation.relationtype_id = relationtype
        # relation.save()
        relation, created = models.Relation.objects.get_or_create(conceptfrom_id=self.id, conceptto_id=concepttorelate.id, relationtype_id=relationtype)
        return relation

    @staticmethod
    def gather_concepts_to_delete(concept, lang=settings.LANGUAGE_CODE):
        """
        Gets a dictionary of all the concepts ids to delete
        The values of the dictionary keys differ somewhat depending on the node type being deleted
        If the nodetype == 'Concept' then return ConceptValue objects keyed to the concept id
        If the nodetype == 'ConceptScheme' then return a ConceptValue object with the value set to any ONE prefLabel keyed to the concept id
        We do this because it takes so long to gather the ids of the concepts when deleting a Scheme or Group

        """

        concepts_to_delete = {}

        # Here we have to worry about making sure we don't delete nodes that have more than 1 parent
        if concept.nodetype == 'Concept':
            concept = Concept().get(id=concept.id, include_subconcepts=True, include_parentconcepts=True, include=['label'], up_depth_limit=1)

            def find_concepts(concept):
                if len(concept.parentconcepts) <= 1:
                    concepts_to_delete[concept.id] = concept
                    for subconcept in concept.subconcepts:
                        find_concepts(subconcept)

            find_concepts(concept)
            return concepts_to_delete

        # here we can just delete everything and so use a recursive CTE to get the concept ids much more quickly
        if concept.nodetype == 'ConceptScheme':
            rows = Concept().get_child_concepts(concept.id, ['narrower', 'hasTopConcept'], ['prefLabel', 'altLabel', 'hiddenLabel'], 'prefLabel')
            for row in rows:
                if row[0] not in concepts_to_delete:
                    concepts_to_delete[row[0]] = Concept({'id': row[0]})

                if row[1] not in concepts_to_delete:
                    concepts_to_delete[row[1]] = Concept({'id': row[1]})

                concepts_to_delete[row[0]].addvalue({'id':row[4], 'conceptid':row[0], 'value':row[2]})
                concepts_to_delete[row[1]].addvalue({'id':row[5], 'conceptid':row[1], 'value':row[3]})

        if concept.nodetype == 'Collection':
            concepts_to_delete[concept.id] = concept

        return concepts_to_delete

    def get_child_concepts(self, conceptid, relationtypes, child_valuetypes, parent_valuetype):
        """
        Recursively builds a list of child concepts for a given concept based on its relationship type and valuetypes.

        """

        cursor = connection.cursor()
        relationtypes = ' or '.join(["d.relationtype = '%s'" % (relationtype) for relationtype in relationtypes])
        sql = """WITH RECURSIVE children AS (
                SELECT d.conceptidfrom, d.conceptidto, c2.value, c.value as valueto, c2.valueid, c.valueid as valueidto, c.valuetype, 1 AS depth       ---|NonRecursive Part
                    FROM relations d
                    JOIN values c ON(c.conceptid = d.conceptidto)
                    JOIN values c2 ON(c2.conceptid = d.conceptidfrom)
                    WHERE d.conceptidfrom = '{0}'
                    and c2.valuetype = '{3}'
                    and c.valuetype in ('{2}')
                    and ({1})
                UNION
                    SELECT d.conceptidfrom, d.conceptidto, v2.value, v.value as valueto, v2.valueid, v.valueid as valueidto, v.valuetype, depth+1      ---|RecursivePart
                    FROM relations  d
                    JOIN children b ON(b.conceptidto = d.conceptidfrom)
                    JOIN values v ON(v.conceptid = d.conceptidto)
                    JOIN values v2 ON(v2.conceptid = d.conceptidfrom)
                    WHERE v2.valuetype = '{3}'
                    and v.valuetype in ('{2}')
                    and ({1})
            )
            SELECT conceptidfrom::text, conceptidto::text, value, valueto, valueid::text, valueidto::text FROM children;""".format(conceptid, relationtypes, ("','").join(child_valuetypes), parent_valuetype)

        cursor.execute(sql)
        rows = cursor.fetchall()
        return rows

    def traverse(self, func, direction='down', scope=None, **kwargs):
        """
        Traverses a concept graph from self to leaf (direction='down') or root (direction='up') calling
        the given function on each node, passes an optional scope to each function

        Return a value from the function to prematurely end the traversal

        """

        _cache = kwargs.pop('_cache', [])
        if self.id not in _cache:
            _cache.append(self.id)

            if scope == None:
                ret = func(self, **kwargs)
            else:
                ret = func(self, scope, **kwargs)

            # break out of the traversal if the function returns a value
            if ret != None:
                return ret

            if direction == 'down':
                for subconcept in self.subconcepts:
                    ret = subconcept.traverse(func, direction, scope, _cache=_cache, **kwargs)
                    if ret != None:
                        return ret
            else:
                for parentconcept in self.parentconcepts:
                    ret = parentconcept.traverse(func, direction, scope, _cache=_cache, **kwargs)
                    if ret != None:
                        return ret

    def get_sortkey(self, lang=settings.LANGUAGE_CODE):
        for value in self.values:
            if value.type == 'sortorder':
                return value.value

        return self.get_preflabel(lang=lang).value

    def get_preflabel(self, lang=settings.LANGUAGE_CODE):
        score = 0
        ranked_labels = []
        if self.values == []:
            concept = Concept().get(id=self.id, include_subconcepts=False, include_parentconcepts=False, include=['label'])
        else:
            concept = self

        for value in concept.values:
            ranked_label = {
                'weight': 1,
                'value': value
            }
            if value.type == 'prefLabel':
                ranked_label['weight'] = ranked_label['weight'] * 10
            elif value.type == 'altLabel':
                ranked_label['weight'] = ranked_label['weight'] * 4

            if value.language == lang:
                ranked_label['weight'] = ranked_label['weight'] * 10
            elif value.language.split('-')[0] == lang.split('-')[0]:
                ranked_label['weight'] = ranked_label['weight'] * 5

            ranked_labels.append(ranked_label)

        ranked_labels = sorted(ranked_labels, key=lambda label: label['weight'], reverse=True)
        if len(ranked_labels) == 0:
            ranked_labels.append({
                'weight': 1,
                'value': ConceptValue()
            })

        return ranked_labels[0]['value']

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
        elif isinstance(value, models.Value):
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

        def delete_concept_values_index(concepts_to_delete):
            se = SearchEngineFactory().create()
            for concept in concepts_to_delete.itervalues():
                query = Query(se, start=0, limit=10000)
                term = Term(field='conceptid', term=concept.id)
                query.add_query(term)
                query.delete(index='strings', doc_type='concept')

        if delete_self:
            concepts_to_delete = Concept.gather_concepts_to_delete(self)
            delete_concept_values_index(concepts_to_delete)

        else:
            delete_concept_values_index({self.id: self})
            for subconcept in self.subconcepts:
                concepts_to_delete = Concept.gather_concepts_to_delete(subconcept)
                delete_concept_values_index(concepts_to_delete)

    def concept_tree(self, top_concept='00000000-0000-0000-0000-000000000001', lang=settings.LANGUAGE_CODE, mode='semantic'):
        class concept(object):
            def __init__(self, *args, **kwargs):
                self.label = ''
                self.labelid = ''
                self.id = ''
                self.load_on_demand = False
                self.children = []

        def _findNarrowerConcept(conceptid, depth_limit=None, level=0):
            labels = models.Value.objects.filter(concept = conceptid)
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

            if mode == 'semantic':
                conceptrealations = models.Relation.objects.filter(Q(conceptfrom = conceptid), Q(relationtype__category = 'Semantic Relations') | Q(relationtype__category = 'Properties'))
            if mode == 'collections':
                conceptrealations = models.Relation.objects.filter(Q(conceptfrom = conceptid), Q(relationtype = 'member') | Q(relationtype = 'hasCollection') )
            if depth_limit != None and len(conceptrealations) > 0 and level >= depth_limit:
                ret.load_on_demand = True
            else:
                if depth_limit != None:
                    level = level + 1
                for relation in conceptrealations:
                    ret.children.append(_findNarrowerConcept(relation.conceptto_id, depth_limit=depth_limit, level=level))
                ret.children = sorted(ret.children, key=lambda concept: concept.label)
            return ret

        def _findBroaderConcept(conceptid, child_concept, depth_limit=None, level=0):
            conceptrealations = models.Relation.objects.filter(Q(conceptto = conceptid), ~Q(relationtype = 'related'), ~Q(relationtype__category = 'Mapping Properties'))
            if len(conceptrealations) > 0 and conceptid != top_concept:
                labels = models.Value.objects.filter(concept = conceptrealations[0].conceptfrom_id)
                ret = concept()
                temp = Concept()
                for label in labels:
                    temp.addvalue(label)
                label = temp.get_preflabel(lang=lang)
                ret.label = label.value
                ret.id = label.conceptid
                ret.labelid = label.id

                ret.children.append(child_concept)
                return _findBroaderConcept(conceptrealations[0].conceptfrom_id, ret, depth_limit=depth_limit, level=level)
            else:
                return child_concept

        graph = []
        if self.id == None or self.id == '' or self.id == 'None' or self.id == top_concept:
            if mode == 'semantic':
                concepts = models.Concept.objects.filter(nodetype='ConceptScheme')
                for conceptmodel in concepts:
                    graph.append(_findNarrowerConcept(conceptmodel.pk, depth_limit=1))
            if mode == 'collections':
                concepts = models.Concept.objects.filter(nodetype='Collection')
                for conceptmodel in concepts:
                    graph.append(_findNarrowerConcept(conceptmodel.pk, depth_limit=0))

                graph = sorted(graph, key=lambda concept: concept.label)
                #graph = _findNarrowerConcept(concepts[0].pk, depth_limit=1).children

        else:
            graph = _findNarrowerConcept(self.id, depth_limit=1).children
            # concepts = _findNarrowerConcept(self.id, depth_limit=1)
            # graph = [_findBroaderConcept(self.id, concepts, depth_limit=1)]

        return graph

    def get_paths(self, lang=settings.LANGUAGE_CODE):

        def graph_to_paths(current_concept, path=[], path_list=[], _cache=[]):
            if len(path) == 0:
                current_path = []
            else:
                current_path = path[:]

            current_path.insert(0, {'label': current_concept.get_preflabel(lang=lang).value, 'relationshiptype': current_concept.relationshiptype, 'id': current_concept.id})

            if len(current_concept.parentconcepts) == 0 or current_concept.id in _cache:
                path_list.append(current_path[:])
            else:
                _cache.append(current_concept.id)
                for parent in current_concept.parentconcepts:
                    ret = graph_to_paths(parent, current_path, path_list, _cache)

            return path_list

        # def graph_to_paths(current_concept, **kwargs):
        #     path = kwargs.get('path', [])
        #     path_list = kwargs.get('path_list', [])

        #     if len(path) == 0:
        #         current_path = []
        #     else:
        #         current_path = path[:]

        #     current_path.insert(0, {'label': current_concept.get_preflabel(lang=lang).value, 'relationshiptype': current_concept.relationshiptype, 'id': current_concept.id})

        #     if len(current_concept.parentconcepts) == 0:
        #         path_list.append(current_path[:])
        #     # else:
        #     #     for parent in current_concept.parentconcepts:
        #     #         ret = graph_to_paths(parent, current_path, path_list, _cache)

        #     #return path_list

        # self.traverse(graph_to_paths, direction='up')

        return graph_to_paths(self)

    def get_node_and_links(self, lang=settings.LANGUAGE_CODE):
        nodes = [{'concept_id': self.id, 'name': self.get_preflabel(lang=lang).value,'type': 'Current'}]
        links = []

        def get_parent_nodes_and_links(current_concept, _cache=[]):
            if current_concept.id not in _cache:
                _cache.append(current_concept.id)
                parents = current_concept.parentconcepts
                for parent in parents:
                    nodes.append({'concept_id': parent.id, 'name': parent.get_preflabel(lang=lang).value, 'type': 'Root' if len(parent.parentconcepts) == 0 else 'Ancestor'})
                    links.append({'target': current_concept.id, 'source': parent.id, 'relationship': 'broader' })
                    get_parent_nodes_and_links(parent, _cache)

        get_parent_nodes_and_links(self)

        # def get_parent_nodes_and_links(current_concept):
        #     parents = current_concept.parentconcepts
        #     for parent in parents:
        #         nodes.append({'concept_id': parent.id, 'name': parent.get_preflabel(lang=lang).value, 'type': 'Root' if len(parent.parentconcepts) == 0 else 'Ancestor'})
        #         links.append({'target': current_concept.id, 'source': parent.id, 'relationship': 'broader' })

        # self.traverse(get_parent_nodes_and_links, direction='up')

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
        if self.nodetype == 'Concept' or self.nodetype == 'Collection':
            concept = Concept().get(id = self.id, include_parentconcepts = True, include = None)
            def get_scheme_id(concept):
                for parentconcept in concept.parentconcepts:
                    if parentconcept.relationshiptype == 'hasTopConcept':
                        return concept

            if len(concept.parentconcepts) > 0:
                return concept.traverse(get_scheme_id, direction='up')
            else:
                return self

        else: # like ConceptScheme or EntityType
            return self

    def check_if_concept_in_use(self):
        """Checks  if a concept or any of its subconcepts is in use by a resource instance"""

        in_use = False
        cursor = connection.cursor()
        for value in self.values:
            sql = """
                SELECT count(*) from tiles t, jsonb_each_text(t.tiledata) as json_data
                WHERE json_data.value = '%s'
            """ % value.id
            cursor.execute(sql)
            rows = cursor.fetchall()
            if rows[0][0] > 0:
                in_use = True
                break
        if in_use != True:
            for subconcept in self.subconcepts:
                in_use = subconcept.check_if_concept_in_use()
                if in_use == True:
                    return in_use
        return in_use

    def get_e55_domain(self, conceptid):
        """
        For a given entitytypeid creates a dictionary representing that entitytypeid's concept graph (member pathway) formatted to support
        select2 dropdowns

        """
        cursor = connection.cursor()

        sql = """
        WITH RECURSIVE children AS (
            SELECT d.conceptidfrom, d.conceptidto, c2.value, c2.valueid as valueid, c.value as valueto, c.valueid as valueidto, c.valuetype as vtype, 1 AS depth, array[d.conceptidto] AS conceptpath, array[c.valueid] AS idpath        ---|NonRecursive Part
                FROM relations d
                JOIN values c ON(c.conceptid = d.conceptidto)
                JOIN values c2 ON(c2.conceptid = d.conceptidfrom)
                WHERE d.conceptidfrom = '{0}'
                and c2.valuetype = 'prefLabel'
                and c.valuetype in ('prefLabel', 'sortorder', 'collector')
                and (d.relationtype = 'member' or d.relationtype = 'hasTopConcept')
                UNION
                SELECT d.conceptidfrom, d.conceptidto, v2.value, v2.valueid as valueid, v.value as valueto, v.valueid as valueidto, v.valuetype as vtype, depth+1, (conceptpath || d.conceptidto), (idpath || v.valueid)   ---|RecursivePart
                FROM relations  d
                JOIN children b ON(b.conceptidto = d.conceptidfrom)
                JOIN values v ON(v.conceptid = d.conceptidto)
                JOIN values v2 ON(v2.conceptid = d.conceptidfrom)
                WHERE  v2.valuetype = 'prefLabel'
                and v.valuetype in ('prefLabel','sortorder', 'collector')
                and (d.relationtype = 'member' or d.relationtype = 'hasTopConcept')
            ) SELECT conceptidfrom::text, conceptidto::text, value, valueid::text, valueto, valueidto::text, depth, idpath::text, conceptpath::text, vtype FROM children ORDER BY depth, conceptpath;
        """.format(conceptid)


        column_names = ['conceptidfrom', 'conceptidto', 'value', 'valueid', 'valueto', 'valueidto', 'depth', 'idpath', 'conceptpath', 'vtype']
        cursor.execute(sql)
        rows = cursor.fetchall()

        class Val(object):
            def __init__(self, conceptid):
                self.text = ''
                self.conceptid = conceptid
                self.id = ''
                self.sortorder = ''
                self.collector = ''
                self.children = []

        result = Val(conceptid)

        def _findNarrower(val, path, rec):
            for conceptid in path:
                childids = [child.conceptid for child in val.children]
                if conceptid not in childids:
                    new_val = Val(rec['conceptidto'])
                    if rec['vtype'] == 'sortorder':
                        new_val.sortorder = rec['valueto']
                    elif rec['vtype'] == 'prefLabel':
                        new_val.text = rec['valueto']
                        new_val.id = rec['valueidto']
                    elif rec['vtype'] == 'collector':
                        new_val.collector = 'collector'
                    val.children.append(new_val)
                else:
                    for child in val.children:
                        if conceptid == child.conceptid:
                            if conceptid == path[-1]:
                                if rec['vtype'] == 'sortorder':
                                    child.sortorder = rec['valueto']
                                elif rec['vtype'] == 'prefLabel':
                                    child.text = rec['valueto']
                                    child.id = rec['valueidto']
                                elif rec['vtype'] == 'collector':
                                    child.collector = 'collector'
                            path.pop(0)
                            _findNarrower(child, path, rec)
                val.children.sort(key=lambda x: (x.sortorder, x.text))

        for row in rows:
            rec = dict(zip(column_names, row))
            path = rec['conceptpath'][1:-1].split(',')
            _findNarrower(result, path, rec)

        return JSONSerializer().serializeToPython(result)['children']

    @staticmethod
    def get_time_filter_data():
        important_dates = []
        for date_search_entity_type in settings.DATE_SEARCH_ENTITY_TYPES:
            important_dates = important_dates + Concept().get_e55_domain(date_search_entity_type)

        return {
            'important_dates': {
                'branch_lists': [],
                'domains': {
                    'important_dates' : important_dates,
                    'date_operators' : [{
                        "conceptid": "0",
                        "entitytypeid": "DATE_COMPARISON_OPERATOR.E55",
                        "id": "0",
                        "languageid": settings.LANGUAGE_CODE,
                        "text": _("Before"),
                        "valuetype": "prefLabel",
                        "sortorder": "",
                        "collector": "",
                        "children": []
                    },{
                        "conceptid": "1",
                        "entitytypeid": "DATE_COMPARISON_OPERATOR.E55",
                        "id": "1",
                        "languageid": settings.LANGUAGE_CODE,
                        "text": _("On"),
                        "valuetype": "prefLabel",
                        "sortorder": "",
                        "collector": "",
                        "children": []
                    },{
                        "conceptid": "2",
                        "entitytypeid": "DATE_COMPARISON_OPERATOR.E55",
                        "id": "2",
                        "languageid": settings.LANGUAGE_CODE,
                        "text": _("After"),
                        "valuetype": "prefLabel",
                        "sortorder": "",
                        "collector": "",
                        "children": []
                    }]
                }
            }
        }

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

    def __repr__(self):
        return ('%s: %s = "%s" in lang %s') % (self.__class__, self.type, self.value, self.language)

    def get(self, id=''):
        self.load(models.Value.objects.get(pk = id))
        return self

    def save(self):
        if self.value.strip() != '':
            self.id = self.id if (self.id != '' and self.id != None) else str(uuid.uuid4())
            value = models.Value()
            value.pk = self.id
            value.value = self.value
            value.concept_id = self.conceptid # models.Concept.objects.get(pk=self.conceptid)
            value.valuetype_id = self.type # models.DValueType.objects.get(pk=self.type)
            if self.language != '':
                value.language_id = self.language # models.DLanguage.objects.get(pk=self.language)
            else:
                value.language_id = settings.LANGUAGE_CODE
            try:
                if value.value != 'Resource To Resource Relationship Types':
                    value.save()
            except IntegrityError as e:
                valuetype = models.DValueType()
                valuetype.valuetype = value.valuetype_id
                valuetype.category = 'undefined'
                valuetype.namespace = 'arches'
                valuetype.save()

                value.save()

            self.category = value.valuetype.category

    def delete(self):
        if self.id != '':
            newvalue = models.Value.objects.get(pk=self.id)
            newvalue.delete()
            self = ConceptValue()
            return self

    def load(self, value):
        if isinstance(value, models.Value):
            self.id = str(value.pk)
            self.conceptid = str(value.concept.pk)
            self.type = value.valuetype.pk
            self.category = value.valuetype.category
            self.value = value.value
            self.language = value.language_id

        if isinstance(value, dict):
            self.id = str(value['id']) if 'id' in value else ''
            self.conceptid = str(value['conceptid']) if 'conceptid' in value else ''
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

            data['top_concept'] = scheme.id
            se.index_data('strings', 'concept', data, 'id')

    def delete_index(self):
        se = SearchEngineFactory().create()
        query = Query(se, start=0, limit=10000)
        term = Term(field='id', term=self.id)
        query.add_query(term)
        query.delete(index='strings', doc_type='concept')

    def get_scheme_id(self):
        se = SearchEngineFactory().create()
        result = se.search(index='strings', doc_type='concept', id=self.id)
        if result['found']:
            return Concept(result['top_concept'])
        else:
            return None


def get_preflabel_from_conceptid(conceptid, lang):
    ret = None
    default = {
        "category": "",
        "conceptid": "",
        "language": "",
        "value": "",
        "type": "",
        "id": ""
    }
    se = SearchEngineFactory().create()
    query = Query(se)
    bool_query = Bool()
    bool_query.must(Match(field='type', query='prefLabel', type='phrase'))
    bool_query.filter(Terms(field='conceptid', terms=[conceptid]))
    query.add_query(bool_query)
    preflabels = query.search(index='strings', doc_type='concept')['hits']['hits']
    for preflabel in preflabels:
        default = preflabel['_source']
        # get the label in the preferred language, otherwise get the label in the default language
        if preflabel['_source']['language'] == lang:
            return preflabel['_source']
        if preflabel['_source']['language'].split('-')[0] == lang.split('-')[0]:
            ret = preflabel['_source']
        if preflabel['_source']['language'] == settings.LANGUAGE_CODE and ret == None:
            ret = preflabel['_source']
    return default if ret == None else ret


def get_concept_label_from_valueid(valueid):
    se = SearchEngineFactory().create()
    concept_label = se.search(index='strings', doc_type='concept', id=valueid)
    if concept_label['found']:
        return concept_label['_source']


def get_preflabel_from_valueid(valueid, lang):
    se = SearchEngineFactory().create()
    concept_label = se.search(index='strings', doc_type='concept', id=valueid)
    if concept_label['found']:
        return get_preflabel_from_conceptid(get_concept_label_from_valueid(valueid)['conceptid'], lang)
