import importlib
import json
import logging
import os
import re
import sys
import uuid
from io import StringIO
from oauth2_provider.views import ProtectedResourceView
from pyld.jsonld import compact, frame, from_rdf
from rdflib import RDF
from rdflib.namespace import SKOS, DCTERMS
from revproxy.views import ProxyView
from slugify import slugify
from urllib import parse
from django.shortcuts import render
from django.views.generic import View
from django.db import transaction, connection
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.http.request import QueryDict
from django.core import management
from django.core.cache import cache
from django.urls import reverse
from django.utils.translation import ugettext as _
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from arches.app.models import models
from arches.app.models.concept import Concept
from arches.app.models.card import Card as CardProxyModel
from arches.app.models.graph import Graph
from arches.app.models.mobile_survey import MobileSurvey
from arches.app.models.resource import Resource
from arches.app.models.system_settings import settings
from arches.app.models.tile import Tile as TileProxyModel
from arches.app.views.tile import TileData as TileView
from arches.app.utils.skos import SKOSWriter
from arches.app.utils.response import JSONResponse
from arches.app.utils.decorators import (
    can_read_concept,
    group_required
)
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.data_management.resources.exporter import ResourceExporter
from arches.app.utils.data_management.resources.formats.rdffile import JsonLdReader
from arches.app.utils.permission_backend import (
    user_can_read_resource,
    user_can_edit_resource,
    user_can_delete_resource,
    user_can_read_concepts,
    user_is_resource_reviewer,
    get_restricted_instances,
    check_resource_instance_permissions,
    get_nodegroups_by_perm,
)
from arches.app.utils.geo_utils import GeoUtils
from arches.app.search.components.base import SearchFilterFactory
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.search.search_engine_factory import SearchEngineFactory


from arches.celery import app

logger = logging.getLogger(__name__)


def userCanAccessMobileSurvey(request, surveyid=None):
    ms = MobileSurvey.objects.get(pk=surveyid)
    user = request.user
    allowed = False
    if user in ms.users.all():
        allowed = True
    else:
        users_groups = {group.id for group in user.groups.all()}
        ms_groups = {group.id for group in ms.groups.all()}
        if len(ms_groups.intersection(users_groups)) > 0:
            allowed = True

    return allowed


class CouchdbProxy(ProtectedResourceView, ProxyView):
    upstream = settings.COUCHDB_URL
    p = re.compile(r"project_(?P<surveyid>[\w-]{36})")

    def dispatch(self, request, path):
        try:
            if path is None or path == "":
                return super(CouchdbProxy, self).dispatch(request, path)
            else:
                m = self.p.match(path)
                surveyid = ""
                if m is not None:
                    surveyid = m.groupdict().get("surveyid")
                    if MobileSurvey.objects.filter(pk=surveyid).exists() is False:
                        message = _("The survey you are attempting to sync is no longer available on the server")
                        return JSONResponse({"notification": message}, status=500)
                    else:
                        try:
                            if userCanAccessMobileSurvey(request, surveyid):
                                return super(CouchdbProxy, self).dispatch(request, path)
                            else:
                                return JSONResponse(_("Sync Failed. User unauthorized to sync project"), status=403)
                        except Exception:
                            logger.exception(_("Unable to determine user access to collector project"))
                            pass
        except Exception:
            logger.exception(_("Failed to dispatch Couch proxy"))

        return JSONResponse(_("Sync failed"), status=500)


class KibanaProxy(ProxyView):
    upstream = settings.KIBANA_URL

    def dispatch(self, request, path):
        try:
            path = f"{settings.KIBANA_CONFIG_BASEPATH}/{path}"
            return super(KibanaProxy, self).dispatch(request, path)
        except Exception:
            logger.exception(_("Failed to dispatch Kibana proxy"))

        return JSONResponse(_("KibanaProxy failed"), status=500)


class APIBase(View):
    def dispatch(self, request, *args, **kwargs):
        try:
            get_params = request.GET.copy()
            accept = request.META.get("HTTP_ACCEPT")
            format = request.GET.get("format", False)
            format_values = {
                "application/ld+json": "json-ld",
                "application/json": "json",
                "application/xml": "xml",
            }
            if not format and accept in format_values:
                get_params["format"] = format_values[accept]
            for key, value in request.META.items():
                if key.startswith("HTTP_X_ARCHES_"):
                    if key.replace("HTTP_X_ARCHES_", "").lower() not in request.GET:
                        get_params[key.replace("HTTP_X_ARCHES_", "").lower()] = value
            get_params._mutable = False
            request.GET = get_params

        except Exception:
            logger.exception(_("Failed to create API request"))

        return super(APIBase, self).dispatch(request, *args, **kwargs)


class Sync(APIBase):
    def get(self, request, surveyid=None):

        can_sync = userCanAccessMobileSurvey(request, surveyid)
        if can_sync:
            synclog = models.MobileSyncLog(logid=None, survey_id=surveyid, userid=request.user.id)
            try:
                survey = MobileSurvey.objects.get(id=surveyid)
                synclog = survey.sync(userid=request.user.id, use_celery=True)
            except Exception:
                logger.exception(_("Sync Failed"))
            status = 200
            if synclog.status == "FAILED":
                status = 500

            return JSONResponse(synclog, status=status)
        else:
            return JSONResponse(_("Sync Failed"), status=403)


class CheckSyncStatus(APIBase):
    def get(self, request, synclogid=None):
        synclog = models.MobileSyncLog.objects.get(pk=synclogid)
        return JSONResponse(synclog)


class Surveys(APIBase):
    def get(self, request, surveyid=None):

        auth_header = request.META.get("HTTP_AUTHORIZATION", None)
        logger.info("Requesting projects for user: {0}".format(request.user.username))
        try:
            if hasattr(request.user, "userprofile") is not True:
                models.UserProfile.objects.create(user=request.user)

            def get_child_cardids(card, cardset):
                for child_card in models.CardModel.objects.filter(nodegroup__parentnodegroup_id=card.nodegroup_id):
                    cardset.add(str(child_card.cardid))
                    get_child_cardids(child_card, cardset)

            group_ids = list(request.user.groups.values_list("id", flat=True))
            if request.GET.get("status", None) is not None:
                ret = {}
                surveys = MobileSurvey.objects.filter(users__in=[request.user]).distinct()
                for survey in surveys:
                    survey.deactivate_expired_survey()
                    survey = survey.serialize_for_mobile()
                    ret[survey["id"]] = {}
                    for key in [
                        "active",
                        "name",
                        "description",
                        "startdate",
                        "enddate",
                        "onlinebasemaps",
                        "bounds",
                        "tilecache",
                        "image_size_limits",
                    ]:
                        ret[survey["id"]][key] = survey[key]
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
                    project["mapboxkey"] = settings.MAPBOX_API_KEY
                    permitted_cards = set()
                    ordered_project_cards = project["cards"]
                    for rootcardid in project["cards"]:
                        card = models.CardModel.objects.get(cardid=rootcardid)
                        if str(card.nodegroup_id) in permitted_nodegroups:
                            permitted_cards.add(str(card.cardid))
                            get_child_cardids(card, permitted_cards)
                    project["cards"] = list(permitted_cards)
                    for graph in project["graphs"]:
                        cards = []
                        for card in graph["cards"]:
                            if card["cardid"] in project["cards"]:
                                card["relative_position"] = (
                                    ordered_project_cards.index(card["cardid"]) if card["cardid"] in ordered_project_cards else None
                                )
                                cards.append(card)
                        unordered_cards = [card for card in cards if card["relative_position"] is None]
                        ordered_cards = [card for card in cards if card["relative_position"] is not None]
                        sorted_cards = sorted(ordered_cards, key=lambda x: x["relative_position"])
                        graph["cards"] = unordered_cards + sorted_cards
                response = JSONResponse(projects_for_couch, indent=4)
        except Exception:
            logger.exception(_("Unable to fetch collector projects"))
            response = JSONResponse(_("Unable to fetch collector projects"), indent=4)

        logger.info("Returning projects for user: {0}".format(request.user.username))
        return response


class GeoJSON(APIBase):
    se = SearchEngineFactory().create()

    def get_name(self, resource):
        module = importlib.import_module("arches.app.functions.primary_descriptors")
        PrimaryDescriptorsFunction = getattr(module, "PrimaryDescriptorsFunction")()
        functionConfig = models.FunctionXGraph.objects.filter(graph_id=resource.graph_id, function__functiontype="primarydescriptors")
        if len(functionConfig) == 1:
            return PrimaryDescriptorsFunction.get_primary_descriptor_from_nodes(resource, functionConfig[0].config["name"])
        else:
            return _("Unnamed Resource")

    def get(self, request):
        datatype_factory = DataTypeFactory()
        set_precision = GeoUtils().set_precision
        resourceid = request.GET.get("resourceid", None)
        nodeid = request.GET.get("nodeid", None)
        nodeids = request.GET.get("nodeids", None)
        tileid = request.GET.get("tileid", None)
        nodegroups = request.GET.get("nodegroups", [])
        precision = request.GET.get("precision", None)
        field_name_length = int(request.GET.get("field_name_length", 0))
        use_uuid_names = bool(request.GET.get("use_uuid_names", False))
        include_primary_name = bool(request.GET.get("include_primary_name", False))
        include_geojson_link = bool(request.GET.get("include_geojson_link", False))
        use_display_values = bool(request.GET.get("use_display_values", False))
        geometry_type = request.GET.get("type", None)
        indent = request.GET.get("indent", None)
        limit = request.GET.get("limit", None)
        page = int(request.GET.get("page", 1))
        if limit is not None:
            limit = int(limit)
        if indent is not None:
            indent = int(indent)
        if isinstance(nodegroups, str):
            nodegroups = nodegroups.split(",")
        if hasattr(request.user, "userprofile") is not True:
            models.UserProfile.objects.create(user=request.user)
        viewable_nodegroups = request.user.userprofile.viewable_nodegroups
        nodegroups = [i for i in nodegroups if i in viewable_nodegroups]
        nodes = models.Node.objects.filter(datatype="geojson-feature-collection", nodegroup_id__in=viewable_nodegroups)
        node_filter = []
        if nodeids:
            node_filter += nodeids.split(",")
        if nodeid:
            node_filter.append(nodeid)
        nodes = nodes.filter(nodeid__in=node_filter)
        nodes = nodes.order_by("sortorder")
        features = []
        i = 1
        property_tiles = models.TileModel.objects.filter(nodegroup_id__in=nodegroups)
        property_node_map = {}
        property_nodes = models.Node.objects.filter(nodegroup_id__in=nodegroups).order_by("sortorder")
        restricted_resource_ids = get_restricted_instances(request.user, self.se)
        for node in property_nodes:
            property_node_map[str(node.nodeid)] = {"node": node}
            if node.fieldname is None or node.fieldname == "":
                property_node_map[str(node.nodeid)]["name"] = slugify(node.name, max_length=field_name_length, separator="_")
            else:
                property_node_map[str(node.nodeid)]["name"] = node.fieldname
        tiles = models.TileModel.objects.filter(nodegroup__in=[node.nodegroup for node in nodes])
        last_page = None
        if resourceid is not None:
            tiles = tiles.filter(resourceinstance_id__in=resourceid.split(","))
        if tileid is not None:
            tiles = tiles.filter(tileid=tileid)
        tiles = tiles.order_by("sortorder")
        tiles = [tile for tile in tiles if str(tile.resourceinstance_id) not in restricted_resource_ids]
        if limit is not None:
            start = (page - 1) * limit
            end = start + limit
            last_page = len(tiles) < end
            tiles = tiles[start:end]
        for tile in tiles:
            data = tile.data
            for node in nodes:
                try:
                    for feature_index, feature in enumerate(data[str(node.pk)]["features"]):
                        if geometry_type is None or geometry_type == feature["geometry"]["type"]:
                            if len(nodegroups) > 0:
                                for pt in property_tiles.filter(resourceinstance_id=tile.resourceinstance_id).order_by("sortorder"):
                                    for key in pt.data:
                                        field_name = key if use_uuid_names else property_node_map[key]["name"]
                                        if pt.data[key] is not None:
                                            if use_display_values:
                                                property_node = property_node_map[key]["node"]
                                                datatype = datatype_factory.get_instance(property_node.datatype)
                                                value = datatype.get_display_value(pt, property_node)
                                            else:
                                                value = pt.data[key]
                                            try:
                                                feature["properties"][field_name].append(value)
                                            except KeyError:
                                                feature["properties"][field_name] = value
                                            except AttributeError:
                                                feature["properties"][field_name] = [feature["properties"][field_name], value]
                            if include_primary_name:
                                feature["properties"]["primary_name"] = self.get_name(tile.resourceinstance)
                            feature["properties"]["resourceinstanceid"] = tile.resourceinstance_id
                            feature["properties"]["tileid"] = tile.pk
                            if nodeid is None:
                                feature["properties"]["nodeid"] = node.pk
                            if include_geojson_link:
                                feature["properties"]["geojson"] = "%s?tileid=%s&nodeid=%s" % (reverse("geojson"), tile.pk, node.pk)
                            feature["id"] = i
                            if precision is not None:
                                coordinates = set_precision(feature["geometry"]["coordinates"], precision)
                                feature["geometry"]["coordinates"] = coordinates
                            i += 1
                            features.append(feature)
                except KeyError:
                    pass
                except TypeError:
                    pass

        feature_collection = {"type": "FeatureCollection", "features": features}
        if last_page is not None:
            feature_collection["_page"] = page
            feature_collection["_lastPage"] = last_page

        response = JSONResponse(feature_collection, indent=indent)
        return response


class MVT(APIBase):
    EARTHCIRCUM = 40075016.6856
    PIXELSPERTILE = 256

    def get(self, request, nodeid, zoom, x, y):
        if hasattr(request.user, "userprofile") is not True:
            models.UserProfile.objects.create(user=request.user)
        viewable_nodegroups = request.user.userprofile.viewable_nodegroups
        try:
            node = models.Node.objects.get(nodeid=nodeid, nodegroup_id__in=viewable_nodegroups)
        except models.Node.DoesNotExist:
            raise Http404()
        config = node.config
        cache_key = f"mvt_{nodeid}_{zoom}_{x}_{y}"
        tile = cache.get(cache_key)
        if tile is None:
            resource_ids = get_restricted_instances(request.user, allresources=True)
            if len(resource_ids) == 0:
                resource_ids.append("10000000-0000-0000-0000-000000000001")  # This must have a uuid that will never be a resource id.
            resource_ids = tuple(resource_ids)
            with connection.cursor() as cursor:
                if int(zoom) <= int(config["clusterMaxZoom"]):
                    arc = self.EARTHCIRCUM / ((1 << int(zoom)) * self.PIXELSPERTILE)
                    distance = arc * int(config["clusterDistance"])
                    min_points = int(config["clusterMinPoints"])
                    cursor.execute(
                        """WITH clusters(tileid, resourceinstanceid, nodeid, geom, cid)
                        AS (
                            SELECT m.*,
                            ST_ClusterDBSCAN(geom, eps := %s, minpoints := %s) over () AS cid
                            FROM (
                                SELECT tileid,
                                    resourceinstanceid,
                                    nodeid,
                                    geom
                                FROM mv_geojson_geoms
                                WHERE nodeid = %s and resourceinstanceid not in %s
                            ) m
                        )

                        SELECT ST_AsMVT(
                            tile,
                             %s,
                            4096,
                            'geom',
                            'id'
                        ) FROM (
                            SELECT resourceinstanceid::text,
                                row_number() over () as id,
                                1 as total,
                                ST_AsMVTGeom(
                                    geom,
                                    TileBBox(%s, %s, %s, 3857)
                                ) AS geom,
                                '' AS extent
                            FROM clusters
                            WHERE cid is NULL
                            UNION
                            SELECT NULL as resourceinstanceid,
                                row_number() over () as id,
                                count(*) as total,
                                ST_AsMVTGeom(
                                    ST_Centroid(
                                        ST_Collect(geom)
                                    ),
                                    TileBBox(%s, %s, %s, 3857)
                                ) AS geom,
                                ST_AsGeoJSON(
                                    ST_Extent(geom)
                                ) AS extent
                            FROM clusters
                            WHERE cid IS NOT NULL
                            GROUP BY cid
                        ) as tile;""",
                        [distance, min_points, nodeid, resource_ids, nodeid, zoom, x, y, zoom, x, y],
                    )
                else:
                    cursor.execute(
                        """SELECT ST_AsMVT(tile, %s, 4096, 'geom', 'id') FROM (SELECT tileid,
                            row_number() over () as id,
                            resourceinstanceid,
                            nodeid,
                            ST_AsMVTGeom(
                                geom,
                                TileBBox(%s, %s, %s, 3857)
                            ) AS geom,
                            1 AS total
                        FROM mv_geojson_geoms
                        WHERE nodeid = %s and resourceinstanceid not in %s) AS tile;""",
                        [nodeid, zoom, x, y, nodeid, resource_ids],
                    )
                tile = bytes(cursor.fetchone()[0])
                cache.set(cache_key, tile, settings.TILE_CACHE_TIMEOUT)
        if not len(tile):
            raise Http404()
        return HttpResponse(tile, content_type="application/x-protobuf")


@method_decorator(csrf_exempt, name="dispatch")
class Graphs(APIBase):
    def get(self, request, graph_id=None):
        perm = "read_nodegroup"
        datatypes = models.DDataType.objects.all()
        graph = cache.get(f"graph_{graph_id}")
        user = request.user
        if graph is None:
            graph = Graph.objects.get(graphid=graph_id)
        cards = CardProxyModel.objects.filter(graph_id=graph_id).order_by("sortorder")
        permitted_cards = []
        for card in cards:
            if user.has_perm(perm, card.nodegroup):
                card.filter_by_perm(user, perm)
                permitted_cards.append(card)
        cardwidgets = [
            widget for widgets in [card.cardxnodexwidget_set.order_by("sortorder").all() for card in permitted_cards] for widget in widgets
        ]
        graph = JSONSerializer().serializeToPython(graph, sort_keys=False, exclude=["is_editable", "functions"])
        permitted_cards = JSONSerializer().serializeToPython(permitted_cards, sort_keys=False, exclude=["is_editable"])
        return JSONResponse({"datatypes": datatypes, "cards": permitted_cards, "graph": graph, "cardwidgets": cardwidgets})


@method_decorator(csrf_exempt, name="dispatch")
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
        if not user_can_read_resource(user=request.user, resourceid=resourceid):
            return JSONResponse(status=403)

        allowed_formats = ["json", "json-ld", "arches-json"]
        format = request.GET.get("format", "json-ld")
        user = request.user
        perm = "read_nodegroup"

        if format not in allowed_formats:
            return JSONResponse(status=406, reason="incorrect format specified, only %s formats allowed" % allowed_formats)

        indent = request.GET.get("indent")
        if indent and str.isdigit(indent):
            indent = int(indent)
        else:
            indent = None

        if resourceid:
            if format == "json":
                resource = Resource.objects.get(pk=resourceid)

                compact = bool(request.GET.get("compact", "true").lower() == "true")  # default True
                hide_empty_nodes = bool(request.GET.get("hide_empty_nodes", "false").lower() == "true")  # default False

                out = {
                    "resource": resource.to_json(
                        compact=compact,
                        hide_empty_nodes=hide_empty_nodes,
                        user=user,
                        perm=perm,
                    ),
                    "displaydescription": resource.displaydescription,
                    "displayname": resource.displayname,
                    "graph_id": resource.graph_id,
                    "legacyid": resource.legacyid,
                    "map_popup": resource.map_popup,
                    "resourceinstanceid": resource.resourceinstanceid,
                }

            elif format == "arches-json":
                out = Resource.objects.get(pk=resourceid)

                include_tiles = bool(request.GET.get("includetiles", "true").lower() == "true")  # default True

                if include_tiles:
                    out.load_tiles(user, perm)

            elif format == "json-ld":
                try:
                    models.ResourceInstance.objects.get(pk=resourceid)  # check for existance
                    exporter = ResourceExporter(format=format)
                    output = exporter.writer.write_resources(resourceinstanceids=[resourceid], indent=indent, user=request.user)
                    out = output[0]["outputfile"].getvalue()
                except models.ResourceInstance.DoesNotExist:
                    logger.error(_("The specified resource '{0}' does not exist. JSON-LD export failed.".format(resourceid)))
                    return JSONResponse(status=404)

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
                page = int(request.GET.get("page", None))
            except Exception:
                page = 1

            start = (page - 1) * page_size
            end = start + page_size

            base_url = "%s%s" % (settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT, reverse("resources", args=[""]).lstrip("/"))
            out = {
                "@context": "https://www.w3.org/ns/ldp/",
                "@id": "",
                "@type": "ldp:BasicContainer",
                # Here we actually mean the name
                # "label": str(model.name),
                "ldp:contains": [
                    "%s%s" % (base_url, resourceid)
                    for resourceid in list(
                        Resource.objects.values_list("pk", flat=True)
                        .exclude(pk=settings.SYSTEM_SETTINGS_RESOURCE_ID)
                        .order_by("pk")[start:end]
                    )
                ],
            }

        return JSONResponse(out, indent=indent)

    # def put(self, request, resourceid):
    #     try:
    #         indent = int(request.POST.get('indent', None))
    #     except:
    #         indent = None

    #     try:
    #         if user_can_edit_resource(user=request.user):
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
            indent = int(request.PUT.get("indent", None))
        except Exception:
            indent = None

        if not user_can_edit_resource(user=request.user, resourceid=resourceid):
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
                            response.append(JSONDeserializer().deserialize(self.get(request, resource.resourceinstanceid).content))
                        return JSONResponse(response, indent=indent, status=201)
                except models.ResourceInstance.DoesNotExist:
                    return JSONResponse(status=404)
                except Exception as e:
                    return JSONResponse({"error": "resource data could not be saved"}, status=500, reason=e)

    def post(self, request, resourceid=None, slug=None, graphid=None):
        try:
            indent = int(request.POST.get("indent", None))
        except Exception:
            indent = None

        try:
            if user_can_edit_resource(user=request.user, resourceid=resourceid):
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
                        response.append(JSONDeserializer().deserialize(self.get(request, resource.resourceinstanceid).content))
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
        if user_can_edit_resource(user=request.user, resourceid=resourceid) and user_can_delete_resource(
            user=request.user, resourceid=resourceid
        ):
            try:
                resource_instance = Resource.objects.get(pk=resourceid)
                resource_instance.delete()
            except models.ResourceInstance.DoesNotExist:
                return JSONResponse(status=404)
        else:
            return JSONResponse(status=500)

        return JSONResponse(status=200)


@method_decorator(csrf_exempt, name="dispatch")
class Concepts(APIBase):
    def get(self, request, conceptid=None):
        if user_can_read_concepts(user=request.user):
            allowed_formats = ["json", "json-ld"]
            format = request.GET.get("format", "json-ld")
            if format not in allowed_formats:
                return JSONResponse(status=406, reason="incorrect format specified, only %s formats allowed" % allowed_formats)

            include_subconcepts = request.GET.get("includesubconcepts", "true") == "true"
            include_parentconcepts = request.GET.get("includeparentconcepts", "true") == "true"
            include_relatedconcepts = request.GET.get("includerelatedconcepts", "true") == "true"

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
                    return JSONResponse(status=404)
                except Exception as e:
                    return JSONResponse(status=500, reason=e)
            else:
                return JSONResponse(status=500)
        else:
            return JSONResponse(status=500)

        if format == "json-ld":
            try:
                skos = SKOSWriter()
                value = skos.write(ret, format="nt")
                js = from_rdf(value.decode("utf-8"), options={format: "application/nquads"})

                context = [{"@context": {"skos": SKOS, "dcterms": DCTERMS, "rdf": str(RDF)}}, {"@context": settings.RDM_JSONLD_CONTEXT}]

                ret = compact(js, context)
            except Exception as e:
                return JSONResponse(status=500, reason=e)

        return JSONResponse(ret, indent=indent)


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
                if request.user.has_perm("write_nodegroup", node.nodegroup):
                    editable_nodegroups.append(node.nodegroup)
                    nodegroups.append(node.nodegroup)
                    added = True
                if not added and request.user.has_perm("read_nodegroup", node.nodegroup):
                    nodegroups.append(node.nodegroup)

        nodes = nodes.filter(nodegroup__in=nodegroups)
        cards = graph.cardmodel_set.order_by("sortorder").filter(nodegroup__in=nodegroups).prefetch_related("cardxnodexwidget_set")
        cardwidgets = [
            widget for widgets in [card.cardxnodexwidget_set.order_by("sortorder").all() for card in cards] for widget in widgets
        ]
        datatypes = models.DDataType.objects.all()
        user_is_reviewer = user_is_resource_reviewer(request.user)
        widgets = models.Widget.objects.all()
        card_components = models.CardComponent.objects.all()

        if resource_instance is None:
            tiles = []
            displayname = _("New Resource")
        else:
            displayname = resource_instance.displayname
            if displayname == "undefined":
                displayname = _("Unnamed Resource")
            if str(resource_instance.graph_id) == settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID:
                displayname = _("System Settings")

            tiles = resource_instance.tilemodel_set.order_by("sortorder").filter(nodegroup__in=nodegroups)
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
                                tile.provisionaledits = {str(request.user.id): tile.provisionaledits[str(request.user.id)]}
                                tile.data = tile.provisionaledits[str(request.user.id)]["value"]
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
            card["is_writable"] = False
            if str(card["nodegroup_id"]) in editable_nodegroup_ids:
                card["is_writable"] = True

        context = {
            "resourceid": resourceid,
            "displayname": displayname,
            "tiles": tiles,
            "cards": cards,
            "nodegroups": nodegroups,
            "nodes": nodes,
            "cardwidgets": cardwidgets,
            "datatypes": datatypes,
            "userisreviewer": user_is_reviewer,
            "widgets": widgets,
            "card_components": card_components,
        }

        return JSONResponse(context, indent=4)


class SearchComponentData(APIBase):
    def get(self, request, componentname):
        search_filter_factory = SearchFilterFactory(request)
        search_filter = search_filter_factory.get_filter(componentname)
        if search_filter:
            return JSONResponse(search_filter.view_data())
        return JSONResponse(status=404)


@method_decorator(csrf_exempt, name="dispatch")
class Images(APIBase):
    # meant to handle uploading of full sized images from a mobile client
    def post(self, request):
        tileid = request.POST.get("tileid")
        fileid = request.POST.get("file_id")
        nodeid = request.POST.get("nodeid")
        file_name = request.POST.get("file_name", "temp.jpg")
        file_data = request.FILES.get("data")
        try:
            image_file, file_created = models.File.objects.get_or_create(pk=fileid)
            image_file.path.save(file_name, ContentFile(file_data.read()))

            tile = TileProxyModel.objects.get(pk=tileid)
            tile_data = tile.get_tile_data(request.user.pk)
            for image in tile_data[nodeid]:
                if image["file_id"] == fileid:
                    image["url"] = image_file.path.url
                    image["size"] = image_file.path.size
                    # I don't really want to run all the code TileProxyModel.save(),
                    # so I just call it's super class
                    super(TileProxyModel, tile).save()
                    tile.index()

            # to use base64 use the below code
            # import base64
            # with open("foo.jpg", "w+b") as f:
            #     f.write(base64.b64decode(request.POST.get('data')))

        except TileProxyModel.DoesNotExist:
            # it's ok if the TileProxyModel doesn't exist, that just means that there is some
            # latency in the updating of the db from couch
            # see process_mobile_data in the FileListDatatype for how image thumbnails get
            # pushed to the db and files saved
            pass
        except Exception as e:
            return JSONResponse(status=500)

        return JSONResponse()


class IIIFManifest(APIBase):
    def get(self, request):
        query = request.GET.get("query", None)
        start = int(request.GET.get("start", 0))
        limit = request.GET.get("limit", None)

        manifests = models.IIIFManifest.objects.all()
        if query is not None:
            manifests = manifests.filter(Q(label__icontains=query) | Q(description__icontains=query))
        count = manifests.count()
        if limit is not None:
            manifests = manifests[start : start + int(limit)]

        response = JSONResponse({"results": manifests, "count": count})
        return response


class OntologyProperty(APIBase):
    def get(self, request):
        domain_ontology_class = request.GET.get("domain_ontology_class", None)
        range_ontology_class = request.GET.get("range_ontology_class", None)
        ontologyid = request.GET.get("ontologyid", "sdl")

        ret = []
        if domain_ontology_class and range_ontology_class:
            ontology_classes = models.OntologyClass.objects.get(source=domain_ontology_class)
            for ontologyclass in ontology_classes.target["down"]:
                if range_ontology_class in ontologyclass["ontology_classes"]:
                    ret.append(ontologyclass["ontology_property"])

        return JSONResponse(ret)


@method_decorator(csrf_exempt, name="dispatch")
class Tile(APIBase):
    def get(self, request, tileid):
        try:
            tile = models.TileModel.objects.get(tileid=tileid)
        except Exception as e:
            return JSONResponse(str(e), status=404)

        # filter tiles from attribute query based on user permissions
        permitted_nodegroups = [str(nodegroup.pk) for nodegroup in get_nodegroups_by_perm(request.user, "models.read_nodegroup")]
        if str(tile.nodegroup_id) in permitted_nodegroups:
            return JSONResponse(tile, status=200)
        else:
            return JSONResponse(_("Tile not found."), status=404)

    def post(self, request, tileid):
        tileview = TileView()
        tileview.action = "update_tile"
        request.POST = request.POST.copy()
        request.POST["data"] = request.body
        return tileview.post(request)


@method_decorator(csrf_exempt, name="dispatch")
class Node(APIBase):
    def get(self, request, nodeid=None):
        graph_cache = {}
        params = request.GET.dict()
        user = request.user
        perms = "models." + params.pop("perms", "read_nodegroup")
        params["nodeid"] = params.get("nodeid", nodeid)
        try:
            uuid.UUID(params["nodeid"])
        except ValueError as e:
            del params["nodeid"]
        # parse node attributes from params
        # datatype = params.get("datatype")
        # description=params.get('description')
        # exportable=params.get('exportable')
        # fieldname=params.get('fieldname')
        # graph_id=params.get('graph_id')
        # is_collector=params.get('is_collector')
        # isrequired=params.get('isrequired')
        # issearchable=params.get('issearchable')
        # istopnode=params.get('istopnode')
        # name=params.get('name')
        # nodegroup_id=params.get('nodegroup_id')
        # nodeid=params.get('nodeid')
        # ontologyclass=params.get('ontologyclass')
        # sortorder=params.get('sortorder')

        def graphLookup(graphid):
            try:
                return graph_cache[graphid]
            except:
                graph_cache[graphid] = Graph.objects.get(pk=node["graph_id"]).name
                return graph_cache[graphid]

        # try to get nodes by attribute filter and then get nodes by passed in user perms
        try:
            nodes = models.Node.objects.filter(**dict(params)).values()
            permitted_nodegroups = [str(nodegroup.pk) for nodegroup in get_nodegroups_by_perm(user, perms)]
        except Exception as e:
            return JSONResponse(str(e), status=404)

        # check if any nodes were returned from attribute filter and throw error if none were returned
        if len(nodes) == 0:
            return JSONResponse(_("No nodes matching query parameters found."), status=404)

        # filter nodes from attribute query based on user permissions
        permitted_nodes = [node for node in nodes if str(node["nodegroup_id"]) in permitted_nodegroups]
        for node in permitted_nodes:
            try:
                node["resourcemodelname"] = graphLookup(node["graph_id"])
            except:
                return JSONResponse(_("No graph found for graphid %s" % (node["graph_id"])), status=404)

        return JSONResponse(permitted_nodes, status=200)


@method_decorator(csrf_exempt, name="dispatch")
class InstancePermission(APIBase):
    def get(self, request):
        user = request.user
        result = {}
        resourceinstanceid = request.GET.get("resourceinstanceid")
        result["read"] = user_can_read_resource(user, resourceinstanceid)
        result["edit"] = user_can_edit_resource(user, resourceinstanceid)
        result["delete"] = user_can_delete_resource(user, resourceinstanceid)
        return JSONResponse(result)


@method_decorator(csrf_exempt, name="dispatch")
class NodeValue(APIBase):
    def post(self, request):
        datatype_factory = DataTypeFactory()
        tileid = request.POST.get("tileid")
        nodeid = request.POST.get("nodeid")
        data = request.POST.get("data")
        resourceid = request.POST.get("resourceinstanceid", None)
        format = request.POST.get("format")
        operation = request.POST.get("operation")

        # get node model return error if not found
        try:
            node = models.Node.objects.get(nodeid=nodeid)
        except Exception as e:
            return JSONResponse(e, status=404)

        # check if user has permissions to write to node
        user_has_perms = request.user.has_perm("write_nodegroup", node)

        if user_has_perms:
            # get datatype of node
            try:
                datatype = datatype_factory.get_instance(node.datatype)
            except Exception as e:
                return JSONResponse(e, status=404)

            # transform data to format expected by tile
            data = datatype.transform_value_for_tile(data, format=format)

            # get existing data and append new data if operation='append'
            if operation == "append":
                tile = models.TileModel.objects.get(tileid=tileid)
                data = datatype.update(tile, data, nodeid, action=operation)

            # update/create tile
            new_tile = TileProxyModel.update_node_value(nodeid, data, tileid, resourceinstanceid=resourceid)

            response = JSONResponse(new_tile, status=200)
        else:
            response = JSONResponse(_("User does not have permission to edit this node."), status=403)

        return response
