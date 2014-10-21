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
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer

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
                conceptrealations = models.ConceptRelations.objects.filter(Q(conceptidfrom = self.id), ~Q(relationtype = 'has related concept'))
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
                conceptrealations = models.ConceptRelations.objects.filter(Q(conceptidto = self.id), ~Q(relationtype = 'has related concept'))
                if up_depth_limit == None or uplevel < up_depth_limit:
                    if up_depth_limit != None:
                        uplevel = uplevel + 1          
                    for relation in conceptrealations:
                        self.parentconcepts.append(Concept().get(id=relation.conceptidfrom_id, include_subconcepts=False, 
                            include_parentconcepts=include_parentconcepts, include_relatedconcepts=include_relatedconcepts, 
                            exclude=exclude, include=include, depth_limit=depth_limit, 
                            up_depth_limit=up_depth_limit, downlevel=downlevel, uplevel=uplevel))

            if include_relatedconcepts:
                conceptrealations = models.ConceptRelations.objects.filter(Q(relationtype = 'has related concept'), Q(conceptidto = self.id) | Q(conceptidfrom = self.id))
                for relation in conceptrealations:
                    if relation.conceptidto_id != self.id:
                        self.relatedconcepts.append(Concept().get(relation.conceptidto_id, include=['label']).get_preflabel())
                    if relation.conceptidfrom_id != self.id:
                        self.relatedconcepts.append(Concept().get(relation.conceptidfrom_id, include=['label']).get_preflabel())

        return self
            
    def save(self):
        with transaction.atomic():
            #try:
            self.id = self.id if self.id != '' else str(uuid.uuid4())
            concept, created = models.Concepts.objects.get_or_create(pk=self.id, defaults={'legacyoid': self.legacyoid})
            # except:
                
            #     concept = models.Concepts()
            #     concept.pk = self.id
            #     concept.legacyoid = self.legacyoid
            #     #concept.save()
            #     concept.save(force_insert=True)

            for parentconcept in self.parentconcepts:
                parentconcept.save()
                conceptrelation = models.ConceptRelations()
                conceptrelation.pk = str(uuid.uuid4())
                conceptrelation.conceptidfrom_id = parentconcept.id #models.Concepts.objects.get(pk=parentconcept.id)
                conceptrelation.conceptidto = concept
                conceptrelation.relationtype_id = parentconcept.relationshiptype #models.DRelationtypes.objects.get(pk=parentconcept.relationshiptype)
                conceptrelation.save()

            for subconcept in self.subconcepts:
                subconcept.save()
                conceptrelation = models.ConceptRelations()
                conceptrelation.pk = str(uuid.uuid4())
                conceptrelation.conceptidfrom = concept
                conceptrelation.conceptidto_id = subconcept.id #models.Concepts.objects.get(pk=subconcept.id)
                conceptrelation.relationtype_id = self.relationshiptype #models.DRelationtypes.objects.get(pk=self.relationshiptype)
                conceptrelation.save()

            for value in self.values:
                if not isinstance(value, ConceptValue): 
                    value = ConceptValue(value)
                value.conceptid = self.id
                value.save()

            return concept

    def delete(self):
        concept = models.Concepts.objects.get(pk=self.id)
        concept.delete()

    def delete_related_concept(self):
        deletedrelatedconcepts = []
        for relatedconcept in self.relatedconcepts:
            print relatedconcept.id
            conceptrelations = models.ConceptRelations.objects.filter(relationtype = 'has related concept', conceptidto = relatedconcept.id, conceptidfrom = self.id)
            for relation in conceptrelations:
                relation.delete()
                deletedrelatedconcepts.append(relatedconcept)

            conceptrelations = models.ConceptRelations.objects.filter(relationtype = 'has related concept', conceptidfrom = relatedconcept.id, conceptidto = self.id)
            for relation in conceptrelations:
                relation.delete()
                deletedrelatedconcepts.append(relatedconcept)

        for deletedrelatedconcept in deletedrelatedconcepts:
            if deletedrelatedconcept in self.relatedconcepts:
                self.relatedconcepts.remove(deletedrelatedconcept)

    def get_sortkey(self, lang='en-us'):
        for value in self.values:
            if value.type == 'sortorder':
                return value.value

        return self.get_preflabel(lang=lang).value

    def get_auth_doc_concept(self, lang='en-us'):
        concept = Concept().get(id=self.id, include_subconcepts=False, include_parentconcepts=True)
       
        def find_auth_doc(concept):
            for parentconcept in concept.parentconcepts:
                if parentconcept.id == '00000000-0000-0000-0000-000000000004':
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
        if scheme == '':
            scheme = self.get_auth_doc_concept().id
        for label in self.values:
            label.index(scheme=scheme)

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
        self.id = self.id if self.id != '' else str(uuid.uuid4())
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

    def index(self, scheme=''):
        se = SearchEngineFactory().create()
        if self.category == 'label':
            data = JSONSerializer().serializeToPython(self)
            se.index_data('concept_labels', scheme, data, 'id')