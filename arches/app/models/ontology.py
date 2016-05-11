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

    def get_valid_ontology_concepts(self, parent_node, child_properties=[], lang=settings.LANGUAGE_CODE):
        ret = []
        ontology_classes = set()
        for child_property in child_properties:
            #print child_property['ontologyclass_id']
            ontology_property = models.Relation.objects.get(conceptto_id=child_property['ontologyclass_id'])
            #print JSONSerializer().serialize(ontology_property.conceptfrom)
            subclasses = Ontology().get_subclasses(id=ontology_property.conceptfrom_id, include=['label'], lang=lang)

            if len(ontology_classes) == 0:
                ontology_classes = subclasses
            else:
                ontology_classes = ontology_classes.intersection(subclasses)

            if len(ontology_classes) == 0:
                break

        related_properties = self.get_related_properties(parent_node['ontologyclass_id'], lang=lang)
        for related_property in related_properties:
            related_property['ontology_classes'] = set(related_property['ontology_classes']).intersection(ontology_classes)

            if len(related_property['ontology_classes']) > 0:
                item = {
                    'ontology_property':{
                        'value': related_property['ontology_property'].get_preflabel(lang=lang).value,
                        'id': related_property['ontology_property'].id
                    },
                    'ontology_classes':[]
                }
                for ontology_class in related_property['ontology_classes']:
                    item['ontology_classes'].append({
                        'value': ontology_class.get_preflabel(lang=lang).value,
                        'id': ontology_class.id
                    })
                ret.append(item)

        return ret


    #get_valid_ontology_concepts_from_parent

    def get_related_properties(self, ontology_concept_id, lang=settings.LANGUAGE_CODE):
        """
        gets the allowed connections between the given ontology concept class and other ontology classes

        Arguments:
        ontology_concept_id -- the id of the ontology concept

        Keyword Arguments:
        lang -- the language of the returned values

        """

        ret = []
        concept_graph = Ontology().get(id=ontology_concept_id, include_subconcepts=True, 
            include=['label'], depth_limit=2, lang=lang)

        for subconcept in concept_graph.subconcepts:
            if subconcept.relationshiptype == "hasDomainClass":
                item = {
                    'ontology_property': subconcept,
                    'ontology_classes': []
                }
                for ontology_class in subconcept.subconcepts:
                    if ontology_class.relationshiptype == "hasRangeClass":
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