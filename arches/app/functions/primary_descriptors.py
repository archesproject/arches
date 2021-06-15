import uuid
from arches.app.functions.base import BaseFunction
from arches.app.models import models
from arches.app.models.tile import Tile
from arches.app.datatypes.datatypes import DataTypeFactory
from django.utils.translation import ugettext as _


class PrimaryDescriptorsFunction(BaseFunction):
    def get_primary_descriptor_from_nodes(self, resource, config):
        datatype_factory = None
        try:
            if "nodegroup_id" in config and config["nodegroup_id"] != "" and config["nodegroup_id"] is not None:
                tiles = models.TileModel.objects.filter(nodegroup_id=uuid.UUID(config["nodegroup_id"]), sortorder=0).filter(
                    resourceinstance_id=resource.resourceinstanceid
                )
                if len(tiles) == 0:
                    tiles = models.TileModel.objects.filter(nodegroup_id=uuid.UUID(config["nodegroup_id"])).filter(
                        resourceinstance_id=resource.resourceinstanceid
                    )
                for tile in tiles:
                    for node in models.Node.objects.filter(nodegroup_id=uuid.UUID(config["nodegroup_id"])):
                        data = {}
                        if len(list(tile.data.keys())) > 0:
                            data = tile.data
                        elif tile.provisionaledits is not None and len(list(tile.provisionaledits.keys())) == 1:
                            userid = list(tile.provisionaledits.keys())[0]
                            data = tile.provisionaledits[userid]["value"]
                        if str(node.nodeid) in data:
                            if not datatype_factory:
                                datatype_factory = DataTypeFactory()
                            datatype = datatype_factory.get_instance(node.datatype)
                            value = datatype.get_display_value(tile, node)
                            if value is None:
                                value = ""
                            config["string_template"] = config["string_template"].replace("<%s>" % node.name, str(value))
        except ValueError as e:
            print(e, "invalid nodegroupid participating in descriptor function.")
        if config["string_template"].strip() == "":
            config["string_template"] = _("Undefined")
        return config["string_template"]
