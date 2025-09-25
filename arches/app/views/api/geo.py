from django.http import Http404, HttpResponse
from django.urls import reverse
from django.utils.translation import gettext as _
from slugify import slugify

from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models import models
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.utils.geo_utils import GeoUtils
from arches.app.utils.mvt_tiler import MVTTiler
from arches.app.utils.permission_backend import get_filtered_instances
from arches.app.utils.response import JSONResponse
from arches.app.views.api import APIBase


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
        features = []
        i = 1
        property_tiles = models.TileModel.objects.filter(nodegroup_id__in=nodegroups)
        property_node_map = {}
        property_nodes = models.Node.objects.filter(nodegroup_id__in=nodegroups)
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
            nodegroup_id__in=[node.nodegroup_id for node in nodes]
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
        viewable_nodegroups = request.user.userprofile.viewable_nodegroups
        user = request.user

        tile = MVTTiler().createTile(nodeid, viewable_nodegroups, user, zoom, x, y)
        if not tile or not len(tile):
            raise Http404()
        return HttpResponse(tile, content_type="application/x-protobuf")
