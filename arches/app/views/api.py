import json
from django.shortcuts import render
from django.views.generic import View
from django.db.models import Q
from django.http.request import QueryDict
from revproxy.views import ProxyView
from pyld.jsonld import compact, expand, frame

from arches.app.models import models
from arches.app.models.mobile_survey import MobileSurvey
from arches.app.models.resource import Resource
from arches.app.models.system_settings import settings
from arches.app.utils.response import JSONResponse
from arches.app.utils.betterJSONSerializer import JSONSerializer
from arches.app.utils.data_management.resources.exporter import ResourceExporter


class CouchdbProxy(ProxyView):
    #check user credentials here
    upstream = settings.COUCHDB_URL


class APIBase(View):
    def dispatch(self, request, *args, **kwargs):
        get_params = request.GET.copy()
        for key, value in request.META.iteritems():
            if key.startswith('HTTP_X_ARCHES_'):
                if key.replace('HTTP_X_ARCHES_','').lower() not in request.GET:
                    get_params[key.replace('HTTP_X_ARCHES_','').lower()] = value

        get_params._mutable = False
        request.GET = get_params
        return super(APIBase, self).dispatch(request, *args, **kwargs)


class Surveys(APIBase):
    def get(self, request):
        group_ids = list(request.user.groups.values_list('id', flat=True))
        projects = MobileSurvey.objects.filter(Q(users__in=[request.user]) | Q(groups__in=group_ids), active=True)
        response = JSONResponse(projects, indent=4)
        return response


class Resources(APIBase):
    context = {
        "@context": {
            "id": "@id", 
            "type": "@type",
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "crm": "http://www.cidoc-crm.org/cidoc-crm/",
            "la": "https://linked.art/ns/terms/",

            "Right": "crm:E30_Right",
            "LinguisticObject": "crm:E33_Linguistic_Object",
            "Name": "la:Name",
            "Identifier": "crm:E42_Identifier",
            "Language": "crm:E56_Language",
            "Type": "crm:E55_Type",

            "label": "rdfs:label",
            "value": "rdf:value",
            "classified_as": "crm:P2_has_type",
            "referred_to_by": "crm:P67i_is_referred_to_by",
            "language": "crm:P72_has_language",
            "includes": "crm:P106_is_composed_of",
            "identified_by": "crm:P1_is_identified_by"
        }
    }
    def get(self, request, resourceid=None):
        if resourceid:
            format = request.GET.get('format', 'json-ld')
            exporter = ResourceExporter(format=format)
            exporter.writer.get_tiles(resourceinstanceids=[resourceid])
            graph = exporter.writer.get_rdf_graph()
            value = graph.serialize(format='json-ld', indent=4)
            js = json.loads(value)

            # Now pass to pyld to frame it so it's nested properly
            myframe = {
                "@omitDefault": True,
                # This needs to be fixed
                "@id": "http://localhost/resource/%s" % resourceid
            }

            framed = frame(js, myframe)
            out = compact(framed, self.context)
            out['@context'] = "https://linked.art/ns/v1/linked-art.json"
            value = json.dumps(out, indent=4, sort_keys=True)
            response = JSONResponse(value, indent=4)
            return response

        # modelid = kw['modelid']
        # resourceid = kw['resourceid']
        # context = self.get_context_data()
        # models = context['graph_models']
        # model = None
        # for m in models:
        #     # This shouldn't be the name, but a separate slug
        #     if m.name == modelid:
        #         model = m
        #         break
        # if model == None:
        #     return HttpResponseNotFound('<h1>Model not found</h1>')
        # if resourceid is not None:
        #     resource_instance = Resource.objects.get(pk=resourceid)
        #     list(models.TileModel.objects.filter(resourceinstance=self))
        #     if resource_instance:
        #         ri_graph = resource_instance.graph
        #         if ri_graph != model:
        #             return HttpResponseNotFound('<h1>Instance not found</h1>')
        #     else:
        #         return HttpResponseNotFound('<h1>Instance not found</h1>')              

        #     writer = RdfWriter()
        #     writer.get_tiles(resourceinstanceids=[resourceid])
        #     graph = writer.get_rdf_graph()
        #     value = graph.serialize(format='json-ld', indent=2, context=self.context)
        #     js = json.loads(value)

        #     # Now pass to pyld to frame it so it's nested properly
        #     myframe = {
        #         "@omitDefault": True,
        #         # This needs to be fixed
        #         "@id": "http://localhost/resource/%s" % resourceid
        #     }

        #     framed = frame(js, myframe)
        #     out = compact(framed, self.context)
        #     out['@context'] = "https://linked.art/ns/v1/linked-art.json"
        #     value = json.dumps(out, indent=2, sort_keys=True)

        else:
            # GET on the container
            out = {
                "@context": "https://www.w3.org/ns/ldp/",
                "id": "%sresources/%s/" % (settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT, 'modelid'),
                "type": "BasicContainer",
                # Here we actually mean the name
                #"label": str(model.name),
                "contains": list(Resource.objects.values_list('pk', flat=True).order_by('pk')[:100])
            }

            #
            # XXX: Here we should list all of the UUIDs of the instances of this model
            # in a consistent order in the contains array.
            # 

            #value = json.dumps(out, indent=2, sort_keys=True)

        return JSONResponse(out, indent=4)