import uuid
from dataclasses import asdict, dataclass

from django.utils.translation import get_language, gettext as _

from arches.app.datatypes.base import BaseDataType
from arches.app.models.models import Node
from arches.app.models.graph import GraphValidationError

from arches_controlled_lists.models import ListItem


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
    def to_python(self, value):
        if value is None:
            return None
        if not value:
            raise ValueError(_("Reference datatype value cannot be empty"))

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

        return references

    def serialize(self, value):
        if isinstance(value, list):
            return [
                asdict(reference) if isinstance(reference, Reference) else {**reference}
                for reference in value
            ]
        return value

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

    def validate_multivalue(self, parsed, node, nodeid):
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
                message = _(
                    "Missing required value(s): {}".format(e.args[0].split(": ")[-1])
                )
            elif "unexpected keyword argument" in e.args[0]:
                message = _(
                    "Unexpected value: {}".format(e.args[0].split("argument ")[-1])
                )
        elif isinstance(e, ValueError) and e.args:
            message = e.args[0]
        return {
            "type": "ERROR",
            "message": message,
            "title": _("Invalid Reference Datatype Value"),
        }

    def transform_value_for_tile(self, value, **kwargs):
        list_id = kwargs.get("controlledList")
        value = self.serialize(value)
        if (
            isinstance(value, list)
            and isinstance(value[0], dict)
            and "value" in value[0]
        ):
            value = value[0]["value"]
        if isinstance(value, str):
            found_item = self.lookup_listitem_from_label(value, list_id)
            if found_item:
                value = [found_item.build_tile_value()]
        return value

    def lookup_listitem_from_label(self, value, list_id):
        return (
            ListItem.objects.filter(list_id=list_id, list_item_values__value=value)
            .order_by("sortorder")
            .first()
        )

    def clean(self, tile, nodeid):
        super().clean(tile, nodeid)
        if tile.data[nodeid] == []:
            tile.data[nodeid] = None

    def transform_export_values(self, value, *args, **kwargs):
        return ",".join(value)

    def get_display_value(self, tile, node, **kwargs):
        labels = []
        requested_language = kwargs.pop("language", None)
        current_language = requested_language or get_language()
        node_data = self.get_tile_data(tile)[str(node.nodeid)]
        if node_data:
            for item in node_data:
                for label in item["labels"]:
                    if (
                        label["language_id"] == current_language
                        and label["valuetype_id"] == "prefLabel"
                    ):
                        labels.append(label.get("value", ""))
        return ", ".join(labels)

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
