import uuid
from dataclasses import asdict, dataclass
from typing import Iterable, Mapping

from django.db.models import F, JSONField
from django.utils.translation import gettext as _

from arches.app.datatypes.base import BaseDataType
from arches.app.models.models import Node
from arches.app.models.graph import GraphValidationError
from arches.app.search.elasticsearch_dsl_builder import (
    Exists,
    Match,
)

from arches_controlled_lists.models import ListItem

try:
    import rest_framework.fields
except:
    pass
else:

    class ReferenceSerializer(rest_framework.fields.JSONField):
        def to_internal_value(self, data):
            return ReferenceDataType().to_python(data)


class ReferenceField(JSONField): ...


@dataclass(kw_only=True)
class ReferenceLabel:
    id: uuid.UUID
    value: str
    language_id: str
    valuetype_id: str
    list_item_id: uuid.UUID


@dataclass(kw_only=True)
class Reference:
    uri: str
    labels: list[ReferenceLabel]
    list_id: uuid.UUID


class ReferenceDataType(BaseDataType):
    model_field = ReferenceField(null=True)

    def to_python(
        self, value: Iterable[Mapping] | None, **kwargs
    ) -> list[Reference] | None:
        if not value:
            return None

        references = []
        for reference in value:
            incoming_args = {**reference}
            if labels := incoming_args.get("labels"):
                incoming_args["labels"] = [
                    ReferenceLabel(**label) for label in incoming_args["labels"]
                ]
            elif labels == []:
                incoming_args.pop("labels")
            references.append(Reference(**incoming_args))

        return references or None

    def serialize(self, value):
        """
        Unlike to_json() which is concerned with calculating display values, this
        method simply serializes all the information held in the Reference(s).
        """
        if value is None:
            return None
        return [
            asdict(reference) if isinstance(reference, Reference) else {**reference}
            for reference in value
        ]

    def validate(
        self,
        value,
        row_number=None,
        source="",
        node=None,
        nodeid=None,
        strict=False,
        **kwargs,
    ):
        try:
            parsed = self.to_python(value)
            self.validate_pref_labels(parsed)
            self.validate_list_item_consistency(parsed)
            self.validate_multivalue(parsed, node, nodeid)
        except Exception as e:
            return [self.transform_exception(e)]
        return []

    def validate_pref_labels(self, references: list[Reference] | None):
        if not references:
            return
        for reference in references:
            pref_label_languages = [
                label.language_id
                for label in reference.labels
                if label.valuetype_id == "prefLabel"
            ]
            if len(set(pref_label_languages)) < len(pref_label_languages):
                msg = _("A reference can have only one prefLabel per language")
                raise ValueError(msg)

    def validate_list_item_consistency(self, references: list[Reference] | None):
        if not references:
            return
        for reference in references:
            list_item_ids = {ref.list_item_id for ref in reference.labels}
            if len(list_item_ids) != 1:
                msg = _("Found multiple list items among labels: {reference}")
                raise ValueError(msg)

    def validate_multivalue(self, parsed: list[Reference] | None, node, nodeid):
        if not parsed:
            return
        if not node:
            if not nodeid:
                raise ValueError
            try:
                node = Node.objects.get(nodeid=nodeid)
            except Node.DoesNotExist:
                return
        if not node.config.get("multiValue") and len(parsed) > 1:
            raise ValueError(_("This node does not allow multiple references."))

    @staticmethod
    def transform_exception(e):
        message = _("Unknown error")
        if isinstance(e, TypeError) and e.args:
            # Localize the error raised by the dataclass constructor.
            if "__init__() missing" in e.args[0]:
                message = _("Missing required value(s): {}").format(
                    e.args[0].split(": ")[-1]
                )
            elif "unexpected keyword argument" in e.args[0]:
                message = _("Unexpected value: {}").format(
                    e.args[0].split("argument ")[-1]
                )
        elif isinstance(e, ValueError) and e.args:
            message = e.args[0]
        return {
            "type": "ERROR",
            "message": message,
            "title": _("Invalid Reference Datatype Value"),
        }

    def transform_value_for_tile(self, value, **kwargs):
        if value is None:
            return None
        if not isinstance(value, list):
            value = [val.strip() for val in value.split(",")]

        # Pre-process to discard display values generated by to_json().
        pre_processed_values = []
        for single_value in value:
            if isinstance(single_value, dict) and (
                list_item_id := single_value.get("list_item_id")
            ):
                pre_processed_values.append(list_item_id)
            else:
                pre_processed_values.append(single_value)

        final_tile_values = []
        for single_value in pre_processed_values:
            found_item: ListItem | Reference | None = None
            match single_value:
                case Reference():
                    found_item = single_value
                case uuid.UUID():
                    found_item = ListItem.objects.filter(pk=list_item_id).first()
                case str():
                    try:
                        list_item_id = uuid.UUID(single_value)
                    except ValueError:
                        list_id = kwargs.get("controlledList")
                        found_item = self.lookup_listitem_from_label(
                            single_value, list_id
                        )
                    else:
                        found_item = ListItem.objects.filter(pk=list_item_id).first()
                case _:
                    raise TypeError(type(single_value))

            if found_item:
                if isinstance(found_item, Reference):
                    final_tile_values.append(asdict(found_item))
                else:
                    final_tile_values.append(found_item.build_tile_value())

        return final_tile_values

    def lookup_listitem_from_label(self, value, list_id):
        if not value or not list_id:
            return None
        return (
            ListItem.objects.filter(list_id=list_id, list_item_values__value=value)
            .order_by(F("parent").asc(nulls_first=True), "sortorder")
            .first()
        )

    def clean(self, tile, nodeid):
        super().clean(tile, nodeid)
        if tile.data[nodeid] == []:
            tile.data[nodeid] = None

    def transform_export_values(self, value, *args, **kwargs):
        if value is not None:
            # Temporarily use concept_export_value_type to determine export format
            # TODO: when RDM/concepts are depricated update name of kwarg
            concept_export_value_type = kwargs.get("concept_export_value_type")

            new_values = []
            for val in value:
                if concept_export_value_type == "id":
                    new_values.append(val["uri"])
                elif (
                    concept_export_value_type is None
                    or concept_export_value_type == ""
                    or concept_export_value_type == "label"
                ):
                    labels = [ReferenceLabel(**label) for label in val["labels"]]
                    best_label = ListItem.find_best_label_from_set(
                        labels, kwargs.get("language")
                    )
                    new_values.append(best_label)
                else:
                    new_values.append(val)
            return ",".join(new_values)

    def get_display_value(self, tile, node, **kwargs):
        requested_language = kwargs.pop("language", None)
        node_data = self.get_tile_data(tile)
        value = node_data.get(str(node.pk), None)
        references = self.to_python(value)
        if not references:
            return ""
        else:
            best_labels = [
                ListItem.find_best_label_from_set(reference.labels, requested_language)
                for reference in references
            ]
            return ", ".join(best_labels)

    def get_display_value_context_in_bulk(self, values):
        list_item_ids = set()
        for value in values:
            if value:
                for item in value:
                    if item.get("labels"):
                        if item_id := item["labels"][0].get("list_item_id"):
                            list_item_ids.add(item_id)

        return (
            ListItem.objects.filter(id__in=list_item_ids)
            .with_list_item_labels()
            .prefetch_related("children")
        )

    def get_details(self, value, *, datatype_context=None, **kwargs):
        """
        Expects tile representation of reference datatype:
        [
            {
                "uri": "",
                "labels": [
                    {
                        "id": "uuid",
                        "value": "label",
                        "language_id": "en",
                        "valuetype_id": "prefLabel",
                        "list_item_id": "uuid"
                    }
                ],
                "list_id": "uuid"
            }
        ]
        Returns list item transformed for use in dropdown pickers:
        [
            {
                "list_item_id": "uuid",
                "uri": "",
                "list_item_values": [
                    {
                        "id": "uuid",
                        "value": "Parent",
                        "language_id": "en",
                        "valuetype_id": "prefLabel",
                        "list_item_id": "uuid"
                    }
                ],
                "display_value": "",
                "sortorder": 0,
                "children": [
                    {
                        "list_item_id": "uuid",
                        "uri": "",
                        "list_item_values": [
                            {
                                "id": "uuid",
                                "value": "Child",
                                "language_id": "en",
                                "valuetype_id": "prefLabel",
                                "list_item_id": "uuid"
                            }
                        ],
                        "display_value": "",
                        "sortorder": 0,
                        "children": []
                    }
                ]
            }
        ]
        """
        list_item_ids: set[uuid.UUID] = set()
        if value:
            for default_val in value:
                list_item_ids.add(uuid.UUID(default_val["labels"][0]["list_item_id"]))
        else:
            return None

        if datatype_context is None:
            datatype_context = []
        # Get as many items from the datatypes_context as possible ...
        transformed_items = [
            item.build_select_option()
            for item in datatype_context
            if item.pk in list_item_ids
        ]
        # ... and fetch the rest.
        remaining_ids_to_fetch = [
            item_id
            for item_id in list_item_ids
            if ListItem(pk=item_id) not in datatype_context
        ]
        items_to_fetch = (
            ListItem.objects.filter(id__in=remaining_ids_to_fetch)
            .with_list_item_labels()
            .prefetch_related("children")
        )
        remaining_transformed_items = [
            item.build_select_option() for item in items_to_fetch
        ]

        return transformed_items + remaining_transformed_items

    def collects_multiple_values(self):
        return True

    def default_es_mapping(self):
        return {
            "properties": {
                "uri": {"type": "keyword"},
                "id": {"type": "keyword"},
                "labels": {
                    "properties": {},
                },
            }
        }

    def validate_node(self, node):
        try:
            uuid.UUID(node.config["controlledList"])
        except (TypeError, KeyError):
            raise GraphValidationError(
                _("A reference datatype node requires a controlled list")
            )

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        if "references" not in document:
            document["references"] = []
        for reference in self.get_nodevalues(nodevalue):
            for label in reference["labels"]:
                document["references"].append(
                    {
                        "id": label["id"],
                        "uri": reference["uri"],
                        "list_id": reference["list_id"],
                        "nodegroup_id": tile.nodegroup_id,
                        "provisional": provisional,
                    }
                )
                document["strings"].append(
                    {
                        "string": label["value"],
                        "nodegroup_id": tile.nodegroup_id,
                        "provisional": provisional,
                    }
                )

    def append_search_filters(self, value, node, query, request):
        # value["val"] is expected to be a list slimmed reference dictionaries:
        # {"labels":[...], "uri": "..."}
        try:
            values_list = value.get("val", [])
            if value["op"] == "null" or value["op"] == "not_null":
                self.append_null_search_filters(value, node, query, request)
            elif values_list:
                uri_field = f"tiles.data.{str(node.pk)}.uri"
                operation = value["op"]
                for val in values_list:
                    uri = val.get("uri", val) if isinstance(val, dict) else val
                    match_query = Match(field=uri_field, type="phrase", query=uri)

                    if operation == "in_list_any":
                        query.should(match_query)
                    elif operation == "in_list_all":
                        query.must(match_query)
                    elif operation == "in_list_not":
                        query.must_not(match_query)
                    elif "!" in operation:
                        query.must_not(match_query)
                        query.filter(Exists(field=uri_field))
                    else:
                        query.must(match_query)

        except KeyError:
            pass
