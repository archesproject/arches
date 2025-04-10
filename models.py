from __future__ import annotations

import datetime
import uuid
from collections import defaultdict
from typing import Iterable

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import Deferrable, Q
from django.utils import translation
from django.utils.translation import gettext_lazy as _

from arches.app.models.models import DValueType, Language, Node
from arches.app.models.utils import field_names
from arches.app.utils.i18n import rank_label
from arches_controlled_lists.querysets import (
    ListQuerySet,
    ListItemQuerySet,
    ListItemImageManager,
    ListItemValueQuerySet,
    NodeQuerySet,
)


class List(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=127, null=False, blank=True)
    dynamic = models.BooleanField(default=False)
    search_only = models.BooleanField(default=False)

    objects = ListQuerySet.as_manager()

    def __str__(self):
        return str(self.name)

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude=exclude)
        if (not exclude or "name" not in exclude) and not self.name:
            self.name = _("Untitled List: ") + datetime.datetime.now().isoformat(
                sep=" ", timespec="seconds"
            )

    def serialize(self, depth_map=None, flat=False, permitted_nodegroups=None):
        if depth_map is None:
            depth_map = defaultdict(int)
        data = {
            "id": str(self.id),
            "name": self.name,
            "dynamic": self.dynamic,
            "search_only": self.search_only,
            "items": sorted(
                [
                    item.serialize(depth_map, flat)
                    for item in self.list_items.all()
                    if flat or item.parent_id is None
                ],
                key=lambda item: item["sortorder"],
            ),
        }
        if hasattr(self, "node_ids"):
            data["nodes"] = [
                {
                    "id": node_id,
                    "name": node_name,
                    "nodegroup_id": nodegroup_id,
                    "graph_id": graph_id,
                    "graph_name": graph_name,
                }
                for node_id, node_name, nodegroup_id, graph_id, graph_name in zip(
                    self.node_ids,
                    self.node_names,
                    self.nodegroup_ids,
                    self.graph_ids,
                    self.graph_names,
                    strict=True,
                )
                if permitted_nodegroups is None or nodegroup_id in permitted_nodegroups
            ]
        else:
            nodes_using_list = NodeProxy.objects.with_controlled_lists().filter(
                controlled_list_id=self.pk, source_identifier=None
            )
            filtered_nodes = [
                node
                for node in nodes_using_list
                if permitted_nodegroups is None
                or node.nodegroup_id in permitted_nodegroups
            ]
            data["nodes"] = [
                {
                    "id": str(node.pk),
                    "name": node.name,
                    "nodegroup_id": node.nodegroup_id,
                    "graph_id": node.graph_id,
                    "graph_name": str(node.graph.name),
                }
                for node in filtered_nodes
            ]
        return data

    def bulk_update_item_parentage_and_order(self, parent_map, sortorder_map):
        """Item parentage and sortorder are updated together because their
        uniqueness is enforced together."""

        reordered_items = []
        exclude_fields = field_names(ListItem()) - {"sortorder", "parent_id"}
        for item_id, sortorder in sortorder_map.items():
            item = ListItem(pk=uuid.UUID(item_id), sortorder=sortorder)
            if item_id in parent_map:
                new_parent = parent_map[item_id]
                item.parent_id = uuid.UUID(new_parent) if new_parent else None
            item.list_id = self.pk
            item.clean_fields(exclude=exclude_fields)
            reordered_items.append(item)

        ListItem.objects.bulk_update(
            reordered_items, fields=["sortorder", "parent_id", "list_id"]
        )


class ListItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uri = models.URLField(max_length=2048, null=False, blank=True)
    list = models.ForeignKey(
        List,
        on_delete=models.CASCADE,
        related_name="list_items",
    )
    sortorder = models.IntegerField(validators=[MinValueValidator(0)])
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="children"
    )
    guide = models.BooleanField(default=False)

    objects = ListItemQuerySet.as_manager()

    class Meta:
        ordering = ["sortorder"]
        constraints = [
            # Sort order concerns the list as a whole, not subsets
            # of the hierarchy.
            models.UniqueConstraint(
                fields=["list", "sortorder"],
                name="unique_list_sortorder",
                deferrable=Deferrable.DEFERRED,
                violation_error_message=_(
                    "All items in this list must have distinct sort orders."
                ),
            ),
            models.UniqueConstraint(
                fields=["list", "uri"],
                name="unique_list_uri",
                violation_error_message=_(
                    "All items in this list must have distinct URIs."
                ),
            ),
        ]

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude=exclude)
        if not self.id and "id" not in exclude:
            id_field = [f for f in self._meta.fields if f.name == "id"][0]
            self.id = id_field.get_default()

    def clean(self):
        if not self.uri:
            self.uri = self.generate_uri()

    def generate_uri(self):
        """Similar logic exists in `etl_collections_to_controlled_lists` migration."""
        if not self.id:
            raise RuntimeError("URI generation attempted without a primary key.")

        parts = [settings.PUBLIC_SERVER_ADDRESS.rstrip("/")]
        if settings.FORCE_SCRIPT_NAME:
            parts.append(settings.FORCE_SCRIPT_NAME)
        parts += ["plugins", "controlled-list-manager", "item", str(self.id)]

        return "/".join(parts)

    def ensure_pref_label(self):
        if not self.list_item_values.filter(valuetype="prefLabel").exists():
            raise ValidationError(_("At least one preferred label is required."))

    def serialize(self, depth_map=None, flat=False):
        if depth_map is None:
            depth_map = defaultdict(int)
        if self.parent_id:
            depth_map[self.id] = depth_map[self.parent_id] + 1
        data = {
            "id": str(self.id),
            "list_id": str(self.list_id),
            "uri": self.uri,
            "sortorder": self.sortorder,
            "guide": self.guide,
            "values": [
                value.serialize()
                for value in self.list_item_values.all()
                if value.valuetype_id != "image"
            ],
            "images": [image.serialize() for image in self.list_item_images.all()],
            "parent_id": str(self.parent_id) if self.parent_id else None,
            "depth": depth_map[self.id],
        }
        if not flat:
            data["children"] = [
                child.serialize(depth_map, flat) for child in self.children.all()
            ]
        return data

    def build_tile_value(self):
        tile_value = {
            "uri": self.uri or self.generate_uri(),
            "labels": [label.serialize() for label in self.list_item_values.labels()],
            "list_id": str(self.list_id),
        }
        return tile_value

    def build_select_option(self):
        labels = getattr(self, "list_item_labels", self.list_item_values.labels())
        best_label = self.best_label_from_set(labels)
        data = {
            "list_item_id": str(self.id),
            "uri": self.uri,
            "list_item_values": [label.serialize() for label in labels],
            "display_value": best_label,
            "sortorder": self.sortorder,
        }
        data["children"] = [
            child.build_select_option() for child in self.children.all()
        ]
        return data

    @staticmethod
    def best_label_from_set(
        labels: Iterable["ListItemValue" | "ReferenceLabel"],
    ) -> str | None:
        ranked_labels = sorted(
            labels,
            key=lambda label: rank_label(
                kind=label.valuetype_id,
                source_lang=label.language_id,
                target_lang=translation.get_language(),
            ),
            reverse=True,
        )
        if not ranked_labels:
            return None
        return ranked_labels[0].value

    def best_label(self):
        return self.best_label_from_set(self.list_item_values.labels())


class ListItemValue(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    list_item = models.ForeignKey(
        ListItem,
        on_delete=models.CASCADE,
        related_name="list_item_values",
    )
    valuetype = models.ForeignKey(
        DValueType,
        on_delete=models.PROTECT,
        limit_choices_to=Q(category__in=("label", "image", "note")),
    )
    language = models.ForeignKey(
        Language,
        db_column="languageid",
        to_field="code",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    value = models.CharField(max_length=1024, null=False, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["list_item", "value", "valuetype", "language"],
                name="unique_item_value_valuetype_language",
                violation_error_message=_(
                    "The same item value cannot be stored twice in the same language."
                ),
            ),
            models.UniqueConstraint(
                fields=["list_item", "language"],
                condition=Q(valuetype="prefLabel"),
                name="unique_item_preflabel_language",
                violation_error_message=_(
                    "Only one preferred label per language is permitted."
                ),
            ),
            models.CheckConstraint(
                check=Q(language_id__isnull=False) | Q(valuetype="image"),
                name="only_images_nullable_language",
                violation_error_message=_(
                    "Item values must be associated with a language."
                ),
            ),
        ]

    objects = ListItemValueQuerySet.as_manager()

    def clean(self):
        if not self.value:
            self.value = _("New Item: ") + datetime.datetime.now().isoformat(
                sep=" ", timespec="seconds"
            )

    def serialize(self):
        return {
            "id": str(self.id),
            "valuetype_id": self.valuetype_id,
            "language_id": self.language_id,
            "value": self.value,
            "list_item_id": str(self.list_item_id),
        }

    def delete(self):
        with transaction.atomic():
            ret = super().delete()
            self.list_item.ensure_pref_label()
        return ret


class ListItemImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    list_item = models.ForeignKey(
        ListItem,
        on_delete=models.CASCADE,
        related_name="list_item_images",
    )
    valuetype = models.ForeignKey(
        DValueType, on_delete=models.PROTECT, limit_choices_to={"category": "image"}
    )
    language = models.ForeignKey(
        Language,
        db_column="languageid",
        to_field="code",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    value = models.FileField(upload_to="list_item_images")

    objects = ListItemImageManager()

    class Meta:
        managed = False
        db_table = "arches_controlled_lists_listitemvalue"

    def serialize(self):
        return {
            "id": str(self.id),
            "list_item_id": str(self.list_item_id),
            "url": self.value.url,
            "metadata": [
                metadata.serialize() for metadata in self.list_item_image_metadata.all()
            ],
        }


class ListItemImageMetadata(models.Model):
    class MetadataChoices(models.TextChoices):
        TITLE = "title", _("Title")
        DESCRIPTION = "desc", _("Description")
        ATTRIBUTION = "attr", _("Attribution")
        ALT_TEXT = "alt", _("Alternative text")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    list_item_image = models.ForeignKey(
        ListItemImage,
        on_delete=models.CASCADE,
        related_name="list_item_image_metadata",
    )
    language = models.ForeignKey(
        Language,
        db_column="languageid",
        to_field="code",
        on_delete=models.PROTECT,
    )
    metadata_type = models.CharField(max_length=5, choices=MetadataChoices.choices)
    value = models.CharField(max_length=2048)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["list_item_image", "metadata_type", "language"],
                name="unique_image_metadata_valuetype_language",
                violation_error_message=_(
                    "Only one metadata entry per language and metadata type is permitted."
                ),
            ),
        ]

    def serialize(self):
        choices = ListItemImageMetadata.MetadataChoices
        return {
            field: str(value)
            for (field, value) in vars(self).items()
            if not field.startswith("_")
        } | {
            # Get localized label for metadata type
            "metadata_label": str(choices(self.metadata_type).label)
        }


# Proxy models for tables managed by core arches
class NodeProxy(Node):
    objects = NodeQuerySet.as_manager()

    class Meta:
        proxy = True


from arches_controlled_lists.datatypes.datatypes import ReferenceLabel
