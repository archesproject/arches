import json
import logging
import os
import sys
import uuid
import traceback
from base64 import b64decode
from http import HTTPStatus
from pyld.jsonld import compact, from_rdf
from rdflib import RDF
from rdflib.namespace import SKOS, DCTERMS
from revproxy.views import ProxyView
from slugify import slugify
from collections import OrderedDict
from django.contrib.auth import authenticate
from django.views.generic import View
from django.db import transaction, connection
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.core.cache import cache
from django.forms.models import model_to_dict
from django.urls import reverse
from django.utils.translation import get_language, gettext as _
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from arches.app.models import models
from arches.app.models.concept import Concept
from arches.app.models.card import Card as CardProxyModel
from arches.app.models.graph import Graph
from arches.app.models.resource import Resource
from arches.app.models.system_settings import settings
from arches.app.models.tile import Tile as TileProxyModel, TileValidationError
from arches.app.utils.mvt_tiler import MVTTiler
from arches.app.views.tile import TileData as TileView
from arches.app.views.resource import (
    RelatedResourcesView,
    get_resource_relationship_types,
)
from arches.app.utils.skos import SKOSWriter
from arches.app.utils.response import JSONResponse, JSONErrorResponse
from arches.app.utils.decorators import group_required
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.data_management.resources.exporter import ResourceExporter
from arches.app.utils.data_management.resources.formats.rdffile import JsonLdReader
from arches.app.utils.data_management.resources.formats.archesfile import (
    ArchesFileReader,
)
from arches.app.utils.permission_backend import (
    user_can_read_resource,
    user_can_edit_resource,
    user_can_delete_resource,
    user_can_read_concepts,
    user_is_resource_reviewer,
    get_filtered_instances,
    get_nodegroups_by_perm,
)
from arches.app.utils.geo_utils import GeoUtils
from arches.app.utils.permission_backend import user_is_resource_editor
from arches.app.search.components.base import SearchFilterFactory
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.settings_utils import list_arches_app_paths

logger = logging.getLogger(__name__)


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


class API404(View):
    def dispatch(self, request, *args, **kwargs):
        return JSONErrorResponse(
            _("Request failed"), _("Route not found"), status=HTTPStatus.NOT_FOUND
        )


class GetFrontendI18NData(APIBase):
    def get(self, request):
        user_language = get_language()

        language_file_path = []

        language_file_path.append(
            os.path.join(settings.ROOT_DIR, "locale", user_language + ".json")
        )

        for arches_app_path in list_arches_app_paths():
            language_file_path.append(
                os.path.join(arches_app_path, "locale", user_language + ".json")
            )

        language_file_path.append(
            os.path.join(settings.APP_ROOT, "locale", user_language + ".json")
        )

        localized_strings = {}
        for lang_file in language_file_path:
            try:
                localized_strings = (
                    json.load(open(lang_file))[user_language] | localized_strings
                )
            except FileNotFoundError:
                pass

        return JSONResponse(
            {
                "enabled_languages": {
                    language_tuple[0]: str(language_tuple[1])
                    for language_tuple in settings.LANGUAGES
                },
                "translations": {user_language: localized_strings},
                "language": user_language,
            }
        )


class GeoJSON(APIBase):
    se = SearchEngineFactory().create()

    def get_name(self, resource):
        graph_function = models.FunctionXGraph.objects.filter(
            graph_id=resource.graph_id, function__functiontype="primarydescriptors"
        ).select_related("function")
        if len(graph_function) == 1:
            module = graph_function[0].function.get_class_module()()
            return module.get_primary_descriptor_from_nodes(
                self,
                graph_function[0].config["descriptor_types"]["name"],
                descriptor="name",
            )
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
        nodes = models.Node.objects.filter(
            datatype="geojson-feature-collection", nodegroup_id__in=viewable_nodegroups
        )
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
        property_nodes = models.Node.objects.filter(
            nodegroup_id__in=nodegroups
        ).order_by("sortorder")
        exclusive_set, filtered_instance_ids = get_filtered_instances(
            request.user, self.se, resources=resourceid.split(",")
        )
        for node in property_nodes:
            property_node_map[str(node.nodeid)] = {"node": node}
            if node.fieldname is None or node.fieldname == "":
                property_node_map[str(node.nodeid)]["name"] = slugify(
                    node.name, max_length=field_name_length, separator="_"
                )
            else:
                property_node_map[str(node.nodeid)]["name"] = node.fieldname
        tiles = models.TileModel.objects.filter(
            nodegroup__in=[node.nodegroup for node in nodes]
        )
        last_page = None
        if resourceid is not None:
            tiles = tiles.filter(resourceinstance_id__in=resourceid.split(","))
        if tileid is not None:
            tiles = tiles.filter(tileid=tileid)
        tiles = tiles.order_by("sortorder")
        resource_available = str(tile.resourceinstance_id) not in filtered_instance_ids
        resource_available = (
            not (resource_available) if exclusive_set else resource_available
        )
        tiles = [tile for tile in tiles if resource_available]
        if limit is not None:
            start = (page - 1) * limit
            end = start + limit
            last_page = len(tiles) < end
            tiles = tiles[start:end]
        for tile in tiles:
            data = tile.data
            for node in nodes:
                try:
                    for feature_index, feature in enumerate(
                        data[str(node.pk)]["features"]
                    ):
                        if (
                            geometry_type is None
                            or geometry_type == feature["geometry"]["type"]
                        ):
                            if len(nodegroups) > 0:
                                for pt in property_tiles.filter(
                                    resourceinstance_id=tile.resourceinstance_id
                                ).order_by("sortorder"):
                                    for key in pt.data:
                                        field_name = (
                                            key
                                            if use_uuid_names
                                            else property_node_map[key]["name"]
                                        )
                                        if pt.data[key] is not None:
                                            if use_display_values:
                                                property_node = property_node_map[key][
                                                    "node"
                                                ]
                                                datatype = (
                                                    datatype_factory.get_instance(
                                                        property_node.datatype
                                                    )
                                                )
                                                value = datatype.get_display_value(
                                                    pt, property_node
                                                )
                                            else:
                                                value = pt.data[key]
                                            try:
                                                feature["properties"][
                                                    field_name
                                                ].append(value)
                                            except KeyError:
                                                feature["properties"][
                                                    field_name
                                                ] = value
                                            except AttributeError:
                                                feature["properties"][field_name] = [
                                                    feature["properties"][field_name],
                                                    value,
                                                ]
                            if include_primary_name:
                                feature["properties"]["primary_name"] = self.get_name(
                                    tile.resourceinstance
                                )
                            feature["properties"][
                                "resourceinstanceid"
                            ] = tile.resourceinstance_id
                            feature["properties"]["tileid"] = tile.pk
                            try:
                                feature["properties"].pop("nodeId")
                            except KeyError:
                                pass
                            feature["properties"]["nodeid"] = node.pk
                            if include_geojson_link:
                                feature["properties"]["geojson"] = (
                                    "%s?tileid=%s&nodeid=%s"
                                    % (
                                        reverse("geojson"),
                                        tile.pk,
                                        node.pk,
                                    )
                                )
                            feature["id"] = i
                            if precision is not None:
                                coordinates = set_precision(
                                    feature["geometry"]["coordinates"], precision
                                )
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
    def get(self, request, nodeid, zoom, x, y):
        if hasattr(request.user, "userprofile") is not True:
            models.UserProfile.objects.create(user=request.user)
        viewable_nodegroups = request.user.userprofile.viewable_nodegroups
        user = request.user

        tile = MVTTiler().createTile(nodeid, viewable_nodegroups, user, zoom, x, y)
        if not tile or not len(tile):
            raise Http404()
        return HttpResponse(tile, content_type="application/x-protobuf")


@method_decorator(csrf_exempt, name="dispatch")
class Graphs(APIBase):
    action = None

    def get(self, request, graph_id=None):
        cards_querystring = request.GET.get("cards", None)
        exclusions_querystring = request.GET.get("exclude", None)
        if cards_querystring == "false":
            get_cards = False
        else:
            get_cards = True

        if exclusions_querystring is not None:
            exclusions = list(map(str.strip, exclusions_querystring.split(",")))
        else:
            exclusions = []

        perm = "read_nodegroup"
        user = request.user
        if graph_id and not self.action:
            graph = Graph.objects.get(graphid=graph_id)
            graph = JSONSerializer().serializeToPython(
                graph,
                sort_keys=False,
                exclude=["is_editable", "functions"] + exclusions,
            )

            if get_cards:
                datatypes = models.DDataType.objects.all()
                cards = CardProxyModel.objects.filter(graph_id=graph_id).order_by(
                    "sortorder"
                )
                permitted_cards = []
                for card in cards:
                    if user.has_perm(perm, card.nodegroup):
                        card.filter_by_perm(user, perm)
                        permitted_cards.append(card)
                cardwidgets = [
                    widget
                    for widgets in [
                        card.cardxnodexwidget_set.order_by("sortorder").all()
                        for card in permitted_cards
                    ]
                    for widget in widgets
                ]

                permitted_cards = JSONSerializer().serializeToPython(
                    permitted_cards, sort_keys=False, exclude=["is_editable"]
                )

                return JSONResponse(
                    {
                        "datatypes": datatypes,
                        "cards": permitted_cards,
                        "graph": graph,
                        "cardwidgets": cardwidgets,
                    }
                )
            else:
                return JSONResponse({"graph": graph})
        elif self.action == "get_graph_models":
            graphs = models.GraphModel.objects.all()
            return JSONResponse(JSONSerializer().serializeToPython(graphs))


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
        hide_hidden_nodes = bool(request.GET.get("hidden", "true").lower() == "false")
        user = request.user
        perm = "read_nodegroup"

        if format not in allowed_formats:
            return JSONResponse(
                status=406,
                reason="incorrect format specified, only %s formats allowed"
                % allowed_formats,
            )

        indent = request.GET.get("indent")
        if indent and str.isdigit(indent):
            indent = int(indent)
        else:
            indent = None

        if resourceid:
            if format == "json":
                resource = Resource.objects.get(pk=resourceid)

                version = request.GET.get("v", None)
                compact = bool(
                    request.GET.get("compact", "true").lower() == "true"
                )  # default True
                hide_empty_nodes = bool(
                    request.GET.get("hide_empty_nodes", "false").lower() == "true"
                )  # default False

                if version == "beta":
                    out = resource.to_json(
                        compact=compact,
                        hide_empty_nodes=hide_empty_nodes,
                        user=user,
                        perm=perm,
                        version=version,
                        hide_hidden_nodes=hide_hidden_nodes,
                    )
                else:
                    out = {
                        "resource": resource.to_json(
                            compact=compact,
                            hide_empty_nodes=hide_empty_nodes,
                            user=user,
                            perm=perm,
                            version=version,
                            hide_hidden_nodes=hide_hidden_nodes,
                        ),
                        "displaydescription": resource.displaydescription(),
                        "displayname": resource.displayname(),
                        "graph_id": resource.graph_id,
                        "legacyid": resource.legacyid,
                        "map_popup": resource.map_popup(),
                        "resourceinstanceid": resource.resourceinstanceid,
                    }

            elif format == "arches-json":
                out = Resource.objects.get(pk=resourceid)

                include_tiles = bool(
                    request.GET.get("includetiles", "true").lower() == "true"
                )  # default True

                if include_tiles:
                    out.load_tiles(user, perm)

            elif format == "json-ld":
                try:
                    resource = models.ResourceInstance.objects.select_related(
                        "graph"
                    ).get(pk=resourceid)
                    if not resource.graph.ontology_id:
                        return JSONErrorResponse(
                            message=_(
                                "The graph '{0}' does not have an ontology. JSON-LD requires one."
                            ).format(resource.graph.name),
                            status=400,
                        )
                    exporter = ResourceExporter(format=format)
                    output = exporter.writer.write_resources(
                        resourceinstanceids=[resourceid],
                        indent=indent,
                        user=request.user,
                    )
                    out = output[0]["outputfile"].getvalue()
                except models.ResourceInstance.DoesNotExist:
                    logger.error(
                        _(
                            "The specified resource '{0}' does not exist. JSON-LD export failed."
                        ).format(resourceid)
                    )
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

            base_url = "%s%s" % (
                settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT,
                reverse("resources", args=[""]).lstrip("/"),
            )
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

    def put(self, request, resourceid, slug=None, graphid=None):
        allowed_formats = ["arches-json", "json-ld"]
        indent = request.GET.get("indent", None)
        format = request.GET.get("format", "json-ld")

        if format not in allowed_formats:
            return JSONResponse(
                status=406,
                reason="incorrect format specified, only %s formats allowed"
                % allowed_formats,
            )

        if format == "json-ld" and slug is None and graphid is None:
            return JSONResponse(
                {
                    "error": "Need to supply either a graph id or slug in the request url.  See the API reference in the developer documentation at https://arches.readthedocs.io for more details"
                },
                status=400,
            )

        if not user_can_edit_resource(user=request.user, resourceid=resourceid):
            return JSONResponse(status=403)
        else:
            with transaction.atomic():
                try:
                    if format == "json-ld":
                        data = JSONDeserializer().deserialize(request.body)
                        reader = JsonLdReader()
                        if slug is not None:
                            graphid = models.GraphModel.objects.get(slug=slug).pk
                        reader.read_resource(
                            data, resourceid=resourceid, graphid=graphid
                        )
                        if reader.errors:
                            response = []
                            for value in reader.errors.values():
                                response.append(value.message)
                            return JSONResponse(
                                {"error": response}, indent=indent, status=400
                            )
                        else:
                            response = []
                            for resource in reader.resources:
                                with transaction.atomic():
                                    try:
                                        # DELETE
                                        resource_instance = Resource.objects.get(
                                            pk=resource.pk
                                        )
                                        resource_instance.delete()
                                    except models.ResourceInstance.DoesNotExist:
                                        pass
                                    resource.save(request=request)
                                response.append(
                                    JSONDeserializer().deserialize(
                                        self.get(
                                            request, resource.resourceinstanceid
                                        ).content
                                    )
                                )
                            return JSONResponse(response, indent=indent, status=201)

                    elif format == "arches-json":
                        reader = ArchesFileReader()
                        archesresource = JSONDeserializer().deserialize(request.body)

                        # IF a resource id is supplied in the url it should match the resource ids in the body of the request.
                        if resourceid != archesresource["resourceinstanceid"]:
                            return JSONResponse(
                                {
                                    "error": "Resource id in the URI does not match the resourceinstanceid supplied in the document"
                                },
                                indent=indent,
                                status=400,
                            )

                        #  Resource id's in the request body take precedence over the id supplied in the url.
                        resource = {
                            "resourceinstance": {
                                "graph_id": archesresource["graph_id"],
                                "resourceinstanceid": archesresource[
                                    "resourceinstanceid"
                                ],
                                "legacyid": archesresource["legacyid"],
                            },
                            "tiles": archesresource["tiles"],
                        }

                        reader.import_business_data({"resources": [resource]})

                        if reader.errors:
                            response = []
                            for value in reader.errors.values():
                                response.append(value.message)
                            return JSONResponse(
                                {"error": response}, indent=indent, status=400
                            )
                        else:
                            response = []
                            response.append(
                                JSONDeserializer().deserialize(
                                    self.get(
                                        request, archesresource["resourceinstanceid"]
                                    ).content
                                )
                            )
                            return JSONResponse(response, indent=indent, status=201)

                except models.ResourceInstance.DoesNotExist:
                    return JSONResponse(status=404)
                except Exception as e:
                    return JSONResponse(
                        {"error": "resource data could not be saved"},
                        status=500,
                        reason=e,
                    )

    def post(self, request, resourceid=None, slug=None, graphid=None):
        allowed_formats = ["arches-json", "json-ld"]
        indent = request.POST.get("indent", None)
        format = request.GET.get("format", "json-ld")

        if format not in allowed_formats:
            return JSONResponse(
                status=406,
                reason="incorrect format specified, only %s formats allowed"
                % allowed_formats,
            )

        if format == "json-ld" and slug is None and graphid is None:
            return JSONResponse(
                {
                    "error": "Need to supply either a graph id or slug in the request url.  See the API reference in the developer documentation at https://arches.readthedocs.io for more details"
                },
                status=400,
            )

        try:
            if user_can_edit_resource(user=request.user, resourceid=resourceid):
                if format == "json-ld":
                    data = JSONDeserializer().deserialize(request.body)
                    reader = JsonLdReader()
                    if slug is not None:
                        graphid = models.GraphModel.objects.get(slug=slug).pk
                    reader.read_resource(data, graphid=graphid)
                    if reader.errors:
                        response = []
                        for value in reader.errors.values():
                            response.append(value.message)
                        return JSONResponse(
                            {"error": response}, indent=indent, status=400
                        )
                    else:
                        response = []
                        for resource in reader.resources:
                            with transaction.atomic():
                                resource.save(request=request)
                            response.append(
                                JSONDeserializer().deserialize(
                                    self.get(
                                        request, resource.resourceinstanceid
                                    ).content
                                )
                            )
                        return JSONResponse(response, indent=indent, status=201)

                elif format == "arches-json":
                    reader = ArchesFileReader()
                    archesresource = JSONDeserializer().deserialize(request.body)

                    nascent_resourceinstanceid = str(uuid.uuid4())

                    resource = {
                        "resourceinstance": {
                            "graph_id": archesresource["graph_id"],
                            "resourceinstanceid": nascent_resourceinstanceid,
                            "legacyid": archesresource["legacyid"],
                        },
                        "tiles": archesresource["tiles"],
                    }

                    reader.import_business_data({"resources": [resource]})

                    if reader.errors:
                        response = []
                        for value in reader.errors.values():
                            response.append(value.message)
                        return JSONResponse(
                            {"error": response}, indent=indent, status=400
                        )
                    else:
                        response = []
                        response.append(
                            JSONDeserializer().deserialize(
                                self.get(request, nascent_resourceinstanceid).content
                            )
                        )
                        return JSONResponse(response, indent=indent, status=201)

            else:
                return JSONResponse(status=403)
        except Exception as e:
            if settings.DEBUG is True:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                formatted = traceback.format_exception(
                    exc_type, exc_value, exc_traceback
                )
                if len(formatted):
                    for message in formatted:
                        print(message)
            return JSONResponse(
                {"error": "resource data could not be saved: %s" % e},
                status=500,
                reason=e,
            )

    def delete(self, request, resourceid, slug=None, graphid=None):
        if user_can_edit_resource(
            user=request.user, resourceid=resourceid
        ) and user_can_delete_resource(user=request.user, resourceid=resourceid):
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
                return JSONResponse(
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
                js = from_rdf(
                    value.decode("utf-8"), options={format: "application/nquads"}
                )

                context = [
                    {"@context": {"skos": SKOS, "dcterms": DCTERMS, "rdf": str(RDF)}},
                    {"@context": settings.RDM_JSONLD_CONTEXT},
                ]

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

        nodegroups = []
        editable_nodegroups = []
        nodes = graph.node_set.all().select_related("nodegroup")
        for node in nodes:
            if node.is_collector:
                added = False
                if request.user.has_perm("write_nodegroup", node.nodegroup):
                    editable_nodegroups.append(node.nodegroup)
                    nodegroups.append(node.nodegroup)
                    added = True
                if not added and request.user.has_perm(
                    "read_nodegroup", node.nodegroup
                ):
                    nodegroups.append(node.nodegroup)

        user_is_reviewer = user_is_resource_reviewer(request.user)

        if resource_instance is None:
            tiles = []
            displayname = _("New Resource")
        else:
            displayname = resource_instance.displayname()
            if displayname == "undefined":
                displayname = _("Unnamed Resource")
            if (
                str(resource_instance.graph_id)
                == settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID
            ):
                displayname = _("System Settings")

            tiles = resource_instance.tilemodel_set.order_by("sortorder").filter(
                nodegroup__in=nodegroups
            )
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
                                    str(request.user.id): tile.provisionaledits[
                                        str(request.user.id)
                                    ]
                                }
                                tile.data = tile.provisionaledits[str(request.user.id)][
                                    "value"
                                ]
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

        serialized_graph = None
        if graph.publication:
            published_graph = graph.get_published_graph()
            serialized_graph = published_graph.serialized_graph

        if serialized_graph:
            serialized_cards = serialized_graph["cards"]
            cardwidgets = [
                widget
                for widget in models.CardXNodeXWidget.objects.filter(
                    pk__in=[
                        widget_dict["id"] for widget_dict in serialized_graph["widgets"]
                    ]
                )
            ]
        else:
            cards = (
                graph.cardmodel_set.order_by("sortorder")
                .filter(nodegroup__in=nodegroups)
                .prefetch_related("cardxnodexwidget_set")
            )
            serialized_cards = JSONSerializer().serializeToPython(cards)
            cardwidgets = [
                widget
                for widget in [
                    card.cardxnodexwidget_set.order_by("sortorder").all()
                    for card in cards
                ]
            ]

        editable_nodegroup_ids = [
            str(nodegroup.pk) for nodegroup in editable_nodegroups
        ]
        for card in serialized_cards:
            card["is_writable"] = False
            if str(card["nodegroup_id"]) in editable_nodegroup_ids:
                card["is_writable"] = True

        context = {
            "resourceid": resourceid,
            "displayname": displayname,
            "tiles": tiles,
            "cards": serialized_cards,
            "nodegroups": nodegroups,
            "nodes": nodes.filter(nodegroup__in=nodegroups),
            "cardwidgets": cardwidgets,
            "datatypes": models.DDataType.objects.all(),
            "userisreviewer": user_is_reviewer,
            "widgets": models.Widget.objects.all(),
            "card_components": models.CardComponent.objects.all(),
        }

        return JSONResponse(context, indent=4)


class Plugins(View):
    def get(self, request, plugin_id=None):
        if plugin_id:
            plugins = models.Plugin.objects.filter(pk=plugin_id)
        else:
            plugins = models.Plugin.objects.all()

        plugins = [
            plugin
            for plugin in plugins
            if self.request.user.has_perm("view_plugin", plugin)
        ]

        return JSONResponse(plugins)


class SearchExport(View):
    @method_decorator(
        ratelimit(
            key="header:http-authorization", rate=settings.RATE_LIMIT, block=False
        )
    )
    def get(self, request):
        from arches.app.search.search_export import (
            SearchResultsExporter,
        )  # avoids circular import

        total = int(request.GET.get("total", 0))
        download_limit = settings.SEARCH_EXPORT_IMMEDIATE_DOWNLOAD_THRESHOLD
        format = request.GET.get("format", "tilecsv")
        report_link = request.GET.get("reportlink", False)
        if "HTTP_AUTHORIZATION" in request.META and not request.GET.get(
            "limited", False
        ):
            request_auth = request.META.get("HTTP_AUTHORIZATION").split()
            if request_auth[0].lower() == "basic":
                user_cred = b64decode(request_auth[1]).decode().split(":")
                user = authenticate(username=user_cred[0], password=user_cred[1])
                if user is not None:
                    request.user = user
                else:
                    return JSONErrorResponse(status=HTTPStatus.UNAUTHORIZED)
        exporter = SearchResultsExporter(search_request=request)
        export_files, export_info = exporter.export(format, report_link)
        if format == "geojson" and total <= download_limit:
            if settings.EXPORT_DATA_FIELDS_IN_CARD_ORDER:
                response = JSONResponse(export_files, sort_keys=False)
            else:
                response = JSONResponse(export_files)
            return response
        return JSONResponse(status=404)


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

        except Exception as e:
            return JSONResponse(status=500)

        return JSONResponse()


class IIIFManifest(APIBase):
    def get(self, request):
        query = request.GET.get("query", None)
        start = int(request.GET.get("start", 0))
        limit = request.GET.get("limit", None)
        more = False

        manifests = models.IIIFManifest.objects.all()
        if query is not None:
            manifests = manifests.filter(
                Q(label__icontains=query) | Q(description__icontains=query)
            )
        count = manifests.count()
        if limit is not None:
            manifests = manifests[start : start + int(limit)]
            more = start + int(limit) < count

        response = JSONResponse({"results": manifests, "count": count, "more": more})
        return response


class IIIFAnnotations(APIBase):
    def get(self, request):
        canvas = request.GET.get("canvas", None)
        resourceid = request.GET.get("resourceid", None)
        nodeid = request.GET.get("nodeid", None)
        permitted_nodegroups = get_nodegroups_by_perm(
            request.user, "models.read_nodegroup"
        )
        annotations = models.VwAnnotation.objects.filter(
            nodegroup__in=permitted_nodegroups
        )
        if canvas is not None:
            annotations = annotations.filter(canvas=canvas)
        if resourceid is not None:
            annotations = annotations.filter(resourceinstance_id=resourceid)
        if nodeid is not None:
            annotations = annotations.filter(node_id=nodeid)
        return JSONResponse(
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "id": annotation.feature["id"],
                        "geometry": annotation.feature["geometry"],
                        "properties": {
                            **annotation.feature["properties"],
                            **{
                                "nodeId": annotation.node_id,
                                "nodegroupId": annotation.nodegroup_id,
                                "resourceId": annotation.resourceinstance_id,
                                "graphId": annotation.node.graph_id,
                                "tileId": annotation.tile_id,
                            },
                        },
                    }
                    for annotation in annotations
                ],
            }
        )


class IIIFAnnotationNodes(APIBase):
    def get(self, request, indent=None):
        permitted_nodegroups = get_nodegroups_by_perm(
            request.user, "models.read_nodegroup"
        )
        annotation_nodes = models.Node.objects.filter(
            nodegroup__in=permitted_nodegroups, datatype="annotation"
        )
        return JSONResponse(
            [
                {
                    **model_to_dict(node),
                    "graph_name": node.graph.name,
                    "icon": node.graph.iconclass,
                }
                for node in annotation_nodes
            ]
        )


class Manifest(APIBase):
    def get(self, request, id):
        try:
            uuid.UUID(id)
            manifest = models.IIIFManifest.objects.get(globalid=id).manifest
            return JSONResponse(manifest)
        except:
            manifest = models.IIIFManifest.objects.get(id=id).manifest
            return JSONResponse(manifest)


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


class ResourceReport(APIBase):
    def get(self, request, resourceid):
        exclude = request.GET.get("exclude", [])
        uncompacted_value = request.GET.get("uncompacted")
        version = request.GET.get("v")
        compact = True
        if uncompacted_value == "true":
            compact = False
        perm = "read_nodegroup"

        resource = Resource.objects.get(pk=resourceid)
        graph = Graph.objects.get(graphid=resource.graph_id)
        template = models.ReportTemplate.objects.get(pk=graph.template_id)

        if not template.preload_resource_data:
            return JSONResponse(
                {
                    "template": template,
                    "report_json": resource.to_json(
                        compact=compact, version=version, user=request.user, perm=perm
                    ),
                }
            )

        resp = {
            "datatypes": models.DDataType.objects.all(),
            "displayname": resource.displayname(),
            "resourceid": resourceid,
            "graph": graph,
            "hide_empty_nodes": settings.HIDE_EMPTY_NODES_IN_REPORT,
            "report_json": resource.to_json(compact=compact, version=version),
        }

        if "template" not in exclude:
            resp["template"] = template

        if "related_resources" not in exclude:
            resource_models = (
                models.GraphModel.objects.filter(isresource=True)
                .exclude(publication=None)
                .exclude(pk=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
            )

            get_params = request.GET.copy()
            get_params.update({"paginate": "false"})
            request.GET = get_params

            related_resources_response = RelatedResourcesView().get(
                request, resourceid, include_rr_count=False
            )
            related_resources = json.loads(related_resources_response.content)

            related_resources_summary = self._generate_related_resources_summary(
                related_resources=related_resources["related_resources"],
                resource_relationships=related_resources["resource_relationships"],
                resource_models=resource_models,
            )

            resp["related_resources"] = related_resources_summary

        if "tiles" not in exclude:
            resource.load_tiles(user=request.user, perm=perm)
            permitted_tiles = resource.tiles

            resp["tiles"] = permitted_tiles

        if "cards" not in exclude:
            # collect the nodegroups for which this user has perm
            readable_nodegroups = get_nodegroups_by_perm(
                request.user, [perm], any_perm=True
            )

            # query only the cards whose nodegroups are readable by user
            permitted_cards = (
                CardProxyModel.objects.filter(
                    graph_id=resource.graph_id, nodegroup__in=readable_nodegroups
                )
                .prefetch_related("cardxnodexwidget_set")
                .order_by("sortorder")
            )

            cardwidgets = [
                widget
                for widgets in [
                    sorted(
                        card.cardxnodexwidget_set.all(), key=lambda x: x.sortorder or 0
                    )
                    for card in permitted_cards
                ]
                for widget in widgets
            ]

            resp["cards"] = permitted_cards
            resp["cardwidgets"] = cardwidgets

        return JSONResponse(resp)

    def _generate_related_resources_summary(
        self, related_resources, resource_relationships, resource_models
    ):
        related_resource_summary = [
            {
                "graphid": str(resource_model.graphid),
                "name": resource_model.name,
                "resources": [],
            }
            for resource_model in resource_models
        ]

        resource_relationship_types = {
            resource_relationship_type["id"]: resource_relationship_type["text"]
            for resource_relationship_type in get_resource_relationship_types()[
                "values"
            ]
        }

        for related_resource in related_resources:
            for summary in related_resource_summary:
                if related_resource["graph_id"] == summary["graphid"]:
                    relationship_summary = []
                    for resource_relationship in resource_relationships:
                        if (
                            related_resource["resourceinstanceid"]
                            == resource_relationship["resourceinstanceidto"]
                        ):
                            rr_type = (
                                resource_relationship_types[
                                    resource_relationship["relationshiptype"]
                                ]
                                if resource_relationship["relationshiptype"]
                                in resource_relationship_types
                                else resource_relationship["relationshiptype"]
                            )
                            relationship_summary.append(rr_type)
                        elif (
                            related_resource["resourceinstanceid"]
                            == resource_relationship["resourceinstanceidfrom"]
                        ):
                            rr_type = (
                                resource_relationship_types[
                                    resource_relationship["inverserelationshiptype"]
                                ]
                                if resource_relationship["inverserelationshiptype"]
                                in resource_relationship_types
                                else resource_relationship["inverserelationshiptype"]
                            )
                            relationship_summary.append(rr_type)

                    summary["resources"].append(
                        {
                            "resourceinstanceid": related_resource[
                                "resourceinstanceid"
                            ],
                            "displayname": related_resource["displayname"],
                            "relationships": relationship_summary,
                        }
                    )

        return related_resource_summary


class BulkResourceReport(APIBase):
    def get(self, request):
        graph_ids = request.GET.get("graph_ids").split(",")
        exclude = request.GET.get("exclude", [])

        if not graph_ids:
            raise Exception()

        exclusions_querystring = request.GET.get("exclude", None)

        if exclusions_querystring is not None:
            exclusions = list(map(str.strip, exclude.split(",")))
        else:
            exclusions = []

        graph_ids_set = set(graph_ids)  # calls set to delete dups
        graph_ids_not_in_cache = []

        graph_lookup = {}

        for graph_id in graph_ids_set:
            graph = cache.get("serialized_graph_{}".format(graph_id))

            if graph:
                graph_lookup[graph["graphid"]] = graph
            else:
                graph_ids_not_in_cache.append(graph_id)

        if graph_ids_not_in_cache:
            graphs_from_database = list(
                Graph.objects.filter(pk__in=graph_ids_not_in_cache)
            )

            for graph in graphs_from_database:
                serialized_graph = JSONSerializer().serializeToPython(
                    graph,
                    sort_keys=False,
                    exclude=["is_editable", "functions"] + exclusions,
                )
                cache.set("serialized_graph_{}".format(graph.pk), serialized_graph)
                graph_lookup[str(graph.pk)] = serialized_graph

        graph_ids_with_templates_that_preload_resource_data = []
        graph_ids_with_templates_that_do_not_preload_resource_data = []

        for graph in graph_lookup.values():
            template = models.ReportTemplate.objects.get(pk=graph["template_id"])

            if template.preload_resource_data:
                graph_ids_with_templates_that_preload_resource_data.append(
                    graph["graphid"]
                )
            else:
                graph_ids_with_templates_that_do_not_preload_resource_data.append(
                    graph["graphid"]
                )

        permitted_cards = []

        if "cards" not in exclude:
            cards = (
                CardProxyModel.objects.filter(
                    graph_id__in=graph_ids_with_templates_that_preload_resource_data
                )
                .select_related("nodegroup")
                .order_by("sortorder")
            )

            perm = "read_nodegroup"
            permitted_cards = []

            for card in cards:
                if request.user.has_perm(perm, card.nodegroup):
                    card.filter_by_perm(request.user, perm)
                    permitted_cards.append(card)

        if "datatypes" not in exclude:
            datatypes = list(models.DDataType.objects.all())

        resp = {}

        for graph_id in graph_ids_with_templates_that_preload_resource_data:
            graph = graph_lookup[graph_id]

            graph_cards = [
                card
                for card in permitted_cards
                if str(card.graph_id) == graph["graphid"]
            ]

            cardwidgets = [
                widget
                for widgets in [
                    card.cardxnodexwidget_set.order_by("sortorder").all()
                    for card in graph_cards
                ]
                for widget in widgets
            ]

            resp[graph_id] = {
                "graph": graph,
                "cards": JSONSerializer().serializeToPython(
                    graph_cards, sort_keys=False, exclude=["is_editable"]
                ),
                "cardwidgets": cardwidgets,
            }

            if "datatypes" not in exclude:
                resp[graph_id]["datatypes"] = datatypes

        for graph_id in graph_ids_with_templates_that_do_not_preload_resource_data:
            graph = graph_lookup[graph_id]
            resp[graph_id] = {"template_id": graph["template_id"]}

        return JSONResponse(resp)


class BulkDisambiguatedResourceInstance(APIBase):
    def get(self, request):
        resource_ids = request.GET.get("resource_ids").split(",")
        version = request.GET.get("v")
        hide_hidden_nodes = bool(request.GET.get("hidden", "true").lower() == "false")
        compact = bool(request.GET.get("uncompacted", "false").lower() == "false")
        user = request.user
        perm = "read_nodegroup"

        disambiguated_resource_instances = OrderedDict().fromkeys(resource_ids)
        for resource in Resource.objects.filter(pk__in=resource_ids):
            disambiguated_resource_instances[str(resource.pk)] = resource.to_json(
                compact=compact,
                version=version,
                hide_hidden_nodes=hide_hidden_nodes,
                user=user,
                perm=perm,
            )

        return JSONResponse(disambiguated_resource_instances, sort_keys=False)


@method_decorator(csrf_exempt, name="dispatch")
class Tile(APIBase):
    def get(self, request, tileid):
        try:
            tile = models.TileModel.objects.get(tileid=tileid)
        except Exception as e:
            return JSONResponse(str(e), status=404)

        # filter tiles from attribute query based on user permissions
        permitted_nodegroups = get_nodegroups_by_perm(
            request.user, "models.read_nodegroup"
        )
        if tile.nodegroup_id in permitted_nodegroups:
            return JSONResponse(tile, status=200)
        else:
            return JSONResponse(_("Tile not found."), status=404)

    def post(self, request, tileid):
        tileview = TileView()
        tileview.action = "update_tile"
        # check that no data is on POST or FILES before assigning body to POST (otherwise request fails)
        if (
            len(dict(request.POST.items())) == 0
            and len(dict(request.FILES.items())) == 0
        ):
            request.POST = request.POST.copy()
            request.POST["data"] = request.body
        return tileview.post(request)


@method_decorator(csrf_exempt, name="dispatch")
class NodeGroup(APIBase):
    def get(self, request, nodegroupid=None):
        params = request.GET.dict()
        user = request.user
        perms = "models." + params.pop("perms", "read_nodegroup")
        params["nodegroupid"] = params.get("nodegroupid", nodegroupid)

        try:
            uuid.UUID(params["nodegroupid"])
        except ValueError as e:
            del params["nodegroupid"]

        try:
            nodegroup = models.NodeGroup.objects.get(pk=params["nodegroupid"])
            permitted_nodegroups = get_nodegroups_by_perm(user, perms)
        except Exception as e:
            return JSONResponse(str(e), status=404)

        if not nodegroup or nodegroup.pk not in permitted_nodegroups:
            return JSONResponse(
                _("No nodegroup matching query parameters found."), status=404
            )

        return JSONResponse(nodegroup, status=200)


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
            permitted_nodegroups = get_nodegroups_by_perm(user, perms)
        except Exception as e:
            return JSONResponse(str(e), status=404)

        # check if any nodes were returned from attribute filter and throw error if none were returned
        if len(nodes) == 0:
            return JSONResponse(
                _("No nodes matching query parameters found."), status=404
            )

        # filter nodes from attribute query based on user permissions
        permitted_nodes = [
            node for node in nodes if node["nodegroup_id"] in permitted_nodegroups
        ]
        for node in permitted_nodes:
            try:
                node["resourcemodelname"] = graphLookup(node["graph_id"])
            except:
                return JSONResponse(
                    _("No graph found for graphid %s" % (node["graph_id"])), status=404
                )

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
        transaction_id = request.POST.get("transaction_id")

        # get node model return error if not found
        try:
            node = models.Node.objects.get(nodeid=nodeid)
        except Exception as e:
            return JSONResponse(e, status=404)

        # check if user has permissions to write to node
        user_has_perms = request.user.has_perm("write_nodegroup", node.nodegroup)
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
            new_tile = TileProxyModel.update_node_value(
                nodeid,
                data,
                tileid,
                request=request,
                resourceinstanceid=resourceid,
                transaction_id=transaction_id,
            )

            response = JSONResponse(new_tile, status=200)
        else:
            response = JSONResponse(
                _("User does not have permission to edit this node."), status=403
            )

        return response


class UserIncompleteWorkflows(APIBase):
    def get(self, request):
        if not user_is_resource_editor(request.user):
            return JSONErrorResponse(
                _("Request Failed"), _("Permission Denied"), status=403
            )

        if request.user.is_superuser:
            incomplete_workflows = (
                models.WorkflowHistory.objects.filter(completed=False)
                .exclude(componentdata__iexact="{}")
                .order_by("created")
            )
        else:
            incomplete_workflows = (
                models.WorkflowHistory.objects.filter(
                    user=request.user, completed=False
                )
                .exclude(componentdata__iexact="{}")
                .order_by("created")
            )

        incomplete_workflows_user_ids = [
            incomplete_workflow.user_id for incomplete_workflow in incomplete_workflows
        ]

        incomplete_workflows_users = models.User.objects.filter(
            pk__in=set(incomplete_workflows_user_ids)
        )

        user_ids_to_usernames = {
            incomplete_workflows_user.pk: incomplete_workflows_user.username
            for incomplete_workflows_user in incomplete_workflows_users
        }

        plugins = models.Plugin.objects.all()

        workflow_slug_to_workflow_name = {
            plugin.componentname: plugin.name for plugin in plugins
        }

        incomplete_workflows_json = JSONDeserializer().deserialize(
            JSONSerializer().serialize(incomplete_workflows)
        )

        for incomplete_workflow in incomplete_workflows_json:
            incomplete_workflow["username"] = user_ids_to_usernames[
                incomplete_workflow["user_id"]
            ]
            incomplete_workflow["pluginname"] = workflow_slug_to_workflow_name[
                incomplete_workflow["workflowname"]
            ]

        return JSONResponse(
            {
                "incomplete_workflows": incomplete_workflows_json,
                "requesting_user_is_superuser": request.user.is_superuser,
            }
        )


@method_decorator(csrf_exempt, name="dispatch")
class Validator(APIBase):
    """
    Class for validating existing objects in the system using GET (resource instances, tiles, etc...)
    or for validating new objects using POST.

    arches-json format is assumed when posting a new resource instance for validation

    Querystring parameters:
    indent -- set to an integer value to format the json to be indented that number of characters
    verbose -- (default is False), set to True to return more information about the validation result
    strict -- (default is True), set to True to force the datatype to perform a more complete check
            (eg: check for the existance of a referenced resoure on the resource-instance datatype)
    """

    def validate_resource(self, resource, verbose, strict):
        errors = resource.validate(verbose=verbose, strict=strict)
        ret = {}

        ret["valid"] = len(errors) == 0
        if verbose:
            ret["errors"] = errors
        return ret

    def validate_tile(self, tile, verbose, strict):
        errors = []
        ret = {}

        try:
            tile.validate(raise_early=(not verbose), strict=strict)
        except TileValidationError as err:
            errors += err.message if isinstance(err.message, list) else [err.message]
        except BaseException as err:
            errors += [str(err)]

        ret["valid"] = len(errors) == 0
        if verbose:
            ret["errors"] = errors
        return ret

    def get(self, request, itemtype=None, itemid=None):
        valid_item_types = ["resource", "tile"]
        if itemtype not in valid_item_types:
            return JSONResponse(
                {
                    "message": f"items to validate can only be of the following types: {valid_item_types} -- eg: .../item_type/item_id"
                },
                status=400,
            )

        indent = request.GET.get("indent", None)
        verbose = (
            False if request.GET.get("verbose", "false").startswith("f") else True
        )  # default is False
        strict = (
            True if request.GET.get("strict", "true").startswith("t") else False
        )  # default is True

        if itemtype == "resource":
            try:
                resource = Resource.objects.get(pk=itemid)
            except:
                return JSONResponse(status=404)

            return JSONResponse(
                self.validate_resource(resource, verbose, strict), indent=indent
            )

        if itemtype == "tile":
            errors = []

            try:
                tile = TileProxyModel.objects.get(pk=itemid)
            except:
                return JSONResponse(status=404)

            return JSONResponse(
                self.validate_tile(tile, verbose, strict), indent=indent
            )

        return JSONResponse(status=400)

    def post(self, request, itemtype=None):
        valid_item_types = ["resource", "tile"]
        if itemtype not in valid_item_types:
            return JSONResponse(
                {
                    "message": f"items to validate can only be of the following types: {valid_item_types} -- eg: .../item_type/item_id"
                },
                status=400,
            )

        indent = request.GET.get("indent", None)
        verbose = (
            False if request.GET.get("verbose", "false").startswith("f") else True
        )  # default is False
        strict = (
            True if request.GET.get("strict", "true").startswith("t") else False
        )  # default is True
        data = JSONDeserializer().deserialize(request.body)

        if itemtype == "resource":
            resource = Resource()
            for tiledata in data["tiles"]:
                resource.tiles.append(TileProxyModel(tiledata))

            return JSONResponse(
                self.validate_resource(resource, verbose, strict), indent=indent
            )

        if itemtype == "tile":
            tile = TileProxyModel(data)
            return JSONResponse(
                self.validate_tile(tile, verbose, strict), indent=indent
            )

        return JSONResponse(status=400)


class TransformEdtfForTile(APIBase):
    def get(self, request):
        try:
            value = request.GET.get("value")
            datatype_factory = DataTypeFactory()
            edtf_datatype = datatype_factory.get_instance("edtf")
            transformed_value = edtf_datatype.transform_value_for_tile(value)
            is_valid = len(edtf_datatype.validate(transformed_value)) == 0
            result = (transformed_value, is_valid)

        except TypeError as e:
            return JSONResponse({"data": (str(e), False)})

        except Exception as e:
            return JSONResponse(str(e), status=500)

        return JSONResponse({"data": result})


class GetNodegroupTree(APIBase):
    """
    Returns the path to a nodegroup from the root node. Transforms node alias to node name.
    """

    def get(self, request):
        graphid = request.GET.get("graphid")
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT * FROM __get_nodegroup_tree_by_graph(%s)""", (graphid,)
            )
            result = cursor.fetchall()
            permitted_nodegroups = get_nodegroups_by_perm(
                request.user, "models.read_nodegroup"
            )
            permitted_result = [
                nodegroup
                for nodegroup in result
                if nodegroup[0] in permitted_nodegroups
            ]

        return JSONResponse({"path": permitted_result})


class SpatialView(APIBase):
    """ """

    def get(self, request, identifier=None):
        """
        Returns a permitted spatial view given an id
        otherwise returns a list of permitted spatial views
        """
        spatialview_id = None

        # ensure specific spatial view exists before proceeding
        if identifier:
            spatialview_id = identifier
            if not models.SpatialView.objects.filter(pk=identifier).exists():
                return JSONErrorResponse(
                    _("No Spatial View Exists with this id"), status=404
                )

        permitted_nodegroupids = get_nodegroups_by_perm(
            request.user, "models.read_nodegroup"
        )

        permitted_spatialviews = models.SpatialView.objects.filter(
            geometrynode__nodegroup_id__in=permitted_nodegroupids
        )

        if identifier:
            permitted_spatialviews = permitted_spatialviews.filter(pk=spatialview_id)
            if not len(permitted_spatialviews):
                return JSONErrorResponse(
                    _("Request Failed"), _("Permission Denied"), status=403
                )

        response_data = [
            spatialview.to_json() for spatialview in permitted_spatialviews
        ]

        # when using identifier, return a single object instead of a list
        if len(response_data) == 1 and identifier:
            response_data = response_data[0]

        return JSONResponse(response_data)

    def transform_json_data_for_spatialview(self, json_data):
        """
        Transforms the JSON data object to be used in the spatialview model
        """

        json_data["geometrynode_id"] = json_data.pop("geometrynodeid")
        json_data["language_id"] = json_data.pop("language")

        return json_data

    def create_spatialview_from_json_data(self, json_data):
        """
        Returns a SpatialView object from the JSON data. Should only be used if the JSON data has been validated.
        """

        json_data = self.transform_json_data_for_spatialview(json_data)

        try:
            spatialview = models.SpatialView.objects.get(pk=json_data["spatialviewid"])
        except KeyError:
            # if no spatialviewid is provided then is from POST so create a new spatialview object
            spatialview = models.SpatialView(**json_data)
            return spatialview
        except ObjectDoesNotExist:
            return JSONErrorResponse(
                _("Spatialview not found"),
                _("No Spatialview exists for the provided spatialviewid"),
                status=404,
            )

        # update the spatialview object with the new data
        for key, value in json_data.items():
            setattr(spatialview, key, value)

        return spatialview

    def validate_json_data_content(
        self, json_data, spatialviewid_identifier=None, is_post=False
    ):
        """
        Validates the JSON data passed in the request body where not handled by model validation.

        returns a JSONErrorResponse if validation fails or SpatialView if validation passes
        """

        if is_post and "spatialviewid" in json_data.keys():
            return JSONErrorResponse(
                _("Incorrect Spatialview json data"),
                _(
                    "POST REST request should not have a spatialviewid provided in the JSON data."
                ),
                status=400,
            )

        # Check if spatialviewid_identifier matches the spatialviewid in the json_data
        if spatialviewid_identifier:
            if "spatialviewid" in json_data:
                if spatialviewid_identifier != json_data["spatialviewid"]:
                    return JSONErrorResponse(
                        _("Incorrect Spatialview json data"),
                        _(
                            "Spatialviewid in the URL does not match the spatialviewid in the JSON data."
                        ),
                        status=400,
                    )
            else:
                return JSONErrorResponse(
                    _("Incorrect Spatialview json data"),
                    _("No spatialviewid provided in the JSON data."),
                    status=400,
                )

        # Check if geometrynodeid exists in the database before transforming the json data
        try:
            if not models.Node.objects.filter(pk=json_data["geometrynodeid"]).exists():
                return JSONErrorResponse(
                    _("Incorrect Spatialview json data"),
                    _("No geometrynode exists with the provided geometrynodeid."),
                    status=400,
                )

            # Check if language exists in the database before transforming the json data
            if not models.Language.objects.filter(code=json_data["language"]).exists():
                return JSONErrorResponse(
                    _("Incorrect Spatialview json data"),
                    _("No language exists with the provided language code."),
                    status=400,
                )
        except KeyError:
            return JSONErrorResponse(
                _("Incorrect Spatialview json data"),
                _("The JSON data provided is missing required fields."),
                status=400,
            )

        return self.create_spatialview_from_json_data(json_data)

    @method_decorator(group_required("Application Administrator", raise_exception=True))
    def post(self, request, identifier=None):

        # if identifier is not None then the user is trying to update a spatialview so an error should be returned with a message
        if identifier:
            return JSONErrorResponse(
                _("Spatialview creation failed"),
                _("POST request should not have a spatialviewid provided in the URL"),
                status=400,
            )

        try:
            json_data = JSONDeserializer().deserialize(request.body)
        except ValueError:
            return JSONErrorResponse(
                _("Invalid JSON data"),
                _("The Spatialview API was sent invalid JSON"),
                status=400,
            )

        if json_data is not None:

            validate_json_data_content_result = self.validate_json_data_content(
                json_data, is_post=True
            )
            if isinstance(validate_json_data_content_result, JSONErrorResponse):
                return validate_json_data_content_result

            spatialview = validate_json_data_content_result

            try:
                spatialview.full_clean()
                spatialview.save()
            except ValidationError as e:
                return JSONErrorResponse(
                    _("Validation Error when creating Spatialview"),
                    e.messages,
                    status=400,
                )

            return JSONResponse(spatialview.to_json(), status=201)
        return JSONErrorResponse(_("No json request payload"), status=400)

    @method_decorator(group_required("Application Administrator", raise_exception=True))
    def put(self, request, identifier=None):

        if not identifier:
            return JSONErrorResponse(
                _("Spatialview update failed"),
                _(
                    "PUT REST request requires a spatialviewid to be provided in the URL"
                ),
                status=400,
            )

        try:
            json_data = JSONDeserializer().deserialize(request.body)
        except ValueError:
            return JSONErrorResponse(
                _("Invalid JSON data"),
                _("The Spatialview API was sent invalid JSON"),
                status=400,
            )

        if json_data is not None:

            validate_json_data_content_result = self.validate_json_data_content(
                json_data, identifier
            )
            if isinstance(validate_json_data_content_result, JSONErrorResponse):
                return validate_json_data_content_result

            spatialview = validate_json_data_content_result

            try:
                spatialview.full_clean()
                spatialview.save()
            except ValidationError as e:
                return JSONErrorResponse(
                    _("Validation Error when updating Spatialview"),
                    e.messages,
                    status=400,
                )

            return JSONResponse(spatialview.to_json(), status=200)
        return JSONErrorResponse(
            _("Spatialview update failed"), _("No json request payload"), status=400
        )

    @method_decorator(group_required("Application Administrator", raise_exception=True))
    def delete(self, request, identifier=None):
        if identifier:
            spatialview = None
            try:
                spatialview = models.SpatialView.objects.get(pk=identifier)
            except ObjectDoesNotExist:
                return JSONErrorResponse(
                    _("Spatialview delete failed"),
                    _("Spatialview does not exist"),
                    status=404,
                )

            try:
                spatialview.delete()
            except Exception as e:
                logger.error(e)
                return JSONErrorResponse(
                    _("Spatialview delete failed"),
                    _("An error occurred when trying to delete the spatialview"),
                    status=500,
                )

        else:
            return JSONErrorResponse(
                _("Spatialview delete failed"),
                _(
                    "DELETE REST request requires a spatialviewid to be provided in the URL"
                ),
                status=400,
            )
        return JSONResponse(status=204)
