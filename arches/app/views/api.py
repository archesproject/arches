import os
import json
import uuid
import re
from django.shortcuts import render
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction
from django.db.models import Q
from django.http.request import QueryDict
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from revproxy.views import ProxyView
from arches.app.models import models
from arches.app.models.concept import Concept
from arches.app.models.graph import Graph
from arches.app.models.mobile_survey import MobileSurvey
from arches.app.models.resource import Resource
from arches.app.models.system_settings import settings
from arches.app.utils.skos import SKOSWriter
from arches.app.utils.response import JSONResponse
from arches.app.utils.decorators import can_read_resource_instance, can_edit_resource_instance, can_read_concept
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.data_management.resources.exporter import ResourceExporter
from arches.app.utils.data_management.resources.formats.rdffile import JsonLdReader
from arches.app.utils.permission_backend import user_can_read_resources
from arches.app.utils.permission_backend import user_can_edit_resources
from arches.app.utils.permission_backend import user_can_read_concepts
from arches.app.utils.decorators import group_required
from pyld.jsonld import compact, frame, from_rdf
from rdflib import RDF
from rdflib.namespace import SKOS, DCTERMS

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class CouchdbProxy(ProxyView):
    # check user credentials here
    upstream = settings.COUCHDB_URL


class APIBase(View):

    def dispatch(self, request, *args, **kwargs):
        get_params = request.GET.copy()
        accept = request.META.get('HTTP_ACCEPT')
        format = request.GET.get('format', False)
        format_values = {
            'application/ld+json': 'json-ld',
            'application/json': 'json',
            'application/xml': 'xml',
        }
        if not format and accept in format_values:
            get_params['format'] = format_values[accept]
        for key, value in request.META.iteritems():
            if key.startswith('HTTP_X_ARCHES_'):
                if key.replace('HTTP_X_ARCHES_', '').lower() not in request.GET:
                    get_params[key.replace('HTTP_X_ARCHES_', '').lower()] = value
        get_params._mutable = False
        request.GET = get_params
        return super(APIBase, self).dispatch(request, *args, **kwargs)


class Surveys(APIBase):

    def get(self, request):
        group_ids = list(request.user.groups.values_list('id', flat=True))
        projects = MobileSurvey.objects.filter(Q(users__in=[request.user]) | Q(groups__in=group_ids), active=True)
        response = JSONResponse(projects, indent=4)
        return response


@method_decorator(csrf_exempt, name='dispatch')
class Resources(APIBase):

    # context = [{
    #     "@context": {
    #         "id": "@id",
    #         "type": "@type",
    #         "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    #         "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    #         "crm": "http://www.cidoc-crm.org/cidoc-crm/",
    #         "la": "https://linked.art/ns/terms/",

    #         "Right": "crm:E30_Right",
    #         "LinguisticObject": "crm:E33_Linguistic_Object",
    #         "Name": "la:Name",
    #         "Identifier": "crm:E42_Identifier",
    #         "Language": "crm:E56_Language",
    #         "Type": "crm:E55_Type",

    #         "label": "rdfs:label",
    #         "value": "rdf:value",
    #         "classified_as": "crm:P2_has_type",
    #         "referred_to_by": "crm:P67i_is_referred_to_by",
    #         "language": "crm:P72_has_language",
    #         "includes": "crm:P106_is_composed_of",
    #         "identified_by": "crm:P1_is_identified_by"
    #     }
    # },{
    #     "@context": "https://linked.art/ns/v1/linked-art.json"
    # }]

    def get(self, request, resourceid=None):
        if user_can_read_resources(user=request.user):
            allowed_formats = ['json', 'json-ld']
            format = request.GET.get('format', 'json-ld')
            if format not in allowed_formats:
                return JSONResponse(status=406, reason='incorrect format specified, only %s formats allowed' % allowed_formats)

            try:
                indent = int(request.GET.get('indent', None))
            except:
                indent = None

            if resourceid:
                if format == 'json-ld':
                    try:
                        exporter = ResourceExporter(format=format)
                        output = exporter.writer.write_resources(
                            resourceinstanceids=[resourceid], indent=indent, user=request.user)
                        out = output[0]['outputfile'].getvalue()
                    except models.ResourceInstance.DoesNotExist:
                        return JSONResponse(status=404)
                    except Exception as e:
                        return JSONResponse(status=500, reason=e)
                elif format == 'json':
                    out = Resource.objects.get(pk=resourceid)
                    out.load_tiles()
            else:
                #
                # The following commented code would be what you would use if you wanted to use the rdflib module,
                # the problem with using this is that items in the "ldp:contains" array don't maintain a consistent order
                #

                # archesproject = Namespace(settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT)
                # ldp = Namespace('https://www.w3.org/ns/ldp/')

                # g = Graph()
                # g.bind('archesproject', archesproject, False)
                # g.add((archesproject['resources'], RDF.type, ldp['BasicContainer']))

                # base_url = "%s%s" % (settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT, reverse('resources',args=['']).lstrip('/'))
                # for resourceid in list(Resource.objects.values_list('pk', flat=True).order_by('pk')[:10]):
                #     g.add((archesproject['resources'], ldp['contains'], URIRef("%s%s") % (base_url, resourceid) ))

                # value = g.serialize(format='nt')
                # out = from_rdf(str(value), options={format:'application/nquads'})
                # framing = {
                #     "@omitDefault": True
                # }

                # out = frame(out, framing)
                # context = {
                #     "@context": {
                #         'ldp': 'https://www.w3.org/ns/ldp/',
                #         'arches': settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT
                #     }
                # }
                # out = compact(out, context, options={'skipExpansion':False, 'compactArrays': False})

                page_size = settings.API_MAX_PAGE_SIZE
                try:
                    page = int(request.GET.get('page', None))
                except:
                    page = 1

                start = ((page - 1) * page_size) + 1
                end = start + page_size

                base_url = "%s%s" % (settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT,
                                     reverse('resources', args=['']).lstrip('/'))
                out = {
                    "@context": "https://www.w3.org/ns/ldp/",
                    "@id": "",
                    "@type": "ldp:BasicContainer",
                    # Here we actually mean the name
                    #"label": str(model.name),
                    "ldp:contains": ["%s%s" % (base_url, resourceid) for resourceid in list(Resource.objects.values_list('pk', flat=True).order_by('pk')[start:end])]
                }

            return JSONResponse(out, indent=indent)
        else:
            return JSONResponse(status=403)

    def put(self, request, resourceid):
        try:
            indent = int(request.POST.get('indent', None))
        except:
            indent = None

        try:
            if user_can_edit_resources(user=request.user):
                data = JSONDeserializer().deserialize(request.body)
                reader = JsonLdReader()
                reader.read_resource(data, use_ids=True)
                if reader.errors:
                    response = []
                    for value in reader.errors.itervalues():
                        response.append(value.message)
                    return JSONResponse(data, indent=indent, status=400, reason=response)
                else:
                    response = []
                    for resource in reader.resources:
                        if resourceid != str(resource.pk):
                            raise Exception(
                                'Resource id in the URI does not match the resource @id supplied in the document')
                        old_resource = Resource.objects.get(pk=resource.pk)
                        old_resource.load_tiles()
                        old_tile_ids = set([str(tile.pk) for tile in old_resource.tiles])
                        new_tile_ids = set([str(tile.pk) for tile in resource.get_flattened_tiles()])
                        tileids_to_delete = old_tile_ids.difference(new_tile_ids)
                        tiles_to_delete = models.TileModel.objects.filter(pk__in=tileids_to_delete)
                        with transaction.atomic():
                            tiles_to_delete.delete()
                            resource.save(request=request)
                        response.append(JSONDeserializer().deserialize(
                            self.get(request, resource.resourceinstanceid).content))
                    return JSONResponse(response, indent=indent)
            else:
                return JSONResponse(status=403)
        except Exception as e:
            return JSONResponse(status=500, reason=e)

    def post(self, request, resourceid=None):
        try:
            indent = int(request.POST.get('indent', None))
        except:
            indent = None

        try:
            if user_can_edit_resources(user=request.user):
                data = JSONDeserializer().deserialize(request.body)
                reader = JsonLdReader()
                reader.read_resource(data)
                if reader.errors:
                    response = []
                    for value in reader.errors.itervalues():
                        response.append(value.message)
                    return JSONResponse(data, indent=indent, status=400, reason=response)
                else:
                    response = []
                    for resource in reader.resources:
                        with transaction.atomic():
                            resource.save(request=request)
                        response.append(JSONDeserializer().deserialize(
                            self.get(request, resource.resourceinstanceid).content))
                    return JSONResponse(response, indent=indent)
            else:
                return JSONResponse(status=403)
        except Exception as e:
            return JSONResponse(status=500, reason=e)

    def delete(self, request, resourceid):
        if user_can_edit_resources(user=request.user):
            try:
                resource_instance = Resource.objects.get(pk=resourceid)
                resource_instance.delete()
            except models.ResourceInstance.DoesNotExist:
                return JSONResponse(status=404)
        else:
            return JSONResponse(status=500)

        return JSONResponse(status=200)


@method_decorator(csrf_exempt, name='dispatch')
class Concepts(APIBase):

    def get(self, request, conceptid=None):
        if user_can_read_concepts(user=request.user):
            allowed_formats = ['json', 'json-ld']
            format = request.GET.get('format', 'json-ld')
            if format not in allowed_formats:
                return JSONResponse(status=406, reason='incorrect format specified, only %s formats allowed' % allowed_formats)

            include_subconcepts = request.GET.get('includesubconcepts', 'true') == 'true'
            include_parentconcepts = request.GET.get('includeparentconcepts', 'true') == 'true'
            include_relatedconcepts = request.GET.get('includerelatedconcepts', 'true') == 'true'

            depth_limit = request.GET.get('depthlimit', None)
            lang = request.GET.get('lang', settings.LANGUAGE_CODE)

            try:
                indent = int(request.GET.get('indent', None))
            except:
                indent = None
            if conceptid:
                try:
                    ret = []
                    concept_graph = Concept().get(id=conceptid, include_subconcepts=include_subconcepts,
                                                  include_parentconcepts=include_parentconcepts, include_relatedconcepts=include_relatedconcepts,
                                                  depth_limit=depth_limit, up_depth_limit=None, lang=lang)

                    ret.append(concept_graph)
                except models.Concept.DoesNotExist:
                    return JSONResponse(status=404)
                except Exception as e:
                    return JSONResponse(status=500, reason=e)
            else:
                return JSONResponse(status=500)
        else:
            return JSONResponse(status=500)

        if format == 'json-ld':
            try:
                skos = SKOSWriter()
                value = skos.write(ret, format="nt")
                js = from_rdf(str(value), options={format: 'application/nquads'})

                context = [{
                    "@context": {
                        "skos": SKOS,
                        "dcterms": DCTERMS,
                        "rdf": str(RDF)
                    }
                }, {
                    "@context": settings.RDM_JSONLD_CONTEXT
                }]

                ret = compact(js, context)
            except Exception as e:
                return JSONResponse(status=500, reason=e)

        return JSONResponse(ret, indent=indent)
