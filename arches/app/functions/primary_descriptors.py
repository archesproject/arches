import uuid
from arches.app.functions.base import BaseFunction
from arches.app.models import models
from arches.app.models.tile import Tile
from arches.app.datatypes.datatypes import DataTypeFactory
from django.utils.translation import ugettext as _


class PrimaryDescriptorsFunction(BaseFunction):
    def get_primary_descriptor_from_nodes(self, resource, config):
        map_popup = False
        map_popup_template_default = "<Place Address> (<Address Type>)"
        display_name_template_default = "<Name> - <Place Address>"
        display_name_template_preferred = "<Name>\n<Place Address>"
        # sans_addr_display_name_template_default = "<Name>"
        hist_res_name = False
        hist_res_name_ngid = 'a271c354-1037-11ec-b65f-31043b30bbcd'
        if config["string_template"] == map_popup_template_default:
            map_popup = True
        if config["string_template"] == display_name_template_default:
            hist_res_name = True
            config["string_template"] = display_name_template_preferred
        datatype_factory = None
        # from pprint import pprint
        # print("COFIG")
        # pprint(config)
        try:
            if "nodegroup_id" in config and config["nodegroup_id"] != "" and config["nodegroup_id"] is not None:
                tiles = list(models.TileModel.objects.filter(nodegroup_id=uuid.UUID(config["nodegroup_id"]), sortorder=0).filter(
                    resourceinstance_id=resource.resourceinstanceid
                ))
                if len(tiles) == 0:
                    tiles = list(models.TileModel.objects.filter(nodegroup_id=uuid.UUID(config["nodegroup_id"])).filter(
                        resourceinstance_id=resource.resourceinstanceid
                    ))
                if hist_res_name:
                    name_tile = models.TileModel.objects.filter(nodegroup_id=uuid.UUID(hist_res_name_ngid), sortorder=0).filter(
                        resourceinstance_id=resource.resourceinstanceid
                    )
                    if len(name_tile) > 0:
                        tiles.append(name_tile[0])
                for tile in tiles:
                    if hist_res_name:
                        ng_ids = [config["nodegroup_id"], hist_res_name_ngid]
                    else:
                        ng_ids = [config["nodegroup_id"]]
                    for node in models.Node.objects.filter(nodegroup_id__in=ng_ids):
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
                            if str(value) not in config["string_template"]:
                                config["string_template"] = config["string_template"].replace("<%s>" % node.name, str(value))
                            if map_popup and map_popup_template_default not in config["string_template"]:
                                config["string_template"] += "<br>" + map_popup_template_default.replace("<%s>" % node.name, str(value))
        except ValueError as e:
            print(e, "invalid nodegroupid participating in descriptor function.")
        if config["string_template"].strip() == "":
            config["string_template"] = _("Undefined")
        return config["string_template"]
