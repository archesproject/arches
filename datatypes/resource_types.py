import json
import logging
import uuid

from arches import VERSION as arches_version
from arches.app.datatypes import datatypes
from arches.app.models import models

from django.utils.translation import get_language, gettext as _


logger = logging.getLogger(__name__)


class ResourceInstanceDataType(datatypes.ResourceInstanceDataType):
    def transform_value_for_tile(self, value, **kwargs):
        def from_id_string(uuid_string, graph_id=None):
            nonlocal kwargs
            for graph_config in kwargs.get("graphs", []):
                if graph_id is None or str(graph_id) == graph_config["graphid"]:
                    break
            else:
                graph_config = {}
            return {
                "resourceId": uuid_string,
                "ontologyProperty": graph_config.get("ontologyProperty", ""),
                "inverseOntologyProperty": graph_config.get(
                    "inverseOntologyProperty", ""
                ),
            }

        try:
            if isinstance(value, str):
                value = [value]
                raise TypeError
            return json.loads(value)
        except TypeError:
            if isinstance(value, list):
                transformed = []
                for inner in value:
                    match inner:
                        case models.ResourceInstance():
                            transformed.append(
                                from_id_string(str(inner.pk), inner.graph_id)
                            )
                        case uuid.UUID():
                            # TODO: handle multiple graph configs, requires db?
                            transformed.append(from_id_string(str(inner)))
                        case str():
                            # TODO: handle multiple graph configs, requires db?
                            transformed.append(from_id_string(inner))
                        case _:
                            # TODO: move this to validate?
                            inner.pop("display_value", None)
                            transformed.append(inner)
                return transformed
            if isinstance(value, models.ResourceInstance):
                return [from_id_string(str(value.pk), value.graph_id)]
            raise

    def to_json(self, tile, node):
        details = self.get_details(tile, node)
        return {
            "@display_value": self.get_display_value(tile, node, details=details),
            "@details": details,
        }

    def get_display_value(self, tile, node, *, details=None, **kwargs):
        if details is None:
            details = self.get_details(tile, node)
        return ", ".join([detail["display_value"] for detail in details])

    def get_details(self, tile, node):
        resource_details = []
        for inner_val in tile.data.get(str(node.nodeid)) or []:
            if not inner_val:
                continue
            lang = get_language()
            try:
                rxrs = tile.resourceinstance.filtered_from_resxres
            except:
                # TODO: why?
                if arches_version >= (8, 0):
                    rxrs = tile.resourceinstance.from_resxres.all()
                else:
                    rxrs = (
                        tile.resourceinstance.resxres_resource_instance_ids_from.all()
                    )
            for rxr in rxrs:
                to_resource_id = (
                    rxr.resourceinstanceidto_id
                    if arches_version < (8, 0)
                    else rxr.to_resource_id
                )
                if to_resource_id == uuid.UUID(inner_val["resourceId"]):
                    try:
                        to_resource = (
                            rxr.resourceinstanceidto
                            if arches_version < (8, 0)
                            else rxr.to_resource
                        )
                    except models.ResourceInstance.DoesNotExist:
                        msg = f"Missing ResourceXResource target: {to_resource_id}"
                        logger.warning(msg)
                        resource_details.append(
                            {
                                "resourceId": to_resource_id,
                                "display_value": _("Missing"),
                            }
                        )
                        break
                    # TODO: gracefully handle missing language.
                    display_value = to_resource.descriptors[lang]["name"]
                    resource_details.append(
                        {
                            "resourceId": to_resource_id,
                            "display_value": display_value,
                        }
                    )
                    break

        return resource_details

    def get_interchange_value(self, value, *, details, **kwargs):
        if not value:
            return []
        if details is None:
            self.get_details(value)
        resource_display_value_map = {
            str(detail["resourceId"]): detail["display_value"] for detail in details
        }
        return [
            {
                "resourceId": inner["resourceId"],
                "display_value": resource_display_value_map[inner["resourceId"]],
            }
            for inner in value
        ]


class ResourceInstanceListDataType(ResourceInstanceDataType):
    def collects_multiple_values(self):
        return True
