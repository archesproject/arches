import json
import logging
import os
import re
import sys
import uuid
from django.shortcuts import render
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction
from django.db.models import Q
from django.http.request import QueryDict
from django.core import management
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from revproxy.views import ProxyView
from oauth2_provider.views import ProtectedResourceView
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
from arches.app.search.components.base import SearchFilterFactory
from pyld.jsonld import compact, frame, from_rdf
from rdflib import RDF
from rdflib.namespace import SKOS, DCTERMS

logger = logging.getLogger(__name__)

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


def userCanAccessMobileSurvey(request, surveyid=None):
    ms = MobileSurvey.objects.get(pk=surveyid)
    user = request.user
    allowed = False
    if user in ms.users.all():
        allowed = True
    else:
        users_groups = set([group.id for group in user.groups.all()])
        ms_groups = set([group.id for group in ms.groups.all()])
        if len(ms_groups.intersection(users_groups)) > 0:
            allowed = True

    return allowed


class CouchdbProxy(ProtectedResourceView, ProxyView):
    upstream = settings.COUCHDB_URL
    p = re.compile(r"project_(?P<surveyid>[\w-]{36})")

    def dispatch(self, request, path):
        try:
            if path is None or path == '':
                return super(CouchdbProxy, self).dispatch(request, path)
            else:
                m = self.p.match(path)
                surveyid = ''
                if m is not None:
                    surveyid = m.groupdict().get("surveyid")
                    if MobileSurvey.objects.filter(pk=surveyid).exists() is False:
                        message = _('The survey you are attempting to sync is no longer available on the server')
                        return JSONResponse({'notification': message}, status=500)
                    else:
                        try:
                            if userCanAccessMobileSurvey(request, surveyid):
                                return super(CouchdbProxy, self).dispatch(request, path)
                            else:
                                return JSONResponse(_('Sync Failed. User unauthorized to sync project'), status=403)
                        except Exception:
                            logger.exception(_('Unable to determine user access to collector project'))
                            pass
        except Exception:
            logger.exception(_('Failed to dispatch Couch proxy'))

        return JSONResponse(_('Sync failed'), status=500)


class APIBase(View):

    def dispatch(self, request, *args, **kwargs):
        try:
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
            for key, value in request.META.items():
                if key.startswith('HTTP_X_ARCHES_'):
                    if key.replace('HTTP_X_ARCHES_', '').lower() not in request.GET:
                        get_params[key.replace('HTTP_X_ARCHES_', '').lower()] = value
            get_params._mutable = False
            request.GET = get_params

        except Exception:
            logger.exception(_('Failed to create API request'))

        return super(APIBase, self).dispatch(request, *args, **kwargs)


class Sync(APIBase):

    def get(self, request, surveyid=None):
        can_sync = userCanAccessMobileSurvey(request, surveyid)
        if can_sync:
            try:
                logger.info("Starting sync for user {0}".format(request.user.username))
                management.call_command('mobile', operation='sync_survey', id=surveyid, user=request.user.id)
                logger.info("Sync complete for user {0}".format(request.user.username))
            except Exception:
                logger.exception(_('Sync Failed'))

            return JSONResponse(_('Sync Failed'))
        else:
            return JSONResponse(_('Sync Failed'), status=403)


class Surveys(APIBase):

    def get(self, request, surveyid=None):

        auth_header = request.META.get('HTTP_AUTHORIZATION', None)
        logger.info("Requesting projects for user: {0}".format(request.user.username))
        try:
            if hasattr(request.user, 'userprofile') is not True:
                models.UserProfile.objects.create(user=request.user)

            def get_child_cardids(card, cardset):
                for child_card in models.CardModel.objects.filter(nodegroup__parentnodegroup_id=card.nodegroup_id):
                    cardset.add(str(child_card.cardid))
                    get_child_cardids(child_card, cardset)

            group_ids = list(request.user.groups.values_list('id', flat=True))
            if request.GET.get('status', None) is not None:
                ret = {}
                surveys = MobileSurvey.objects.filter(users__in=[request.user]).distinct()
                for survey in surveys:
                    survey.deactivate_expired_survey()
                    survey = survey.serialize_for_mobile()
                    ret[survey['id']] = {}
                    for key in ['active',
                                'name',
                                'description',
                                'startdate',
                                'enddate',
                                'onlinebasemaps',
                                'bounds',
                                'tilecache']:
                        ret[survey['id']][key] = survey[key]
                response = JSONResponse(ret, indent=4)
            else:
                viewable_nodegroups = request.user.userprofile.viewable_nodegroups
                editable_nodegroups = request.user.userprofile.editable_nodegroups
                permitted_nodegroups = viewable_nodegroups.union(editable_nodegroups)
                projects = MobileSurvey.objects.filter(users__in=[request.user], active=True).distinct()
                if surveyid:
                    projects = projects.filter(pk=surveyid)

                projects_for_couch = []
                for project in projects:
                    project.deactivate_expired_survey()
                    projects_for_couch.append(project.serialize_for_mobile())

                for project in projects_for_couch:
                    project['mapboxkey'] = settings.MAPBOX_API_KEY
                    permitted_cards = set()
                    ordered_project_cards = project['cards']
                    for rootcardid in project['cards']:
                        card = models.CardModel.objects.get(cardid=rootcardid)
                        if str(card.nodegroup_id) in permitted_nodegroups:
                            permitted_cards.add(str(card.cardid))
                            get_child_cardids(card, permitted_cards)
                    project['cards'] = list(permitted_cards)
                    for graph in project['graphs']:
                        cards = []
                        for card in graph['cards']:
                            if card['cardid'] in project['cards']:
                                card['relative_position'] = ordered_project_cards.index(
                                    card['cardid']) if card['cardid'] in ordered_project_cards else None
                                cards.append(card)
                        graph['cards'] = sorted(cards, key=lambda x: x['relative_position'])
                response = JSONResponse(projects_for_couch, indent=4)
        except Exception:
            logger.exception(_('Unable to fetch collector projects'))
            response = JSONResponse(_('Unable to fetch collector projects'), indent=4)

        logger.info("Returning projects for user: {0}".format(request.user.username))
        return response


class GeoJSON(APIBase):
    def get(self, request):
        resourceid = request.GET.get('resourceid', None)
        nodeid = request.GET.get('nodeid', None)
        tileid = request.GET.get('tileid', None)
        if hasattr(request.user, 'userprofile') is not True:
            models.UserProfile.objects.create(user=request.user)
        viewable_nodegroups = request.user.userprofile.viewable_nodegroups
        nodes = models.Node.objects.filter(datatype='geojson-feature-collection', nodegroup_id__in=viewable_nodegroups)
        if nodeid is not None:
            nodes = nodes.filter(nodeid=nodeid)
        features = []
        i = 1
        for node in nodes:
            tiles = models.TileModel.objects.filter(nodegroup=node.nodegroup)
            if resourceid is not None:
                # resourceid = resourceid.split(',')
                tiles = tiles.filter(resourceinstance_id__in=resourceid.split(','))
            if tileid is not None:
                tiles = tiles.filter(tileid=tileid)
            for tile in tiles:
                data = tile.data
                try:
                    for feature_index, feature in enumerate(data[unicode(node.pk)]['features']):
                        feature['properties']['index'] = feature_index
                        feature['properties']['resourceinstanceid'] = tile.resourceinstance_id
                        feature['properties']['tileid'] = tile.pk
                        feature['properties']['nodeid'] = node.pk
                        feature['properties']['node'] = node.name
                        feature['properties']['model'] = node.graph.name
                        feature['properties']['geojson'] = '%s?tileid=%s&nodeid=%s' % (reverse('geojson'), tile.pk, node.pk)
                        feature['properties']['featureid'] = feature['id']
                        feature['id'] = i
                        i += 1
                        features.append(feature)
                except KeyError:
                    pass
        response = JSONResponse({'type': 'FeatureCollection', 'features': features})
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

    def get(self, request, resourceid=None, slug=None, graphid=None):
        if user_can_read_resources(user=request.user):
            allowed_formats = ['json', 'json-ld']
            format = request.GET.get('format', 'json-ld')
            if format not in allowed_formats:
                return JSONResponse(
                    status=406, reason='incorrect format specified, only %s formats allowed' % allowed_formats
                    )
            try:
                indent = int(request.GET.get('indent', None))
            except Exception:
                indent = None

            if resourceid:
                if format == 'json-ld':
                    try:
                        exporter = ResourceExporter(format=format)
                        output = exporter.writer.write_resources(
                            resourceinstanceids=[resourceid], indent=indent, user=request.user)
                        out = output[0]['outputfile'].getvalue()
                    except models.ResourceInstance.DoesNotExist:
                        logger.exception(
                            _("The specified resource '{0}' does not exist. JSON-LD export failed.".format(
                                resourceid
                                ))
                            )
                        return JSONResponse(status=404)
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
                except Exception:
                    page = 1

                start = ((page - 1) * page_size)
                end = start + page_size

                base_url = "%s%s" % (settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT,
                                     reverse('resources', args=['']).lstrip('/'))
                out = {
                    "@context": "https://www.w3.org/ns/ldp/",
                    "@id": "",
                    "@type": "ldp:BasicContainer",
                    # Here we actually mean the name
                    #"label": str(model.name),
                    "ldp:contains": ["%s%s" % (base_url, resourceid) for resourceid in list(Resource.objects.values_list('pk', flat=True).
                                                                                            exclude(pk=settings.SYSTEM_SETTINGS_RESOURCE_ID).order_by('pk')[start:end])]
                }

            return JSONResponse(out, indent=indent)
        else:
            return JSONResponse(status=403)

    # def put(self, request, resourceid):
    #     try:
    #         indent = int(request.POST.get('indent', None))
    #     except:
    #         indent = None

    #     try:
    #         if user_can_edit_resources(user=request.user):
    #             data = JSONDeserializer().deserialize(request.body)
    #             reader = JsonLdReader()
    #             reader.read_resource(data, use_ids=True)
    #             if reader.errors:
    #                 response = []
    #                 for value in reader.errors.itervalues():
    #                     response.append(value.message)
    #                 return JSONResponse(data, indent=indent, status=400, reason=response)
    #             else:
    #                 response = []
    #                 for resource in reader.resources:
    #                     if resourceid != str(resource.pk):
    #                         raise Exception(
    #                             'Resource id in the URI does not match the resource @id supplied in the document')
    #                     old_resource = Resource.objects.get(pk=resource.pk)
    #                     old_resource.load_tiles()
    #                     old_tile_ids = set([str(tile.pk) for tile in old_resource.tiles])
    #                     new_tile_ids = set([str(tile.pk) for tile in resource.get_flattened_tiles()])
    #                     tileids_to_delete = old_tile_ids.difference(new_tile_ids)
    #                     tiles_to_delete = models.TileModel.objects.filter(pk__in=tileids_to_delete)
    #                     with transaction.atomic():
    #                         tiles_to_delete.delete()
    #                         resource.save(request=request)
    #                     response.append(JSONDeserializer().deserialize(
    #                         self.get(request, resource.resourceinstanceid).content))
    #                 return JSONResponse(response, indent=indent)
    #         else:
    #             return JSONResponse(status=403)
    #     except Exception as e:
    #         return JSONResponse(status=500, reason=e)

    def put(self, request, resourceid, slug=None, graphid=None):
        try:
            indent = int(request.PUT.get('indent', None))
        except Exception:
            indent = None

        if not user_can_edit_resources(user=request.user):
            return JSONResponse(status=403)
        else:
            with transaction.atomic():
                try:
                    # DELETE
                    resource_instance = Resource.objects.get(pk=resourceid)
                    resource_instance.delete()
                except models.ResourceInstance.DoesNotExist:
                    pass

                try:
                    # POST
                    data = JSONDeserializer().deserialize(request.body)
                    reader = JsonLdReader()
                    if slug is not None:
                        graphid = models.GraphModel.objects.get(slug=slug).pk
                    reader.read_resource(data, resourceid=resourceid, graphid=graphid)
                    if reader.errors:
                        response = []
                        for value in reader.errors.values():
                            response.append(value.message)
                        return JSONResponse({"error": response}, indent=indent, status=400)
                    else:
                        response = []
                        for resource in reader.resources:
                            with transaction.atomic():
                                resource.save(request=request)
                            response.append(JSONDeserializer().deserialize(
                                self.get(request, resource.resourceinstanceid).content))
                        return JSONResponse(response, indent=indent, status=201)
                except models.ResourceInstance.DoesNotExist:
                    return JSONResponse(status=404)
                except Exception as e:
                    return JSONResponse({"error": "resource data could not be saved"}, status=500, reason=e)

    def post(self, request, resourceid=None, slug=None, graphid=None):
        try:
            indent = int(request.POST.get('indent', None))
        except Exception:
            indent = None

        try:
            if user_can_edit_resources(user=request.user):
                data = JSONDeserializer().deserialize(request.body)
                reader = JsonLdReader()
                if slug is not None:
                    graphid = models.GraphModel.objects.get(slug=slug).pk
                reader.read_resource(data, graphid=graphid)
                if reader.errors:
                    response = []
                    for value in reader.errors.values():
                        response.append(value.message)
                    return JSONResponse({"error": response}, indent=indent, status=400)
                else:
                    response = []
                    for resource in reader.resources:
                        with transaction.atomic():
                            resource.save(request=request)
                        response.append(JSONDeserializer().deserialize(
                            self.get(request, resource.resourceinstanceid).content))
                    return JSONResponse(response, indent=indent, status=201)
            else:
                return JSONResponse(status=403)
        except Exception as e:
            if settings.DEBUG is True:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                formatted = traceback.format_exception(exc_type, exc_value, exc_traceback)
                if len(formatted):
                    for message in formatted:
                        print(message)
            return JSONResponse({"error": "resource data could not be saved: %s" % e}, status=500, reason=e)

    def delete(self, request, resourceid, slug=None, graphid=None):
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
            except Exception:
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


def get_resource_relationship_types():
    resource_relationship_types = Concept().get_child_collections('00000000-0000-0000-0000-000000000005')
    default_relationshiptype_valueid = None
    for relationship_type in resource_relationship_types:
        if relationship_type[0] == '00000000-0000-0000-0000-000000000007':
            default_relationshiptype_valueid = relationship_type[2]
    relationship_type_values = {'values': [{'id': str(c[2]), 'text':str(
        c[1])} for c in resource_relationship_types], 'default': str(default_relationshiptype_valueid)}
    return relationship_type_values


class Card(APIBase):

    def get(self, request, resourceid):
        try:
            resource_instance = Resource.objects.get(pk=resourceid)
            graph = resource_instance.graph
        except Resource.DoesNotExist:
            graph = models.GraphModel.objects.get(pk=resourceid)
            resourceid = None
            resource_instance = None
            pass
        nodes = graph.node_set.all()

        nodegroups = []
        editable_nodegroups = []
        for node in nodes:
            if node.is_collector:
                added = False
                if request.user.has_perm('write_nodegroup', node.nodegroup):
                    editable_nodegroups.append(node.nodegroup)
                    nodegroups.append(node.nodegroup)
                    added = True
                if not added and request.user.has_perm('read_nodegroup', node.nodegroup):
                    nodegroups.append(node.nodegroup)

        nodes = nodes.filter(nodegroup__in=nodegroups)
        cards = graph.cardmodel_set.order_by('sortorder').filter(
            nodegroup__in=nodegroups).prefetch_related('cardxnodexwidget_set')
        cardwidgets = [widget for widgets in [card.cardxnodexwidget_set.order_by(
            'sortorder').all() for card in cards] for widget in widgets]
        datatypes = models.DDataType.objects.all()
        user_is_reviewer = request.user.groups.filter(name='Resource Reviewer').exists()
        widgets = models.Widget.objects.all()
        card_components = models.CardComponent.objects.all()

        if resource_instance is None:
            tiles = []
            displayname = _('New Resource')
        else:
            displayname = resource_instance.displayname
            if displayname == 'undefined':
                displayname = _('Unnamed Resource')
            if str(resource_instance.graph_id) == settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID:
                displayname = _("System Settings")

            tiles = resource_instance.tilemodel_set.order_by('sortorder').filter(nodegroup__in=nodegroups)
            provisionaltiles = []
            for tile in tiles:
                append_tile = True
                isfullyprovisional = False
                if tile.provisionaledits is not None:
                    if len(list(tile.provisionaledits.keys())) > 0:
                        if len(tile.data) == 0:
                            isfullyprovisional = True
                        if user_is_reviewer is False:
                            if str(request.user.id) in tile.provisionaledits:
                                tile.provisionaledits = {
                                    str(request.user.id): tile.provisionaledits[str(request.user.id)]}
                                tile.data = tile.provisionaledits[str(request.user.id)]['value']
                            else:
                                if isfullyprovisional is True:
                                    # if the tile IS fully provisional and the current user is not the owner,
                                    # we don't send that tile back to the client.
                                    append_tile = False
                                else:
                                    # if the tile has authoritaive data and the current user is not the owner,
                                    # we don't send the provisional data of other users back to the client.
                                    tile.provisionaledits = None
                if append_tile is True:
                    provisionaltiles.append(tile)
            tiles = provisionaltiles

        cards = JSONSerializer().serializeToPython(cards)
        editable_nodegroup_ids = [str(nodegroup.pk) for nodegroup in editable_nodegroups]
        for card in cards:
            card['is_writable'] = False
            if str(card['nodegroup_id']) in editable_nodegroup_ids:
                card['is_writable'] = True

        context = {
            'resourceid': resourceid,
            'displayname': displayname,
            'tiles': tiles,
            'cards': cards,
            'nodegroups': nodegroups,
            'nodes': nodes,
            'cardwidgets': cardwidgets,
            'datatypes': datatypes,
            'userisreviewer': user_is_reviewer,
            'widgets': widgets,
            'card_components': card_components,
        }

        return JSONResponse(context, indent=4)


class SearchComponentData(APIBase):

    def get(self, request, componentname):
        search_filter_factory = SearchFilterFactory(request)
        search_filter = search_filter_factory.get_filter(componentname)
        if search_filter:
            return JSONResponse(search_filter.view_data())
        return JSONResponse(status=404)
