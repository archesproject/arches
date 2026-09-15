from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.functions.primary_descriptors import AbstractPrimaryDescriptorsFunction
from arches.app.models.system_settings import settings
from arches.app.models import models
import re

from django.utils.translation import get_language, gettext as _

details = {
    "functionid": "00b2d15a-fda0-4578-b79a-784e4138664b",
    "name": "Multi-card Resource Descriptor",
    "type": "primarydescriptors",
    "description": "Configure the name, description, and map popup of a resource",
    "defaultconfig": {
        "descriptor_types": {
            "name": {
                "nodegroup_id": "",
                "string_template": "",
            },
            "map_popup": {
                "nodegroup_id": "",
                "string_template": "",
            },
            "description": {
                "nodegroup_id": "",
                "string_template": "",
            },
        }
    },
    "classname": "MulticardResourceDescriptor",
    "component": "views/components/functions/multicard-resource-descriptor",
}


class MulticardResourceDescriptor(AbstractPrimaryDescriptorsFunction):
    """Updates multicard
    This implementation just fetches the calculated result from the db."""

    # Class-level cache: (frozenset(aliases), graph_id) -> list[Node]
    # Nodes for a given graph/template are constant; no need to re-query per resource.
    _node_cache: dict = {}

    @classmethod
    def _get_nodes(cls, node_aliases, graph_id):
        key = (frozenset(node_aliases), str(graph_id))
        if key not in cls._node_cache:
            cls._node_cache[key] = list(
                models.Node.objects.filter(alias__in=node_aliases, graph_id=graph_id)
            )
        return cls._node_cache[key]

    def get_primary_descriptor_from_nodes(
        self, resource, config, context=None, descriptor=None
    ):
        resource.get_descriptor_language(context)
        requested_language = context.get("language", None) if context else None
        lookup_language = requested_language or get_language() or settings.LANGUAGE_CODE
        result = config["string_template"]

        node_aliases = extract_substrings(result)
        nodes = self._get_nodes(node_aliases, resource.graph_id)

        # Build a nodegroup -> tile lookup from pre-fetched tiles when available,
        # falling back to a DB query only when resource.tiles hasn't been loaded.
        if resource.tiles:
            tiles_by_nodegroup = {}
            for tile in resource.tiles:
                nodegroup = tile.nodegroup_id
                if (
                    nodegroup not in tiles_by_nodegroup
                    or tile.sortorder < tiles_by_nodegroup[nodegroup].sortorder
                ):
                    tiles_by_nodegroup[nodegroup] = tile
        else:
            tiles_by_nodegroup = {}
            nodegroup_ids = [node.nodegroup_id for node in nodes]
            for tile in models.TileModel.objects.filter(
                resourceinstance_id=resource.resourceinstanceid,
                nodegroup_id__in=nodegroup_ids,
            ).order_by("nodegroup_id", "sortorder"):
                tiles_by_nodegroup.setdefault(tile.nodegroup_id, tile)

        datatype_factory = DataTypeFactory()
        for node in nodes:
            datatype = datatype_factory.get_instance(node.datatype)

            tile = tiles_by_nodegroup.get(node.nodegroup_id)

            if tile is not None:
                value = datatype.get_display_value(tile, node, language=lookup_language)
            else:
                value = ""
            result = result.replace("<%s>" % node.alias, str(value))
        return result


def extract_substrings(template_string):
    pattern = r"<(.*?)>"
    substrings = re.findall(pattern, template_string)

    return substrings
