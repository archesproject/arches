import logging
import uuid
from itertools import chain

from arches import VERSION as arches_version
from arches.app.datatypes import datatypes
from arches.app.models import models
from django.utils.translation import get_language
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)


class ResourceInstanceDataType(datatypes.ResourceInstanceDataType):
    def transform_value_for_tile(self, value, **kwargs):
        parsed = super().transform_value_for_tile(value, **kwargs)
        if parsed is None:
            parsed = value

        graph_configs_by_graph_id = {
            graph_config["graphid"]: graph_config
            for graph_config in kwargs.get("graphs", [])
        }

        if not isinstance(parsed, list):
            parsed = [parsed]
        transformed = []
        for inner_val in parsed:
            match inner_val:
                case models.ResourceInstance():
                    transformed.append(
                        self.from_id_string(
                            str(inner_val.pk),
                            graph_configs_by_graph_id.get(inner_val.graph_id),
                        )
                    )
                case uuid.UUID():
                    # TODO: handle multiple graph configs, requires db?
                    transformed.append(self.from_id_string(str(inner_val)))
                case str():
                    # TODO: handle multiple graph configs, requires db?
                    transformed.append(self.from_id_string(inner_val))
                case _:
                    transformed.append(inner_val)
        return transformed

    def get_resource(self, tile):
        try:
            return tile.resourceinstance
        except models.ResourceInstance.DoesNotExist:
            return None
        except AttributeError:
            resource_id = tile["resourceinstance_id"]
            return models.ResourceInstance.objects.filter(pk=resource_id).first()

    def get_display_value(self, tile, node, *, details=None, **kwargs):
        if details is None:
            data = self.get_tile_data(tile)
            value = data.get(str(node.nodeid))
            resource = self.get_resource(tile)
            details = self.get_details(value, resource=resource)
        return ", ".join(
            [detail["display_value"] or "" for detail in details if detail]
        )

    def to_python(self, value, *, resource=None):
        if not (related_resources := self.get_related_resources(value, resource)):
            return None
        return related_resources[0]

    def get_related_resources(self, value, resource):
        if not value:
            return []
        related_resources = []

        # arches_version==9.0.0
        if arches_version >= (8, 0):
            relations = resource.from_resxres.all()
        else:
            relations = resource.resxres_resource_instance_ids_from.all()

        def handle_missing_data(to_resource_id):
            msg = f"Missing ResourceXResource target: {to_resource_id}"
            logger.warning(msg)

        for inner_val in value:
            if not inner_val:
                continue
            target_resource_id = uuid.UUID(inner_val["resourceId"])
            if not relations:
                # arches_version==9.0.0
                if arches_version >= (8, 0):
                    relations = models.ResourceXResource.objects.filter(
                        to_resource_id=target_resource_id
                    ).select_related("to_resource")
                else:
                    relations = models.ResourceXResource.objects.filter(
                        resourceinstanceidto_id=target_resource_id
                    ).select_related("resourceinstanceidto")

            for relation in relations:
                to_resource_id = (
                    relation.resourceinstanceidto_id
                    # arches_version==9.0.0
                    if arches_version < (8, 0)
                    else relation.to_resource_id
                )
                if to_resource_id == target_resource_id:
                    try:
                        to_resource = (
                            relation.resourceinstanceidto
                            # arches_version==9.0.0
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

    def get_details(self, value, *, resource=None, **kwargs):
        lang = get_language()
        related_resources_by_id = {
            related_resource.pk: related_resource
            for related_resource in self.get_related_resources(value, resource)
        }
        ret = []
        for inner_val in value or []:
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
                        "resource_id": None,
                        "display_value": _("Missing"),
                    }
                )
        return ret

    @staticmethod
    def from_id_string(uuid_string, graph_config=None):
        if graph_config is None:
            graph_config = {}
        return {
            "resourceId": uuid_string,
            "ontologyProperty": graph_config.get("ontologyProperty", ""),
            "inverseOntologyProperty": graph_config.get("inverseOntologyProperty", ""),
        }

    @staticmethod
    def values_match(value1, value2):
        if not isinstance(value1, list) or not isinstance(value2, list):
            return value1 == value2
        copy1 = [{**inner_val} for inner_val in value1]
        copy2 = [{**inner_val} for inner_val in value2]
        for inner_val in chain(copy1, copy2):
            inner_val.pop("resourceXresourceId", None)
        return copy1 == copy2


class ResourceInstanceListDataType(ResourceInstanceDataType):
    def collects_multiple_values(self):
        return True

    def to_python(self, value, *, resource=None):
        if not (related_resources := self.get_related_resources(value, resource)):
            return None
        return related_resources

    def get_details(self, value, *, resource=None, **kwargs):
        if not value:
            return []
        details = super().get_details(value=value, resource=resource, **kwargs)
        resource_display_value_map = {
            str(detail["resource_id"]): detail["display_value"] for detail in details
        }
        return [
            {
                "resource_id": resource_dict["resourceId"],
                "display_value": resource_display_value_map.get(
                    resource_dict["resourceId"], _("Missing")
                ),
            }
            for resource_dict in value
        ]
