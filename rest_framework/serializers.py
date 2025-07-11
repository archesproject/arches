import uuid
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
from arches.app.models.models import Node, NodeGroup
from arches.app.utils.betterJSONSerializer import JSONSerializer

from arches_querysets.datatypes.datatypes import DataTypeFactory
from arches_querysets.models import AliasedData, ResourceTileTree, TileTree
from arches_querysets.rest_framework import interchange_mixin


def _make_tile_serializer(
    *, nodegroup_alias, cardinality, sortorder, slug, permitted_nodes, nodes="__all__"
) -> type["ArchesTileSerializer"]:
    """
    DRF encourages a declarative programming style with classes. You, as
    the project implementer, can follow that style if you wish, but we've
    put some effort toward hiding this complexity from you by generating
    classes on the fly by default.
    """

    class DynamicTileSerializer(ArchesTileSerializer):
        aliased_data = TileAliasedDataSerializer(
            required=False,
            allow_null=False,
            permitted_nodes=permitted_nodes,
            graph_slug=slug,
            root_node=nodegroup_alias,
        )

        class Meta:
            model = TileTree
            graph_slug = slug
            root_node = nodegroup_alias
            fields = nodes

    name = "_".join((slug.title(), nodegroup_alias.title(), "TileSerializer"))
    serializer_class = type(name, (DynamicTileSerializer,), {})
    return serializer_class(
        many=cardinality == "n",
        required=False,
        allow_null=True,
        graph_slug=slug,
        permitted_nodes=permitted_nodes,
        style={"alias": nodegroup_alias, "sortorder": sortorder},
    )


def _wrap_serializer_field(serializer_field_class) -> type:
    """
    Ensure every serializer field in DRF's serializer_field_mapping
    resolves to one of *our* serializer fields with overrides handling
    interchange_value wrapping and unwrapping.
    """
    return type(
        serializer_field_class.__name__,
        (interchange_mixin.InterchangeValueMixin, serializer_field_class),
        {},
    )


def _handle_nested_aliased_data(data, *, fields_map) -> AliasedData:
    all_data = AliasedData(**data)
    for field_name, tile_serializer in fields_map.items():
        if not isinstance(tile_serializer, ArchesTileSerializer):
            continue
        field_data = getattr(all_data, field_name, None)
        tile_serializer.initial_data = field_data
        # Later: could look into batching these exceptions up.
        tile_serializer.is_valid(raise_exception=True)
        if tile_serializer.validated_data:
            if getattr(tile_serializer, "many", False):
                tile_or_tiles = [
                    TileTree(**data) for data in tile_serializer.validated_data
                ]
            else:
                tile_or_tiles = TileTree(**tile_serializer.validated_data)
            setattr(all_data, field_name, tile_or_tiles)
    return all_data


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
    def permitted_nodes(self):
        if not self._permitted_nodes:
            self._permitted_nodes = (
                self.context.get("permitted_nodes") or self._find_permitted_nodes()
            )
        return self._permitted_nodes

    def _find_permitted_nodes(self):
        node_filters = models.Q(
            graph__slug=self.graph_slug,
            nodegroup__isnull=False,
            nodegroup__in=self.context["request"].user.userprofile.editable_nodegroups,
        )
        children = "nodegroup_set"
        if arches_version >= (8, 0):
            node_filters &= models.Q(source_identifier=None)
            children = "children"

        return (
            Node.objects.filter(node_filters)
            .select_related("nodegroup")
            .prefetch_related(
                "nodegroup__node_set",
                "nodegroup__cardmodel_set",
                f"nodegroup__{children}",
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
        self._permitted_nodes = []
        self._root_node_aliases = []

    def __deepcopy__(self, memo):
        ret = super().__deepcopy__(memo)
        ret._permitted_nodes = self._permitted_nodes
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
        for node in self.permitted_nodes:
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
                        permitted_nodes=self.permitted_nodes,
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
        """Make nested aliased data writable."""
        self.initial_data = data
        return _handle_nested_aliased_data(data, fields_map=self.fields)

    def validate(self, attrs):
        aliased_data = attrs  # thanks to to_internal_value().
        if unknown_keys := set(vars(aliased_data)) - set(self.fields):
            raise ValidationError({unknown_keys.pop(): "Unexpected field"})
        return attrs


class TileAliasedDataSerializer(serializers.ModelSerializer, NodeFetcherMixin):
    serializer_field_mapping = {
        model_field: _wrap_serializer_field(serializer_field)
        for model_field, serializer_field in serializers.ModelSerializer.serializer_field_mapping.items()
    }

    class Meta:
        model = TileTree
        graph_slug = None
        # If None, supply by a route providing a <slug:nodegroup_alias> component
        root_node = None
        fields = "__all__"

    def __init__(self, instance=None, data=empty, **kwargs):
        self._permitted_nodes = kwargs.pop("permitted_nodes", [])
        self._graph_slug = kwargs.pop("graph_slug", None)
        self._root_node = kwargs.pop("root_node", None)
        super().__init__(instance, data, **kwargs)
        self._child_nodegroup_aliases = []
        if not self.url_field_name:
            # Avoid cryptic errors in case a node alias collides with
            # DRF's default URL field name ("url")
            self.url_field_name = "__nonexistent__"

    def __deepcopy__(self, memo):
        ret = super().__deepcopy__(memo)
        ret._permitted_nodes = self._permitted_nodes
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
        nodes_by_node_aliases = {node.alias: node for node in self.permitted_nodes}
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
                        permitted_nodes=self.permitted_nodes,
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
        for node in self.permitted_nodes:
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
                permitted_nodes=self.permitted_nodes,
                sortorder=sortorder,
            )
        else:
            dt_instance = DataTypeFactory().get_instance(node.datatype)
            model_field = DataTypeFactory.get_model_field(dt_instance)
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
        ret[1]["help_text"] = config.serialize().get("placeholder")
        ret[1]["label"] = label.serialize()
        ret[1]["style"] = {
            "alias": node.alias,
            "visible": visible,
            "widget_config": config,
            "datatype": node.datatype,
            "sortorder": sortorder,
        }

        # Stock default value.
        default_val = TileTree.get_default_value(node)
        # It's a little roundabout to instantiate a tile like this, but the underlying
        # methods expect tiles in case there are provisional edits there.
        dummy_tile = TileTree(data={str(node.pk): default_val})
        pair = dummy_tile.get_display_interchange_pair(node, node_value=default_val)
        ret[1]["initial"] = pair

        return ret

    def to_internal_value(self, data):
        """Make nested aliased data writable."""
        self.initial_data = data
        return _handle_nested_aliased_data(data, fields_map=self.fields)

    def validate(self, attrs):
        aliased_data = attrs  # thanks to to_internal_value().
        if unknown_keys := set(vars(aliased_data)) - set(self.fields):
            raise ValidationError({unknown_keys.pop(): "Unexpected field"})

        if validate_method := getattr(
            self.root, f"validate_{self._root_node.alias}", None
        ):
            attrs = validate_method(attrs, initial_tile_data=self.parent.initial_data)

        return attrs


class ArchesTileSerializer(serializers.ModelSerializer, NodeFetcherMixin):
    # These fields are declared here in full instead of massaged via
    # "extra_kwargs" in class Meta to support subclassing by TileAliasedDataSerializer.
    tileid = serializers.UUIDField(validators=[], required=False, allow_null=True)
    resourceinstance = serializers.PrimaryKeyRelatedField(
        queryset=ResourceTileTree.objects.all(), required=False, html_cutoff=0
    )
    nodegroup = serializers.PrimaryKeyRelatedField(
        queryset=NodeGroup.objects.all(), required=False, html_cutoff=0
    )
    parenttile = serializers.PrimaryKeyRelatedField(
        queryset=TileTree.objects.prefetch_related(None),
        required=False,
        allow_null=True,
        html_cutoff=0,
    )
    aliased_data = TileAliasedDataSerializer(required=False, allow_null=False)

    class Meta:
        model = TileTree
        # If None, supply by a route providing a <slug:graph> component
        graph_slug = None
        # If None, supply by a route providing a <slug:nodegroup_alias> component
        root_node = None
        fields = "__all__"

    def __init__(self, instance=None, data=empty, **kwargs):
        self._graph_slug = kwargs.pop("graph_slug", None)
        self._permitted_nodes = kwargs.pop("permitted_nodes", [])
        super().__init__(instance, data, **kwargs)
        self._child_nodegroup_aliases = []

    def to_representation(self, data):
        """Prevent newly minted blank tiles from serializing with pk's."""
        ret = super().to_representation(data)
        if isinstance(data, TileTree):
            if data._state.adding:
                ret["tileid"] = None
                ret["parenttile"] = None
        return ret

    def get_default_field_names(self, declared_fields, model_info):
        field_names = super().get_default_field_names(declared_fields, model_info)
        try:
            field_names.remove("data")
        except ValueError:
            pass
        return field_names

    def create(self, validated_data):
        options = self.__class__.Meta
        qs = options.model.get_tiles(
            graph_slug=self.graph_slug,
            nodegroup_alias=self.nodegroup_alias,
            only=None,
            as_representation=True,
            user=self.context["request"].user,
        )
        validated_data["nodegroup_id"] = qs._entry_node.nodegroup_id
        if arches_version < (8, 0):
            validated_data["data"] = {}
        validated_data["__request"] = self.context["request"]
        validated_data["__as_representation"] = True
        with transaction.atomic():
            created = super().create(validated_data)
        return created


class ArchesResourceSerializer(serializers.ModelSerializer, NodeFetcherMixin):
    # aliased_data is a virtual field not inferred by serializers.ModelSerializer.
    aliased_data = ResourceAliasedDataSerializer(required=False, allow_null=False)

    class Meta:
        model = ResourceTileTree
        # If None, supply by a route providing a <slug:graph> component
        graph_slug = None
        nodegroups = "__all__"
        fields = "__all__"
        # TODO (arches_version): when Arches 8.1 is the lowest supported version,
        # read_only_fields can be removed, since at that point we can depend on
        # the equivalent editable=False on the model fields (done in 8.1).
        read_only_fields = (
            "principaluser",
            "name",
            "descriptors",
            "legacyid",
            "graph_publication",
            "resource_instance_lifecycle_state",
        )
        extra_kwargs = {
            "resourceinstanceid": {"initial": uuid.uuid4, "allow_null": True},
            "graph": {"allow_null": True},
        }

    def __init__(self, *args, graph_slug=None, permitted_nodes=None, **kwargs):
        if not kwargs.get("context"):
            # The view provides a context, so this is mainly here for CLI usage.
            self.parent = None
            context = {
                "graph_slug": graph_slug,
                "permitted_nodes": permitted_nodes or self.find_permitted_nodes(),
            }
            kwargs = {**kwargs, "context": context}

        super().__init__(*args, **kwargs)

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
            instance_from_factory = options.model.get_tiles(
                graph_slug=self.graph_slug,
                only=None,
                as_representation=True,
                user=self.context["request"].user,
            ).get(pk=instance_without_tile_data.pk)
            # TODO: decide whether to override update() instead of using partial().
            instance_from_factory.save = partial(
                instance_from_factory.save, request=self.context["request"]
            )
            updated = self.update(instance_from_factory, validated_data)
        return updated


# Workaround for I18n_string fields
renderers.JSONRenderer.encoder_class = JSONSerializer
renderers.JSONOpenAPIRenderer.encoder_class = JSONSerializer
