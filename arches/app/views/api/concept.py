from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from pyld.jsonld import compact, from_rdf
from rdflib import RDF
from rdflib.namespace import DCTERMS, SKOS

from arches.app.models import models
from arches.app.models.concept import Concept
from arches.app.models.system_settings import settings
from arches.app.utils.permission_backend import user_can_read_concepts
from arches.app.utils.response import JSONErrorResponse, JSONResponse
from arches.app.utils.skos import SKOSWriter
from arches.app.views.api import APIBase


@method_decorator(csrf_exempt, name="dispatch")
class Concepts(APIBase):
    def get(self, request, conceptid=None):
        if user_can_read_concepts(user=request.user):
            allowed_formats = ["json", "json-ld"]
            format = request.GET.get("format", "json-ld")
            if format not in allowed_formats:
                return JSONErrorResponse(
                    status=406,
                    reason="incorrect format specified, only %s formats allowed"
                    % allowed_formats,
                )

            include_subconcepts = (
                request.GET.get("includesubconcepts", "true") == "true"
            )
            include_parentconcepts = (
                request.GET.get("includeparentconcepts", "true") == "true"
            )
            include_relatedconcepts = (
                request.GET.get("includerelatedconcepts", "true") == "true"
            )

            depth_limit = request.GET.get("depthlimit", None)
            lang = request.GET.get("lang", settings.LANGUAGE_CODE)

            try:
                indent = int(request.GET.get("indent", None))
            except Exception:
                indent = None
            if conceptid:
                try:
                    ret = []
                    concept_graph = Concept().get(
                        id=conceptid,
                        include_subconcepts=include_subconcepts,
                        include_parentconcepts=include_parentconcepts,
                        include_relatedconcepts=include_relatedconcepts,
                        depth_limit=depth_limit,
                        up_depth_limit=None,
                        lang=lang,
                    )

                    ret.append(concept_graph)
                except models.Concept.DoesNotExist:
                    return JSONErrorResponse(status=404)
                except Exception as e:
                    return JSONErrorResponse(status=500, reason=e)
            else:
                return JSONErrorResponse(status=400)
        else:
            return JSONErrorResponse(
                status=401 if request.user.username == "anonymous" else 403
            )

        if format == "json-ld":
            try:
                skos = SKOSWriter()
                value = skos.write(ret, format="nt")
                js = from_rdf(
                    value.decode("utf-8"), options={format: "application/nquads"}
                )

                context = [
                    {"@context": {"skos": SKOS, "dcterms": DCTERMS, "rdf": str(RDF)}},
                    {"@context": settings.RDM_JSONLD_CONTEXT},
                ]

                ret = compact(js, context)
            except Exception as e:
                return JSONErrorResponse(status=500, reason=e)

        return JSONResponse(ret, indent=indent)
