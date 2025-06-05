from functools import lru_cache, partial

from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db import models, transaction
from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError
from rest_framework import renderers
from rest_framework import serializers
from rest_framework.fields import empty

from arches import VERSION as arches_version
from arches.app.models.fields.i18n import I18n_JSON, I18n_String
from arches.app.models.models import Node
from arches.app.utils.betterJSONSerializer import JSONSerializer

from arches_querysets.models import AliasedData, SemanticResource, SemanticTile
from arches_querysets.rest_framework import interchange_fields


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
        # Does not check nodegroup permissions.
        if arches_version >= (8, 0):
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

    def get_value(self, dictionary):
        """Avoid the branch that treats MultiPart data input as HTML."""
        return dictionary.get(self.field_name, empty)

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

    def to_internal_value(self, data):
        attrs = super().to_internal_value(data)
        return AliasedData(**attrs)

    def validate(self, attrs):
        if hasattr(self, "initial_data") and (
            unknown_keys := set(self.initial_data) - set(self.fields)
        ):
            raise ValidationError({unknown_keys.pop(): "Unexpected field"})
        return attrs


class TileAliasedDataSerializer(serializers.ModelSerializer, NodeFetcherMixin):
    datatype_field_mapping = {
        "number": models.FloatField,
        "date": models.DateField,
        "boolean": models.BooleanField,
        "non-localized-string": models.CharField,
    }
    serializer_field_mapping = {
        **serializers.ModelSerializer.serializer_field_mapping,
        models.JSONField: interchange_fields.JSONField,
        models.FloatField: interchange_fields.FloatField,
        models.DateField: interchange_fields.DateField,
        models.BooleanField: interchange_fields.BooleanField,
        models.CharField: interchange_fields.CharField,
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

    # TODO: uncache this
    @staticmethod
    @lru_cache(maxsize=1)
    def get_nodegroup_aliases():
        return {
            node.pk: node.alias
            for node in Node.objects.filter(pk=models.F("nodegroup_id")).only("alias")
        }

    def get_value(self, dictionary):
        """Avoid the branch that treats MultiPart data input as HTML."""
        return dictionary.get(self.field_name, empty)

    def get_fields(self):
        nodegroup_alias = (
            # 1. From __init__()
            getattr(self, "_root_node", None)
            # 2. From Meta options
            or self.Meta.root_node
            # 3. From generic view
            or self.context.get("nodegroup_alias")
        )
        nodes_by_node_aliases = {node.alias: node for node in self.graph_nodes}
        try:
            self._root_node = nodes_by_node_aliases.get(nodegroup_alias)
        except KeyError:
            raise RuntimeError("missing root node")
        field_map = super().get_fields()

        if arches_version < (8, 0):
            nodegroup_aliases = self.get_nodegroup_aliases()

        # __all__ now includes one level of child nodegroups.
        # TODO: do all, or allow specifying a branch origin.
        if self.__class__.Meta.fields == "__all__":
            child_query = (
                self._root_node.nodegroup.children
                if arches_version >= (8, 0)
                else self._root_node.nodegroup.nodegroup_set
            )
            for child_nodegroup in child_query.all():
                if arches_version >= (8, 0):
                    child_nodegroup_alias = child_nodegroup.grouping_node.alias
                else:
                    child_nodegroup_alias = nodegroup_aliases[child_nodegroup.pk]
                self._child_nodegroup_aliases.append(child_nodegroup_alias)

                if (
                    child_nodegroup_alias in nodes_by_node_aliases
                    and child_nodegroup not in field_map
                ):
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

        if node.datatype == "semantic" and node.nodegroup.grouping_node == node:
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
            klass = self.datatype_field_mapping.get(node.datatype, models.JSONField)
            model_field = klass(null=True)
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
    tileid = serializers.UUIDField(validators=[], required=False, allow_null=True)
    resourceinstance = serializers.PrimaryKeyRelatedField(
        queryset=SemanticResource.objects.all(), required=False, html_cutoff=0
    )
    parenttile = serializers.PrimaryKeyRelatedField(
        queryset=SemanticTile.objects.all(),
        required=False,
        allow_null=True,
        html_cutoff=0,
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
            user=self.context["request"].user,
        )
        validated_data["nodegroup_id"] = qs._entry_node.nodegroup_id
        if validated_data.get("sortorder") is None:
            # Use a dummy instance to avoid save() and signals.
            dummy_instance = options.model(**validated_data)
            dummy_instance.sortorder = None
            dummy_instance.set_next_sort_order()
            validated_data["sortorder"] = dummy_instance.sortorder
        with transaction.atomic():
            created = super().create(validated_data)
        return created


class ArchesResourceSerializer(serializers.ModelSerializer, NodeFetcherMixin):
    # aliased_data is the only "virtual" field we need to add here, the rest
    # are inferred by serializers.ModelSerializer. We temporarily define
    # several fields here to set read_only=True until we can depend on Arches
    # 8.1 where the model fields set the equivalent editable=False.
    aliased_data = ResourceAliasedDataSerializer(required=False, allow_null=False)
    principaluser = serializers.PrimaryKeyRelatedField(
        allow_null=True,
        required=False,
        read_only=True,
    )
    name = serializers.JSONField(
        allow_null=True,
        required=False,
        read_only=True,
        encoder=JSONSerializer,
    )
    descriptors = serializers.JSONField(
        allow_null=True,
        required=False,
        read_only=True,
    )
    legacyid = serializers.PrimaryKeyRelatedField(
        allow_null=True,
        required=False,
        read_only=True,
    )
    graph_publication = serializers.PrimaryKeyRelatedField(
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
        if arches_version >= (8, 0) and field_name == "graph":
            ret[1]["queryset"] = ret[1]["queryset"].filter(
                slug=self.graph_slug, source_identifier=None
            )
        return ret

    def validate(self, attrs):
        """Infer the graph if missing from the request."""
        if (
            "graph" in self.fields
            and not attrs.get("graph_id")
            and not attrs.get("graph")
        ):
            attrs["graph_id"] = self.fields["graph"].queryset.first().pk
        return attrs

    def create(self, validated_data):
        options = self.__class__.Meta
        # TODO: we probably want a queryset method to do one-shot
        # creates with tile data
        with transaction.atomic():
            without_tile_data = validated_data.copy()
            without_tile_data.pop("aliased_data", None)
            # TODO: decide on "blank" interface.
            instance_without_tile_data = options.model.mro()[1](**without_tile_data)
            instance_without_tile_data.save()
            instance_from_factory = options.model.as_model(
                graph_slug=self.graph_slug,
                only=None,
                user=self.context["request"].user,
            ).get(pk=instance_without_tile_data.pk)
            instance_from_factory._as_representation = True
            # TODO: decide whether to override update() instead of using partial().
            instance_from_factory.save = partial(
                instance_from_factory.save, request=self.context["request"]
            )
            updated = self.update(instance_from_factory, validated_data)
        return updated
