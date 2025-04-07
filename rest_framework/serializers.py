from copy import deepcopy
from functools import lru_cache

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db import transaction
from django.db.models import fields, F
from django.db.models.fields.json import JSONField
from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError
from rest_framework import renderers
from rest_framework import serializers
from rest_framework.fields import empty

from arches import __version__ as arches_version
from arches.app.models.fields.i18n import I18n_JSON, I18n_String
from arches.app.models.models import Node
from arches.app.utils.betterJSONSerializer import JSONSerializer

from arches_querysets.models import AliasedData, SemanticResource, SemanticTile


# Workaround for I18n_string fields
renderers.JSONRenderer.encoder_class = JSONSerializer
renderers.JSONOpenAPIRenderer.encoder_class = JSONSerializer


def _make_tile_serializer(
    *, nodegroup_alias, cardinality, sortorder, slug, graph_nodes, nodes="__all__"
):
    class DynamicTileSerializer(ArchesTileSerializer):
        aliased_data = TileAliasedDataSerializer(
            required=False,
            allow_null=False,
            graph_nodes=graph_nodes,
            graph_slug=slug,
            root_node=nodegroup_alias,
        )

        class Meta:
            model = SemanticTile
            graph_slug = slug
            root_node = nodegroup_alias
            fields = nodes

    name = "_".join((slug.title(), nodegroup_alias.title(), "TileSerializer"))
    klass = type(name, (DynamicTileSerializer,), {})
    ret = klass(
        many=cardinality == "n",
        required=False,
        allow_null=True,
        graph_nodes=graph_nodes,
        style={"alias": nodegroup_alias, "sortorder": sortorder},
    )
    return ret


class NodeFetcherMixin:
    @property
    def graph_slug(self):
        return (
            # 1. From __init__(), e.g. TileAliasedDataSerializer
            getattr(self, "_graph_slug", None)
            # 2. From Meta options
            or self.__class__.Meta.graph_slug
            # 3. From generic view
            or self.context.get("graph_slug")
            # 4. From settings
            or getattr(settings, "SPECTACULAR_SETTINGS", {}).get(
                "GRAPH_SLUG_FOR_GENERIC_SERIALIZER"
            )
        )

    @property
    def graph_nodes(self):
        if not self._graph_nodes:
            self._graph_nodes = (
                self.context.get("graph_nodes") or self.find_graph_nodes()
            )
        return self._graph_nodes

    def find_graph_nodes(self):
        # This should really only be used when using drf-spectacular.
        if arches_version >= "8":
            return (
                Node.objects.filter(
                    graph__slug=self.graph_slug,
                    graph__source_identifier=None,
                    nodegroup__isnull=False,
                )
                .select_related("nodegroup")
                .prefetch_related(
                    "nodegroup__node_set",
                    "nodegroup__children",
                    "nodegroup__children__grouping_node",
                    "cardxnodexwidget_set",
                )
            )
        return (
            Node.objects.filter(
                graph__slug=self.graph_slug,
                nodegroup__isnull=False,
            )
            .select_related("nodegroup")
            .prefetch_related(
                "nodegroup__node_set",
                "nodegroup__nodegroup_set",
                "cardxnodexwidget_set",
            )
        )

    @property
    def nodegroup_alias(self):
        return self.context.get("nodegroup_alias")


class ResourceAliasedDataSerializer(serializers.Serializer, NodeFetcherMixin):
    class Meta:
        graph_slug = None
        nodegroups = "__all__"
        fields = "__all__"

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        self._graph_nodes = []
        self._root_node_aliases = []

    def __deepcopy__(self, memo):
        ret = super().__deepcopy__(memo)
        ret._graph_nodes = self._graph_nodes
        return ret

    def get_fields(self):
        field_map = super().get_fields()
        self._root_node_aliases = []
        options = self.__class__.Meta
        if options.nodegroups == "__all__":
            only = self.context.get("nodegroup_alias")
        else:
            only = options.nodegroups

        # Create serializers for top-level nodegroups.
        for node in self.graph_nodes:
            if (
                not node.nodegroup_id
                or node.nodegroup.parentnodegroup_id
                or not node.alias
            ):
                continue
            if only and node.nodegroup.grouping_node.alias not in only:
                continue
            if node.pk == node.nodegroup.pk:
                self._root_node_aliases.append(node.alias)
                if node.alias not in field_map:
                    sortorder = 0
                    if node.nodegroup.cardmodel_set.all():
                        sortorder = node.nodegroup.cardmodel_set.all()[0].sortorder
                    # TODO: check "fields" option in Meta for node level control.
                    field_map[node.alias] = _make_tile_serializer(
                        slug=self.graph_slug,
                        nodegroup_alias=node.alias,
                        cardinality=node.nodegroup.cardinality,
                        graph_nodes=self.graph_nodes,
                        sortorder=sortorder,
                    )

        return field_map

    def get_default_field_names(self, declared_fields, model_info):
        field_names = super().get_default_field_names(declared_fields, model_info)
        options = self.__class__.Meta
        if options.fields != "__all__":
            raise NotImplementedError  # TODO...
        if options.nodegroups == "__all__":
            field_names.extend(self._root_node_aliases)
        else:
            field_names.extend(options.nodegroups)
        return field_names


class TileAliasedDataSerializer(serializers.ModelSerializer, NodeFetcherMixin):
    datatype_field_map = {
        "string": JSONField(null=True),
        "number": fields.FloatField(null=True),
        "concept": JSONField(null=True),
        "concept-list": JSONField(null=True),
        "date": fields.DateField(null=True),
        "node-value": fields.CharField(null=True),  # XXX
        "edtf": fields.CharField(null=True),  # XXX
        "annotation": fields.CharField(null=True),  # XXX
        "url": JSONField(null=True),  # XXX
        "resource-instance": JSONField(null=True),
        "resource-instance-list": ArrayField(
            base_field=JSONField(null=True), null=True
        ),
        "boolean": fields.BooleanField(null=True),
        "domain-value": ArrayField(base_field=fields.UUIDField(null=True), null=True),
        "domain-value-list": ArrayField(
            base_field=fields.UUIDField(null=True), null=True
        ),
        "non-localized-string": fields.CharField(null=True),
        "geojson-feature-collection": fields.CharField(null=True),  # XXX
        "file-list": ArrayField(base_field=JSONField(null=True), null=True),
        "reference": ArrayField(base_field=JSONField(null=True), null=True),
    }

    class Meta:
        model = SemanticTile
        graph_slug = None
        # If None, supply by a route providing a <slug:nodegroup_alias> component
        root_node = None
        fields = "__all__"

    def __init__(self, instance=None, data=empty, **kwargs):
        self._graph_nodes = kwargs.pop("graph_nodes", [])
        self._graph_slug = kwargs.pop("graph_slug", None)
        self._root_node = kwargs.pop("root_node", None)
        super().__init__(instance, data, **kwargs)
        self._child_nodegroup_aliases = []

    def __deepcopy__(self, memo):
        ret = super().__deepcopy__(memo)
        ret._graph_nodes = self._graph_nodes
        return ret

    @staticmethod
    @lru_cache(maxsize=1)
    def get_nodegroup_aliases():
        # TODO: uncache this.
        return {
            node.pk: node.alias
            for node in Node.objects.filter(pk=F("nodegroup_id")).only("alias")
        }

    def get_fields(self):
        nodegroup_alias = (
            # 1. From __init__()
            getattr(self, "_root_node", None)
            # 2. From Meta options
            or self.Meta.root_node
            # 3. From generic view
            or self.context.get("nodegroup_alias")
        )
        for node in self.graph_nodes:
            if node.alias == nodegroup_alias:
                self._root_node = node
                break
        else:
            raise RuntimeError("missing root node")
        field_map = super().get_fields()

        if arches_version < "8":
            nodegroup_aliases = self.get_nodegroup_aliases()

        # __all__ now includes one level of child nodegroups.
        # TODO: do all, or allow specifying a branch origin.
        if self.__class__.Meta.fields == "__all__":
            child_query = (
                self._root_node.nodegroup.children
                if arches_version >= "8"
                else self._root_node.nodegroup.nodegroup_set
            )
            for child_nodegroup in child_query.all():
                if arches_version >= "8":
                    child_nodegroup_alias = child_nodegroup.grouping_node.alias
                else:
                    child_nodegroup_alias = nodegroup_aliases[child_nodegroup.pk]
                self._child_nodegroup_aliases.append(child_nodegroup_alias)

                if child_nodegroup_alias not in field_map:
                    sortorder = 0
                    if child_nodegroup.cardmodel_set.all():
                        sortorder = child_nodegroup.cardmodel_set.all()[0].sortorder
                    field_map[child_nodegroup_alias] = _make_tile_serializer(
                        nodegroup_alias=child_nodegroup_alias,
                        cardinality=child_nodegroup.cardinality,
                        slug=self.graph_slug,
                        graph_nodes=self.graph_nodes,
                        sortorder=sortorder,
                    )

        return field_map

    def get_default_field_names(self, declared_fields, model_info):
        field_names = []
        if self.__class__.Meta.fields == "__all__":
            for sibling_node in self._root_node.nodegroup.node_set.all():
                if sibling_node.datatype != "semantic":
                    field_names.append(sibling_node.alias)

        field_names.extend(self._child_nodegroup_aliases)
        return field_names

    def build_unknown_field(self, field_name, model_class):
        for node in self.graph_nodes:
            if node.alias == field_name:
                break
        else:
            raise Node.DoesNotExist(
                f"Node with alias {field_name} not found in graph {self.graph_slug}"
            )

        model_field = deepcopy(self.datatype_field_map[node.datatype])
        if model_field is None:
            if node.nodegroup.grouping_node == node:
                sortorder = 0
                if node.nodegroup.cardmodel_set.all():
                    sortorder = node.nodegroup.cardmodel_set.all()[0].sortorder
                model_field = _make_tile_serializer(
                    slug=self.graph_slug,
                    nodegroup_alias=node.alias,
                    cardinality=node.nodegroup.cardinality,
                    graph_nodes=self.graph_nodes,
                    sortorder=sortorder,
                )
            else:
                msg = _("Field missing for datatype: {}").format(node.datatype)
                raise NotImplementedError(msg)
        model_field.model = model_class
        model_field.blank = not node.isrequired
        try:
            cross = node.cardxnodexwidget_set.all()[0]
            label = cross.label
            visible = cross.visible
            config = cross.config
            sortorder = cross.sortorder or 0
        except (IndexError, ObjectDoesNotExist, MultipleObjectsReturned):
            label = I18n_String()
            visible = True
            config = I18n_JSON()
            sortorder = 0

        ret = self.build_standard_field(field_name, model_field)
        ret[1]["required"] = node.isrequired
        try:
            ret[1]["initial"] = config.serialize().get("defaultValue", {})
        except KeyError:
            pass
        try:
            ret[1]["help_text"] = config.serialize().get("placeholder", None)
        except KeyError:
            pass
        ret[1]["label"] = label.serialize()
        ret[1]["style"] = {
            "alias": node.alias,
            "visible": visible,
            "widget_config": config,
            "datatype": node.datatype,
            "sortorder": sortorder,
        }

        return ret

    def to_internal_value(self, data):
        attrs = super().to_internal_value(data)
        return AliasedData(**attrs)

    def validate(self, attrs):
        if hasattr(self, "initial_data") and (
            unknown_keys := set(self.initial_data) - set(self.fields)
        ):
            raise ValidationError({unknown_keys.pop(): "Unexpected field"})

        if validate_method := getattr(self, f"validate_{self._root_node.alias}", None):
            attrs = validate_method(attrs)

        return attrs


class ArchesTileSerializer(serializers.ModelSerializer, NodeFetcherMixin):
    tileid = serializers.UUIDField(validators=[], required=False)
    resourceinstance = serializers.PrimaryKeyRelatedField(
        queryset=SemanticResource.objects.all(), required=False, html_cutoff=0
    )
    parenttile = serializers.PrimaryKeyRelatedField(
        queryset=SemanticTile.objects.all(),
        required=False,
        allow_null=True,
        # Avoid queries to populate dropdowns in browsable API.
        # https://www.django-rest-framework.org/topics/browsable-api/#handling-choicefield-with-large-numbers-of-items
        style={"base_template": "input.html"},
    )
    aliased_data = TileAliasedDataSerializer(required=False, allow_null=False)

    class Meta:
        model = SemanticTile
        # If None, supply by a route providing a <slug:graph> component
        graph_slug = None
        # If None, supply by a route providing a <slug:nodegroup_alias> component
        root_node = None
        fields = "__all__"

    def __init__(self, instance=None, data=empty, **kwargs):
        self._graph_nodes = kwargs.pop("graph_nodes", [])
        super().__init__(instance, data, **kwargs)
        self._child_nodegroup_aliases = []

    def get_default_field_names(self, declared_fields, model_info):
        field_names = super().get_default_field_names(declared_fields, model_info)
        try:
            field_names.remove("data")
        except ValueError:
            pass
        return field_names

    def create(self, validated_data):
        options = self.__class__.Meta
        qs = options.model.as_nodegroup(
            self.nodegroup_alias,
            graph_slug=self.graph_slug,
            only=None,
            as_representation=True,
            allow_empty=True,
            user=self.context.get("request").user,
        )
        validated_data["nodegroup_id"] = qs._entry_node.nodegroup_id
        if validated_data.get("sortorder") is None:
            # Use a dummy instance to avoid save() and signals.
            dummy_instance = options.model(**validated_data)
            dummy_instance.sortorder = None
            dummy_instance.set_next_sort_order()
            validated_data["sortorder"] = dummy_instance.sortorder
        with transaction.atomic():
            blank_tile = super().create(validated_data)
            tile_from_factory = qs.get(pk=blank_tile.pk)
            updated = self.update(tile_from_factory, validated_data)
        return updated


class ArchesResourceSerializer(serializers.ModelSerializer, NodeFetcherMixin):
    aliased_data = ResourceAliasedDataSerializer(required=False, allow_null=False)
    # Until dropping support for Arches 7.6, we need to explicitly set read_only=True
    principaluser = serializers.PrimaryKeyRelatedField(
        allow_null=True,
        required=False,
        read_only=True,
    )

    class Meta:
        model = SemanticResource
        # If None, supply by a route providing a <slug:graph> component
        graph_slug = None
        nodegroups = "__all__"
        fields = "__all__"

    def build_relational_field(self, field_name, relation_info):
        ret = super().build_relational_field(field_name, relation_info)
        if arches_version >= "8" and field_name == "graph":
            ret[1]["queryset"] = ret[1]["queryset"].filter(
                graphmodel__slug=self.graph_slug
            )
        return ret

    def validate(self, attrs):
        if hasattr(self, "initial_data") and (
            unknown_keys := set(self.initial_data) - set(self.fields)
        ):
            raise ValidationError({unknown_keys.pop(): "Unexpected field"})
        # TODO: this probably doesn't belong here or needed anymore.
        if "graph" in self.fields and not attrs.get("graph_id"):
            attrs["graph_id"] = self.fields["graph"].queryset.first().pk
        return attrs

    def create(self, validated_data):
        options = self.__class__.Meta
        # TODO: we probably want a queryset method to do one-shot
        # creates with tile data
        with transaction.atomic():
            instance_without_tile_data = super().create(validated_data)
            instance_from_factory = options.model.as_model(
                graph_slug=self.graph_slug,
                only=None,
            ).get(pk=instance_without_tile_data.pk)
            instance_from_factory._as_representation = True
            updated = self.update(instance_from_factory, validated_data)
        return updated
