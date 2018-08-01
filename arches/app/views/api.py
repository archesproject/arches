import json
import uuid
from django.shortcuts import render
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
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
from arches.app.utils.response import JSONResponse
from arches.app.utils.decorators import can_read_resource_instance, can_edit_resource_instance, can_read_concept
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.data_management.resources.exporter import ResourceExporter
from arches.app.utils.data_management.resources.formats.rdffile import JsonLdReader
from arches.app.utils.permission_backend import user_can_read_resources
from arches.app.utils.permission_backend import user_can_edit_resources
from arches.app.utils.permission_backend import user_can_read_concepts
from arches.app.utils.decorators import group_required


class CouchdbProxy(ProxyView):
    #check user credentials here
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


@method_decorator(csrf_exempt, name='dispatch')
class Resources(APIBase):

    class AmbiguousGraphException(Exception):
        def __init__(self):
            # self.expression = expression
            self.message = 'Graph is ambiguous, need to inspect further down the graph to find the right node'

    class DataDoesNotMatchGraphException(Exception):
        def __init__(self):
            # self.expression = expression
            self.message = 'A node in the supplied data does not match any node in the subject graph'

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

    @method_decorator(can_read_resource_instance())
    def get(self, request, resourceid=None):
        format = request.GET.get('format', 'json-ld')
        try:
            indent = int(request.GET.get('indent', None))
        except:
            indent = None

        if resourceid:
            try:
                exporter = ResourceExporter(format=format)
                output = exporter.writer.write_resources(resourceinstanceids=[resourceid], indent=indent, user=request.user)
                out = output[0]['outputfile'].getvalue()
            except models.ResourceInstance.DoesNotExist:
                return JSONResponse(status=404)
            except:
                return JSONResponse(status=500)
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

            start = ((page-1)*page_size) + 1
            end = start+page_size

            base_url = "%s%s" % (settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT, reverse('resources',args=['']).lstrip('/'))
            out = {
                "@context": "https://www.w3.org/ns/ldp/",
                "@id": "",
                "@type": "ldp:BasicContainer",
                # Here we actually mean the name
                #"label": str(model.name),
                "ldp:contains": ["%s%s" % (base_url, resourceid) for resourceid in list(Resource.objects.values_list('pk', flat=True).order_by('pk')[start:end])]
            }

        return JSONResponse(out, indent=indent)

    def put(self, request, resourceid):
        if user_can_edit_resources(user=request.user):
            data = JSONDeserializer().deserialize(request.body)
            #print data
            reader = JsonLdReader()
            reader.read_resource(data)
        else:
            return JSONResponse(status=500)

        return JSONResponse(self.get(request, resourceid))

    def post(self, request, resourceid):
        if user_can_edit_resources(user=request.user):
            data = JSONDeserializer().deserialize(request.body)
            graph = Graph.objects.get(graphid=resourceid)
            graphtree = graph.get_tree()



            # check that the current json-ld @type is unique among nodes within the graph at that level of depth
            # if it's unique apply the node id from the graph to the json-ld value
            # if it's not unique then:
            #     check the children @types and compare to teh graphs children, repeat until you find a match

            def findOntologyProperties(o):
                keys = []
                try:
                    for key in o.keys():
                        if key != '@type' and key != '@id' and key != '@archesid':
                            keys.append(key)
                except:
                    pass

                return keys


            def findBranch(node, ontology_property, jsonld_graph):
                """
                    EXAMPLE JSONLD GRAPH:
                    --------------------
                    {
                        "@id": "http://localhost:8000/tile/eed92cf9-b9cd-4e99-9e88-8fb34a0be257/node/e456023d-fa36-11e6-9e3e-026d961c88e6",
                        "@type": "http://www.cidoc-crm.org/cidoc-crm/E12_Production",
                        "http://www.ics.forth.gr/isl/CRMdig/L54_is_same-as": [
                            {
                                "@id": "http://localhost:8000/tile/9fcd9141-930c-4303-b176-78480efbd3d9/node/e4560237-fa36-11e6-9e3e-026d961c88e6",
                                "@type": "http://www.cidoc-crm.org/cidoc-crm/E17_Type_Assignment",
                                "http://www.cidoc-crm.org/cidoc-crm/P42_assigned": [
                                    {
                                        "@id": "http://localhost:8000/tile/9fcd9141-930c-4303-b176-78480efbd3d9/node/e456024f-fa36-11e6-9e3e-026d961c88e6",
                                        "@type": "http://www.cidoc-crm.org/cidoc-crm/E55_Type",
                                        "http://www.w3.org/1999/02/22-rdf-syntax-ns#value": "[u'dfc1fa9b-e3c8-459d-a3fa-d65e1443b9e7']"
                                    },
                                    {
                                        "@id": "http://localhost:8000/tile/9fcd9141-930c-4303-b176-78480efbd3d9/node/e4560246-fa36-11e6-9e3e-026d961c88e6",
                                        "@type": "http://www.cidoc-crm.org/cidoc-crm/E55_Type",
                                        "http://www.w3.org/1999/02/22-rdf-syntax-ns#value": "a18ed9a3-4924-4cf0-a9a7-82d8c3aefbe0"
                                    }
                                ],
                            }
                        ]
                    }
                """
                found = []
                for child in node['children']:
                    # print 'edge'
                    # print ontology_property
                    # print child['parent_edge'].ontologyproperty
                    if child['parent_edge'].ontologyproperty == ontology_property and child['node'].ontologyclass == jsonld_graph['@type']:
                        found.append(child)

                if len(found) == 1:
                    return found[0]
                elif len(found) > 1:
                    raise self.AmbiguousGraphException()
                else:
                    raise self.DataDoesNotMatchGraphException()
                    # no node was found
                    # graph and supplied json don't match

            def getPaths(jsonld, ontology_prop=None, graph=None, parent_node=None, tileid='0'):
                #print keys
                #print "-------------------"
                # p = root[:]
                # p.append('%s' % (jsonld['@type']))
                if not isinstance(jsonld, list):
                    jsonld = [jsonld]

                #tileid = tileid = 0 if tileid is None else (tileid + 1)

                for jsonld_node in jsonld:
                    if parent_node is not None:
                        try:
                            print ontology_prop
                            # print parent_node
                            # print parent_node['name']
                            print 'searching for %s' % jsonld_node['@type']
                            branch = findBranch(parent_node, ontology_prop, jsonld_node)
                            if branch['node'].nodegroup != parent_node['node'].nodegroup:
                                # self.tile_id = self.tile_id + 1
                                #tileid = ("%s_%s") % (tileid, str(self.tile_id))
                                tileid = uuid.uuid4()

                        except self.DataDoesNotMatchGraphException as e:
                            print 'ignoring data for now'
                        except self.AmbiguousGraphException as e:
                            print 'AmbiguousGraphException'
                            branch = None
                        
                    else:
                        branch = graph
                        
                    
                    ontology_properties = findOntologyProperties(jsonld_node)
                    if len(ontology_properties) > 0 and branch is not None:
                        jsonld_node['@archesid'] = '%stile/%s/node/%s' % (settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT, tileid, branch['node'].nodeid)
                        for ontology_property in ontology_properties:
                            print ontology_property
                            # if key == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#value':
                            #     #p.append('%s - %s' % (jsonld_node['@type'], jsonld_node[key]))
                            #     result.append(p)
                            # else:
                            if ontology_property != "http://www.w3.org/1999/02/22-rdf-syntax-ns#value":
                                getPaths(jsonld_node[ontology_property], ontology_prop=ontology_property, graph=None, parent_node=branch, tileid=tileid)
                            else:
                                print 'here'
                    # else:
                    #     result.append(p)
                return jsonld

            # import ipdb
            # ipdb.set_trace()
            paths = getPaths(data, ontology_prop=None, graph=graphtree, parent_node=None)

        try:
            indent = int(request.POST.get('indent', None))
        except:
            indent = None
        return JSONResponse(data, indent=indent)

    def traverse_json_ld_graph(self, func, scope=None, **kwargs):
        """
        Traverses a concept graph from self to leaf (direction='down') or root (direction='up') calling
        the given function on each node, passes an optional scope to each function

        Return a value from the function to prematurely end the traversal

        """

        if scope == None:
            ret = func(self, **kwargs)
        else:
            ret = func(self, scope, **kwargs)

        # break out of the traversal if the function returns a value
        if ret != None:
            return ret

        for subconcept in self.subconcepts:
            ret = subconcept.traverse(func, direction, scope, _cache=_cache, **kwargs)
            if ret != None:
                return ret


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
                except:
                    return JSONResponse(status=500)
            else:
                return JSONResponse(status=500)
        else:
            return JSONResponse(status=500)

        return JSONResponse(ret, indent=indent)
