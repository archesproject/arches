import uuid
import operator
from django.conf import settings
from arches.app.models import models
from django.db.models import Q
from arches.app.models.concept import Concept, ConceptValue
from arches.app.utils.betterJSONSerializer import JSONSerializer

class Ontology(Concept):
    """
    A subclass of the Concept class with specific methods just for Ontologies

    """

    def get_valid_ontology_concepts(self, parent_node=None, child_properties=[], lang=settings.LANGUAGE_CODE):
        """
        given the constraints of parent_node and/or child_properties return the list of valid properties a 
        node can have with a parent node and the associated classes that that node could have

        Keyword Arguments:
        parent_node (optional - required if child_properties is empty) -- a parent node(dictionary) object

        child_properties (optional - required if parent_node is empty) -- a list of edge(dictionary) objects

        lang -- the language of the returned values

        """

        ret = []
        
        # get a list of ontology classes based on any properties to child nodes
        ontology_classes = set()
        if len(child_properties) > 0:
            q_list = [Q(conceptto_id=child_property['ontologyproperty_id']) for child_property in child_properties]
            for ontology_property in models.Relation.objects.filter(reduce(operator.or_, q_list)).distinct('conceptfrom_id'):
                subclasses = Ontology().get_subclasses(id=ontology_property.conceptfrom_id, include=['label'], lang=lang)

                if len(ontology_classes) == 0:
                    ontology_classes = subclasses
                else:
                    ontology_classes = ontology_classes.intersection(subclasses)

                if len(ontology_classes) == 0:
                    break

        # get a list of properties (and corresponding classes) that could be used to relate to my parent node
        # limit the list of properties based on the intersection between the properties classes and the list of 
        # ontology classes we defined above
        if parent_node:
            # get the super classes of the parent node and then for each node
            # call get valid range connnections
            for superclass in self.get_superclasses(id=parent_node['ontologyclass_id']):
                related_properties = self.get_valid_range_connections(superclass.id, lang=lang)
                for related_property in related_properties:
                    if len(child_properties) > 0:
                        related_property['ontology_classes'] = set(related_property['ontology_classes']).intersection(ontology_classes)

                    item = {
                        'ontology_property':related_property['ontology_property'].simplify(lang=lang),
                        'ontology_classes':[]
                    }
                    for ontology_class in related_property['ontology_classes']:
                        item['ontology_classes'].append(ontology_class.simplify(lang=lang))
                    ret.append(item)

        else:
        # if no parent node then just use the list of ontology classes from above, there will be no properties to return
            item = {
                'ontology_property':None,
                'ontology_classes':[]
            }
            if len(child_properties) == 0:
                for concept in models.Concept.objects.filter(nodetype='Ontology Class'):
                    item['ontology_classes'].append(Ontology(concept).simplify(lang=lang))
            for ontology_class in ontology_classes:
                item['ontology_classes'].append(ontology_class.simplify(lang=lang))

            ret.append(item)

        return ret

    def get_valid_domain_connections(self, ontology_concept_id, lang=settings.LANGUAGE_CODE):
        return self.get_related_properties(ontology_concept_id, direction='up', lang=lang)

    def get_valid_range_connections(self, ontology_concept_id, lang=settings.LANGUAGE_CODE):
        return self.get_related_properties(ontology_concept_id, direction='down', lang=lang)

    def get_related_properties(self, ontology_concept_id, direction='down', lang=settings.LANGUAGE_CODE):
        """
        gets the ontology properties that are allowed between the given ontology class and other ontology classes
        returned ontology properties include their related classes

        Arguments:
        ontology_concept_id -- the id of the ontology concept

        Keyword Arguments:
        lang -- the language of the returned values

        """

        ret = []
        concept_graph = Ontology().get(id=ontology_concept_id, include_subconcepts=True, 
            include=None, depth_limit=2, pathway_filter=(Q(relationtype='hasDomainClass') | Q(relationtype='hasRangeClass')), lang=lang)

        for subconcept in concept_graph.subconcepts:
            if subconcept.relationshiptype == 'hasDomainClass' if direction == 'down' else 'hasRangeClass':
                item = {
                    'ontology_property': subconcept,
                    'ontology_classes': []
                }
                for ontology_class in subconcept.subconcepts:
                    if ontology_class.relationshiptype == 'hasRangeClass' if direction == 'down' else 'hasDomainClass':
                        for subclass in ontology_class.get_subclasses(include=['label'], lang=lang):
                            item['ontology_classes'].append(subclass)

                ret.append(item)

        return ret

    def get_subclasses(self, id='', exclude=[], include=[], depth_limit=None, lang=settings.LANGUAGE_CODE, **kwargs):
        """
        reutrns a set of subclasses of self including self

        Arguments:
        id -- id of the ontology class to use as the root, defaults to self.id

        Keyword Arguments:
        exclude -- a list of value types to exclude from the result

        include -- a list of value types to include in the result

        depth_limit -- level to limit the depth to crawl the tree

        lang -- the language of the returned values

        """

        id = id if id != '' else self.id
        if id != '' and id != None:
            self.load(models.Concept.objects.get(pk=id))

            ret = kwargs.pop('ret', set())
            ret.add(self)
            downlevel = kwargs.pop('downlevel', 0)
            depth_limit = depth_limit if depth_limit == None else int(depth_limit)

            if include != None:
                self.values = []
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

            if depth_limit == None or downlevel < depth_limit:
                if depth_limit != None:
                    downlevel = downlevel + 1

                for relation in models.Relation.objects.filter(conceptfrom=self.id, relationtype='subClassOf'):
                    subconcept = Ontology().get_subclasses(id=relation.conceptto_id, exclude=exclude, 
                        include=include, depth_limit=depth_limit, downlevel=downlevel, ret=ret)
                    self.relationshiptype = relation.relationtype.pk

        return ret

    def get_superclasses(self, id='', exclude=[], include=[], depth_limit=None, lang=settings.LANGUAGE_CODE, **kwargs):
        """
        reutrns a set of superclasses of self including self

        Arguments:
        id -- id of the ontology class to use as the root, defaults to self.id

        Keyword Arguments:
        exclude -- a list of value types to exclude from the result

        include -- a list of value types to include in the result

        depth_limit -- level to limit the depth to crawl the tree

        lang -- the language of the returned values

        """

        id = id if id != '' else self.id
        if id != '' and id != None:
            self.load(models.Concept.objects.get(pk=id))

            ret = kwargs.pop('ret', set())
            ret.add(self)
            downlevel = kwargs.pop('downlevel', 0)
            depth_limit = depth_limit if depth_limit == None else int(depth_limit)

            if include != None:
                self.values = []
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

            if depth_limit == None or downlevel < depth_limit:
                if depth_limit != None:
                    downlevel = downlevel + 1

                for relation in models.Relation.objects.filter(conceptto=self.id, relationtype='subClassOf'):
                    parentconcepts = Ontology().get_superclasses(id=relation.conceptfrom_id, exclude=exclude, 
                        include=include, depth_limit=depth_limit, downlevel=downlevel, ret=ret)
                    self.relationshiptype = relation.relationtype.pk
                    #ret.append(parentconcepts[-1])
        return ret

    def simplify(self, lang=settings.LANGUAGE_CODE):
        return {
            'value': self.get_preflabel(lang=lang).value,
            'id': self.id
        }