from arches.app.models import models
from arches.app.utils.response import JSONResponse
from arches.app.views.api import APIBase


class OntologyProperty(APIBase):
    def get(self, request):
        domain_ontology_class = request.GET.get("domain_ontology_class", None)
        range_ontology_class = request.GET.get("range_ontology_class", None)
        ontologyid = request.GET.get("ontologyid", "sdl")

        ret = []
        if domain_ontology_class and range_ontology_class:
            ontology_classes = models.OntologyClass.objects.get(
                source=domain_ontology_class
            )
            for ontologyclass in ontology_classes.target["down"]:
                if range_ontology_class in ontologyclass["ontology_classes"]:
                    ret.append(ontologyclass["ontology_property"])

        return JSONResponse(ret)
