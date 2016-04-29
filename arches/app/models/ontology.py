import uuid
from django.conf import settings
from operator import methodcaller
from arches.app.models import models
from arches.app.models.concept import Concept, ConceptValue
from arches.app.utils.betterJSONSerializer import JSONSerializer

class Ontology(Concept):

    def get_related_properties(self, ontology_concept_id, lang=settings.LANGUAGE_CODE):
        ret = {
            'properties': [],
            'classes': []
        }
        concept_graph = Ontology().get(id=ontology_concept_id, include_subconcepts=True, 
            include=['label'], depth_limit=2, lang=lang)

        for subconcept in concept_graph.subconcepts:
            if subconcept.relationshiptype == "hasDomainClass":
                prop = {
                    'value': subconcept.get_preflabel().value,
                    'id': subconcept.id
                }
                for ontology_class in subconcept.subconcepts:
                    prop['classes'] = []

                    subclasses = ontology_class.get_subclasses(include=['label'], lang=lang)
                    
                    def gather_subclasses(concept):
                        prop['classes'].append({
                            'value': concept.get_preflabel().value,
                            'id': concept.id
                        })

                    subclasses.traverse(gather_subclasses)

                ret['properties'].append(prop)

        return ret

    def get_subclasses(self, id='', exclude=[], include=[], depth_limit=None, lang=settings.LANGUAGE_CODE, **kwargs):
        id = id if id != '' else self.id
        
        if id != '' and id != None:
            self.load(models.Concept.objects.get(pk=id))

            nodetype = kwargs.pop('nodetype', self.nodetype)
            downlevel = kwargs.pop('downlevel', 0)
            depth_limit = depth_limit if depth_limit == None else int(depth_limit)

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

            hassubconcepts = models.Relation.objects.filter(conceptfrom=self.id, relationtype='subClassOf')[0:1]
            if len(hassubconcepts) > 0:
                self.hassubconcepts = True

            conceptrealations = models.Relation.objects.filter(conceptfrom=self.id, relationtype='subClassOf')
            if depth_limit == None or downlevel < depth_limit:
                if depth_limit != None:
                    downlevel = downlevel + 1
                for relation in conceptrealations:
                    #print 'relation.conceptto_id in _cache: %s' % (str(relation.conceptto_id) in _cache)
                    subconcept = Ontology().get_subclasses(id=relation.conceptto_id, exclude=exclude, include=include, depth_limit=depth_limit,
                        downlevel=downlevel, nodetype=nodetype)
                    subconcept.relationshiptype = relation.relationtype.pk
                    self.subconcepts.append(subconcept)

                self.subconcepts = sorted(self.subconcepts, key=methodcaller('get_sortkey', lang=lang), reverse=False)

        return self