import logging
import uuid
from arches.app.utils.betterJSONSerializer import JSONSerializer
from arches.app.functions.base import BaseFunction
from arches.app.models import models
from arches.app.datatypes.datatypes import DataTypeFactory
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)


class AbstractPrimaryDescriptorsFunction(BaseFunction):
    def get_primary_descriptor_from_nodes(
        self, resource, config, context=None, descriptor=None
    ):
        """
        Arguments:
        resource -- the resource instance to which the primary decriptor will be assigned
        config -- the descriptor config which indicates how and what will define the descriptor

        Keyword Arguments:
        context -- string such as "copy" to indicate conditions under which a resource participates in a function.
        descriptor -- type of descriptor, e.g. "name", "map_popup", or "description"
        """

        pass


class PrimaryDescriptorsFunction(AbstractPrimaryDescriptorsFunction):
    def get_primary_descriptor_from_nodes(
        self, resource, config, context=None, descriptor=None
    ):
        """
        Arguments:
        resource -- the resource instance to which the primary decriptor will be assigned
        config -- the descriptor config which indicates how and what will define the descriptor

        Keyword Arguments:
        context -- string such as "copy" to indicate conditions under which a resource participates in a function.
        descriptor -- type of descriptor, e.g. "name", "map_popup", or "description"
        """

        datatype_factory = None
        language = (
            context["language"]
            if (context is not None and "language" in context)
            else None
        )
        result = config["string_template"]
        updated = False

        try:
            if (
                "nodegroup_id" in config
                and config["nodegroup_id"] != ""
                and config["nodegroup_id"] is not None
            ):
                tile = context.get("tile")

                if not tile or tile.sortorder:
                    tile = (
                        models.TileModel.objects.filter(
                            nodegroup_id=uuid.UUID(config["nodegroup_id"])
                        )
                        .filter(resourceinstance_id=resource.resourceinstanceid)
                        .order_by("sortorder")
                        .first()
                    )

                if not tile:  # tile has been deleted
                    result = ""
                    updated = True
                else:
                    for node in models.Node.objects.filter(
                        nodegroup_id=uuid.UUID(config["nodegroup_id"])
                    ):
                        data = {}
                        if len(list(tile.data.keys())) > 0:
                            data = tile.data
                        elif (
                            tile.provisionaledits is not None
                            and len(list(tile.provisionaledits.keys())) == 1
                        ):
                            userid = list(tile.provisionaledits.keys())[0]
                            data = tile.provisionaledits[userid]["value"]
                        if str(node.nodeid) in data:
                            if not datatype_factory:
                                datatype_factory = DataTypeFactory()
                            datatype = datatype_factory.get_instance(node.datatype)
                            value = datatype.get_display_value(
                                tile, node, language=language
                            )
                            if value is None:
                                value = ""
                            result = result.replace("<%s>" % node.name, str(value))
                            updated = True
        except ValueError:
            logger.error(
                _(
                    "Invalid nodegroupid, {0}, participating in descriptor function."
                ).format(config["nodegroup_id"])
            )
        if result.strip() == "":
            result = _("Undefined")
        if not updated:
            try:
                result = resource.descriptors[language][descriptor]
            except KeyError:
                pass

        return result
