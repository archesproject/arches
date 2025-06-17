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
        graph_configs_by_graph_id = {
            graph_config["graphid"]: graph_config
            for graph_config in kwargs.get("graphs", [])
        }
        try:
            if isinstance(value, (str, dict)):
                value = [value]
                raise TypeError
            return json.loads(value)
        except TypeError:
            if isinstance(value, list):
                transformed = []
                for inner_val in value:
                    match inner_val:
                        case models.ResourceInstance():
                            transformed.append(
                                self.from_id_string(
                                    str(inner_val.pk),
                                    graph_configs_by_graph_id.get(
                                        inner_val.graph_id, None
                                    ),
                                )
                            )
                        case uuid.UUID():
                            # TODO: handle multiple graph configs, requires db?
                            transformed.append(self.from_id_string(str(inner_val)))
                        case str():
                            # TODO: handle multiple graph configs, requires db?
                            transformed.append(self.from_id_string(inner_val))
                        case dict():
                            # TODO: handle multiple graph configs, requires db?
                            transformed.append(
                                self.from_id_string(inner_val.get("resource_id"))
                            )
                        case _:
                            transformed.append(inner_val)
                return transformed
            if isinstance(value, models.ResourceInstance):
                return [
                    self.from_id_string(
                        str(value.pk),
                        graph_configs_by_graph_id.get(value.graph_id, None),
                    )
                ]
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

    def to_python(self, value, *, tile, **kwargs):
        if not (related_resources := self.get_related_resources(tile, value)):
            return None
        return related_resources[0]

    def get_related_resources(self, tile, value):
        if not value:
            return []
        related_resources = []
        try:
            relations = tile.resourceinstance.from_resxres_for_queried_nodes
        except:
            if arches_version >= (8, 0):  # TODO: why?
                relations = tile.resourceinstance.from_resxres.all()
            else:
                relations = (
                    tile.resourceinstance.resxres_resource_instance_ids_from.all()
                )

        def handle_missing_data(to_resource_id):
            msg = f"Missing ResourceXResource target: {to_resource_id}"
            logger.warning(msg)

        for inner_val in value:
            if not inner_val:
                continue
            for relation in relations:
                to_resource_id = (
                    relation.resourceinstanceidto_id
                    if arches_version < (8, 0)
                    else relation.to_resource_id
                )
                if to_resource_id == uuid.UUID(inner_val["resourceId"]):
                    try:
                        to_resource = (
                            relation.resourceinstanceidto
                            if arches_version < (8, 0)
                            else relation.to_resource
                        )
                        if to_resource is None:
                            raise models.ResourceInstance.DoesNotExist
                    except models.ResourceInstance.DoesNotExist:
                        handle_missing_data(to_resource_id)
                        break
                    related_resources.append(to_resource)
                    break

        return related_resources

    def get_details(self, tile, node):
        lang = get_language()
        value = tile.data.get(str(node.nodeid)) or []
        related_resources_by_id = {
            related_resource.pk: related_resource
            for related_resource in self.get_related_resources(tile, value)
        }
        ret = []
        for inner_val in value:
            if not inner_val:
                continue
            if related := related_resources_by_id.get(
                uuid.UUID(inner_val["resourceId"]), None
            ):
                ret.append(
                    {
                        "resource_id": str(related.pk),
                        # TODO: gracefully handle missing language.
                        "display_value": related.descriptors[lang]["name"],
                    }
                )
            else:
                ret.append(
                    {
                        "resource_id": str(related.pk),
                        "display_value": _("Missing"),
                    }
                )
        return ret

    def get_interchange_value(self, value, *, details=None, **kwargs):
        if not value:
            return None
        if details is None:
            details = self.get_details(value)
        return details[0]["resource_id"]

    @staticmethod
    def from_id_string(uuid_string, graph_config=None):
        if graph_config is None:
            graph_config = {}
        return {
            "resourceId": uuid_string,
            "ontologyProperty": graph_config.get("ontologyProperty", ""),
            "inverseOntologyProperty": graph_config.get("inverseOntologyProperty", ""),
        }


class ResourceInstanceListDataType(ResourceInstanceDataType):
    def collects_multiple_values(self):
        return True

    def to_python(self, value, *, tile, **kwargs):
        if not (related_resources := self.get_related_resources(tile, value)):
            return None
        return related_resources

    def get_interchange_value(self, value, *, details=None, **kwargs):
        if not value:
            return None
        if details is None:
            details = self.get_details(value)
        resource_display_value_map = {
            str(detail["resource_id"]): detail["display_value"] for detail in details
        }
        return [
            {
                "resource_id": resource_dict["resourceId"],
                "display_value": resource_display_value_map[
                    resource_dict["resourceId"]
                ],
            }
            for resource_dict in value
        ]
