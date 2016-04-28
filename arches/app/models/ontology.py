from django.conf import settings
from arches.app.models.concept import Concept

class Ontology(Concept):

    def get_related_properties(self, ontology_concept_id, lang=settings.LANGUAGE_CODE):
        ret = {
            'properties': [],
            'classes': []
        }
        concept_graph = Concept().get(id=ontology_concept_id, include_subconcepts=True,
                depth_limit=2, lang=lang)
        for subconcept in concept_graph.subconcepts:
            if subconcept.relationshiptype == "hasDomainClass":
                ret['properties'].append(subconcept)

        return ret