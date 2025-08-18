from collections import defaultdict
from functools import partial

from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db import models
from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError
from rest_framework import renderers
from rest_framework import serializers
from rest_framework.fields import empty

from arches import VERSION as arches_version
from arches.app.models.fields.i18n import I18n_JSON, I18n_String
from arches.app.models.models import EditLog, GraphModel, Node, NodeGroup
from arches.app.models.resource import Resource
from arches.app.utils.betterJSONSerializer import JSONSerializer

from arches_querysets.datatypes.datatypes import DataTypeFactory
from arches_querysets.models import AliasedData, ResourceTileTree, TileTree
from arches_querysets.utils.models import ensure_request
from arches_querysets.rest_framework.field_mixins import NodeValueMixin
from arches_querysets.rest_framework.utils import get_nodegroup_alias_lookup


def _make_tile_serializer(
    *,
    nodegroup_alias,
    cardinality,
    sortorder,
    slug,
    graph_nodes,
    request,
    nodegroup_alias_lookup=None,
    nodes="__all__",
    exclude_children=False,
) -> type["ArchesTileSerializer"]:
    """
    DRF encourages a declarative programming style with classes. You, as
    the project implementer, can follow that style if you wish, but we've
    put some effort toward hiding this complexity from you by generating
    classes on the fly by default.
    """
    init_kwargs = {
        "required": False,
        "allow_null": False,
        "graph_nodes": graph_nodes,
        "graph_slug": slug,
        "root_node": nodegroup_alias,
        "nodegroup_alias_lookup": nodegroup_alias_lookup,
    }

    single_serializer = SingleNodegroupAliasedDataSerializer(**init_kwargs)
    multi_serializer = TileAliasedDataSerializer(**init_kwargs)

    class DynamicTileSerializer(ArchesTileSerializer):
        aliased_data = single_serializer if exclude_children else multi_serializer

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
        graph_nodes=graph_nodes,
        nodegroup_alias_lookup=nodegroup_alias_lookup,
        style={"alias": nodegroup_alias, "sortorder": sortorder},
        request=request,
    )


def _wrap_serializer_field(serializer_field_class) -> type:
    """
    Ensure every serializer field in DRF's serializer_field_mapping
    resolves to one of *our* serializer fields with overrides handling
    node_value wrapping and unwrapping.
    """
    return type(
        serializer_field_class.__name__,
        (NodeValueMixin, serializer_field_class),
        {},
    )


def _handle_nested_aliased_data(data, *, fields_map) -> AliasedData:
    all_data = AliasedData(**data)
    for field_name, serializer in fields_map.items():
        field_data = getattr(all_data, field_name, None)
        if isinstance(serializer, ArchesTileSerializer) or (
            isinstance(serializer, serializers.ListSerializer)
            and isinstance(serializer.child, ArchesTileSerializer)
        ):
            serializer.initial_data = field_data
            # Later: could look into batching these exceptions up.
            serializer.is_valid(raise_exception=True)
            if serializer.validated_data:
                if getattr(serializer, "many", False):
                    tile_or_tiles = [
                        TileTree(**data) for data in serializer.validated_data
                    ]
                else:
                    tile_or_tiles = TileTree(**serializer.validated_data)
                setattr(all_data, field_name, tile_or_tiles)
        else:
            setattr(all_data, field_name, serializer.to_internal_value(field_data))
    return all_data


class NodeFetcherMixin:
    @property
    def graph_slug(self):
        return (
            # 1. From __init__(), e.g. TileAliasedDataSerializer
            getattr(self, "_graph_slug", None)
            # 2. From Meta options
            or self.Meta.graph_slug
            # 3. From generic view
            or self.context.get("graph_slug")
            # 4. From settings
            or getattr(settings, "SPECTACULAR_SETTINGS", {}).get(
                "GRAPH_SLUG_FOR_GENERIC_SERIALIZER"
            )
        )

    @graph_slug.setter
    def graph_slug(self, value):
        self._graph_slug = value

    @property
    def graph_nodes(self):
        if not self._graph_nodes:
            graph_nodes = []
            if getattr(self, "parent", None) and isinstance(
                self.parent, NodeFetcherMixin
            ):
                graph_nodes = self.parent.graph_nodes
            if not graph_nodes:
                graph_nodes = self._find_graph_nodes()
            self._graph_nodes = graph_nodes
        return self._graph_nodes

    @graph_nodes.setter
    def graph_nodes(self, value):
        self._graph_nodes = value

    def _find_graph_nodes(self):
        node_filters = models.Q(graph__slug=self.graph_slug, nodegroup__isnull=False)
        children = "nodegroup_set"
        # arches_version==9.0.0
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

    def ensure_context(
        self,
        *,
        graph_slug,
        graph_nodes,
        nodegroup_alias=None,
        nodegroup_alias_lookup=None,
        request=None,
    ):
        """The view provides a context, so this is mainly here for script usage."""
        return {
            "graph_slug": graph_slug,
            "graph_nodes": graph_nodes,
            "nodegroup_alias": nodegroup_alias,
            "nodegroup_alias_lookup": nodegroup_alias_lookup
            or get_nodegroup_alias_lookup(graph_slug),
            "request": ensure_request(request),
        }


class ResourceAliasedDataSerializer(serializers.Serializer, NodeFetcherMixin):
    class Meta:
        graph_slug = None
        nodegroups = "__all__"
        fields = "__all__"
        exclude_children = False

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.graph_nodes = kwargs.pop("graph_nodes", [])
        self._root_node_aliases = []

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
            profile = self.context["request"].user.userprofile
            if (
                not node.nodegroup_id
                # arches_version==9.0.0 replace cached_viewable_nodegroups with viewable_nodegroups
                or str(node.nodegroup_id) not in profile.cached_viewable_nodegroups
                or node.nodegroup.parentnodegroup_id
                or not node.alias  # arches_version==9.0.0: remove `or not node.alias`
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
                        nodegroup_alias_lookup=self.context["nodegroup_alias_lookup"],
                        sortorder=sortorder,
                        exclude_children=options.exclude_children,
                        request=self.context["request"],
                    )

        return field_map

    def get_default_field_names(self, declared_fields, model_info):
        field_names = super().get_default_field_names(declared_fields, model_info)
        if self.Meta.fields != "__all__":
            raise NotImplementedError  # TODO...
        if self.Meta.nodegroups == "__all__":
            field_names.extend(self._root_node_aliases)
        else:
            field_names.extend(self.Meta.nodegroups)
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


class ResourceTopNodegroupsAliasedDataSerializer(ResourceAliasedDataSerializer):
    class Meta:
        graph_slug = None
        nodegroups = "__all__"
        fields = "__all__"
        exclude_children = True


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
        exclude_children = False

    def __init__(self, instance=None, data=empty, **kwargs):
        self.graph_slug = kwargs.pop("graph_slug", None)
        self.graph_nodes = kwargs.pop("graph_nodes", [])
        self._nodegroup_alias_lookup = kwargs.pop("nodegroup_alias_lookup", {})
        self._root_node = kwargs.pop("root_node", None)
        super().__init__(instance, data, **kwargs)
        self._child_nodegroup_aliases = []
        if not self.url_field_name:
            # Avoid cryptic errors in case a node alias collides with
            # DRF's default URL field name ("url")
            self.url_field_name = "__nonexistent__"

    def __deepcopy__(self, memo):
        ret = super().__deepcopy__(memo)
        ret._graph_slug = self._graph_slug
        ret._graph_nodes = self._graph_nodes
        return ret

    @classmethod
    def register_custom_datatype_field(cls, model_field, serializer_field):
        cls.serializer_field_mapping[model_field] = _wrap_serializer_field(
            serializer_field
        )

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
        profile = self.context["request"].user.userprofile
        # arches_version==9.0.0: cached_viewable_nodegroups -> viewable_nodegroups
        if str(self._root_node.nodegroup_id) not in profile.cached_viewable_nodegroups:
            raise PermissionError

        field_map = super().get_fields()
        self.finalize_initial_values(field_map)

        # __all__ includes children as well.
        if self.Meta.fields == "__all__" and not self.Meta.exclude_children:
            child_query = (
                self._root_node.nodegroup.children
                # arches_version==9.0.0
                if arches_version >= (8, 0)
                else self._root_node.nodegroup.nodegroup_set
            )
            flat_node_lookup = {node.pk: node for node in self.context["graph_nodes"]}
            for child_nodegroup in child_query.all():
                # arches_version==9.0.0: cached_viewable_nodegroups -> viewable_nodegroups
                if str(child_nodegroup.pk) not in profile.cached_viewable_nodegroups:
                    continue
                child_nodegroup_alias = self.context["nodegroup_alias_lookup"][
                    child_nodegroup.pk
                ]
                self._child_nodegroup_aliases.append(child_nodegroup_alias)
                child_nodegroup = flat_node_lookup[child_nodegroup.pk].nodegroup

                if (
                    child_nodegroup_alias in nodes_by_node_aliases
                    and child_nodegroup not in field_map
                ):
                    sortorder = 0
                    if child_nodegroup.cardmodel_set.all():
                        sortorder = child_nodegroup.cardmodel_set.all()[0].sortorder
                    field_map[child_nodegroup_alias] = _make_tile_serializer(
                        nodegroup_alias=child_nodegroup_alias,
                        nodegroup_alias_lookup=self.context["nodegroup_alias_lookup"],
                        cardinality=child_nodegroup.cardinality,
                        slug=self.graph_slug,
                        graph_nodes=self.graph_nodes,
                        sortorder=sortorder,
                        request=self.context["request"],
                    )

        return field_map

    def get_default_field_names(self, declared_fields, model_info):
        field_names = []
        if self.Meta.fields == "__all__":
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

        # arches_version==9.0.0: cached_viewable_nodegroups -> viewable_nodegroups
        if (
            node.datatype == "semantic"
            and node.nodegroup.grouping_node == node
            and str(node.nodegroup_id)
            in self.context["request"].user.userprofile.cached_viewable_nodegroups
        ):
            sortorder = 0
            if node.nodegroup.cardmodel_set.all():
                sortorder = node.nodegroup.cardmodel_set.all()[0].sortorder
            model_field = _make_tile_serializer(
                slug=self.graph_slug,
                nodegroup_alias=node.alias,
                cardinality=node.nodegroup.cardinality,
                graph_nodes=self.graph_nodes,
                sortorder=sortorder,
                request=self.context["request"],
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
        # Default value finalized (in bulk) via finalize_initial_values().
        ret[1]["initial"] = TileTree.get_default_value(node)

        return ret

    def finalize_initial_values(self, field_map):
        """Get display values for initial values in bulk if possible."""
        nodes_by_alias = {node.alias: node for node in self.graph_nodes}

        values_by_datatype = defaultdict(list)
        for field_name, field in field_map.items():
            node = nodes_by_alias[field_name]
            values_by_datatype[node.datatype].append(field.initial)

        datatype_contexts = {}
        # Get datatype context querysets per serializer (globally would be better.)
        # Also note this is copied in TileTreeQuerySet._set_aliased_data()
        for datatype, values in values_by_datatype.items():
            datatype_instance = DataTypeFactory().get_instance(datatype)
            bulk_values = datatype_instance.get_display_value_context_in_bulk(values)
            datatype_instance.set_display_value_context_in_bulk(bulk_values)
            datatype_contexts[datatype] = bulk_values

        for field_name, field in field_map.items():
            node = nodes_by_alias[field_name]
            default_val = field.initial
            # It's a little roundabout to instantiate a tile like this, but the underlying
            # methods expect tiles in case there are provisional edits there.
            dummy_tile = TileTree(data={str(node.pk): default_val})
            pair = dummy_tile.get_value_with_context(
                node, node_value=default_val, datatype_contexts=datatype_contexts
            )
            field.initial = pair

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


class SingleNodegroupAliasedDataSerializer(TileAliasedDataSerializer):
    class Meta:
        model = TileTree
        graph_slug = None
        # If None, supply by a route providing a <slug:nodegroup_alias> component
        root_node = None
        fields = "__all__"
        exclude_children = True


class ArchesTileSerializer(serializers.ModelSerializer, NodeFetcherMixin):
    # These fields are declared here in full instead of massaged via
    # "extra_kwargs" in class Meta to support subclassing by TileAliasedDataSerializer.
    tileid = serializers.UUIDField(validators=[], required=False, allow_null=True)
    resourceinstance = serializers.PrimaryKeyRelatedField(
        queryset=ResourceTileTree.objects.all(),
        required=False,
        allow_null=True,
        html_cutoff=0,
    )
    nodegroup = serializers.PrimaryKeyRelatedField(
        queryset=NodeGroup.objects.all(), required=False, allow_null=True, html_cutoff=0
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

    def __init__(self, instance=None, data=empty, *, context=None, **kwargs):
        # TODO(next): reduce number of paths through this code
        self._graph_slug = kwargs.pop(
            "graph_slug", context.get("graph_slug", None) if context else None
        )
        self._graph_nodes = kwargs.pop(
            "graph_nodes", context.get("graph_nodes", None) if context else None
        )
        if not context:
            context = self.ensure_context(
                graph_slug=self.graph_slug,
                graph_nodes=self.graph_nodes,
                nodegroup_alias=kwargs.pop("nodegroup_alias", None),
                nodegroup_alias_lookup=kwargs.pop("nodegroup_alias_lookup", {}),
                request=kwargs.pop("request", None),
            )
        kwargs["context"] = context
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

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)
        # arches_version==9.0.0
        if arches_version < (8, 0):
            # Simulate field default provided by Arches 8+.
            ret["data"] = {}
        return ret

    def get_default_field_names(self, declared_fields, model_info):
        field_names = super().get_default_field_names(declared_fields, model_info)
        try:
            field_names.remove("data")
        except ValueError:
            pass
        return field_names

    def create(self, validated_data):
        # Provide some additional context to TileTree.__init__()
        validated_data["__request"] = self.context["request"]
        validated_data["__as_representation"] = True
        graph_filters = models.Q(slug=self.graph_slug)
        # arches_version==9.0.0
        if arches_version >= (8, 0):
            graph_filters &= models.Q(source_identifier=None)
        graph = (
            GraphModel.objects.filter(graph_filters)
            .annotate(
                entry_nodegroup_id=NodeGroup.objects.filter(
                    node__graph=models.OuterRef("pk"),
                    node__alias=self.nodegroup_alias,
                ).values("pk")[:1]
            )
            .get()
        )
        resource, resource_created = self.create_resource_if_missing(
            validated_data, graph
        )
        validated_data["nodegroup_id"] = graph.entry_nodegroup_id
        try:
            created = super().create(validated_data)
        except:
            if resource_created:
                # Manually manage failures instead of using transaction.atomic(), see:
                # https://github.com/archesproject/arches/issues/12318
                # Don't want to run model delete() which *creates* edit log entries.
                EditLog.objects.filter(resourceinstanceid=resource.pk).delete()
                Resource.objects.filter(pk=resource.pk).delete()
            raise
        return created

    def create_resource_if_missing(self, validated_data, graph):
        if instance := validated_data.get("resourceinstance"):
            return instance, False
        # Would like to do the following, but we don't yet have a ResourceTileTree.save()
        # method handling a fast path for empty creates:
        # ResourceSubclass = self.fields["resourceinstance"].queryset.model
        # So hardcode the Resource(Proxy)Model for now.
        instance = Resource(graph=graph)
        instance.save(request=validated_data["__request"])
        validated_data["resourceinstance"] = instance
        return instance, True


class ArchesSingleNodegroupSerializer(ArchesTileSerializer):
    aliased_data = SingleNodegroupAliasedDataSerializer(
        required=False, allow_null=False
    )


class ArchesResourceSerializer(serializers.ModelSerializer, NodeFetcherMixin):
    # aliased_data is a virtual field not inferred by serializers.ModelSerializer.
    aliased_data = ResourceAliasedDataSerializer(required=False, allow_null=False)

    # Custom read-only fields.
    graph_has_different_publication = serializers.SerializerMethodField()

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
            "resourceinstanceid": {"initial": None, "allow_null": True},
            "graph": {"allow_null": True},
        }

    def __init__(
        self,
        *args,
        graph_slug=None,
        graph_nodes=None,
        nodegroup_alias_lookup=None,
        context=None,
        **kwargs,
    ):
        self._graph_slug = graph_slug
        # TODO(next): simplify supplying context
        self._graph_nodes = graph_nodes or (context or {}).get("graph_nodes") or []
        if not context:
            context = self.ensure_context(
                graph_slug=self.graph_slug,
                graph_nodes=self.graph_nodes,
                nodegroup_alias_lookup=nodegroup_alias_lookup or {},
                request=kwargs.pop("request", None),
            )
        kwargs["context"] = context
        super().__init__(*args, **kwargs)

    def build_relational_field(self, field_name, relation_info):
        ret = super().build_relational_field(field_name, relation_info)
        # arches_version==9.0.0
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
        # TODO: we probably want a queryset method to do one-shot
        # creates with tile data
        without_tile_data = validated_data.copy()
        without_tile_data.pop("aliased_data", None)
        # TODO: decide on "blank" interface.
        instance_without_tile_data = self.Meta.model.mro()[1](**without_tile_data)
        instance_without_tile_data.save()
        instance_from_factory = self.Meta.model.get_tiles(
            graph_slug=self.graph_slug,
            as_representation=True,
        ).get(pk=instance_without_tile_data.pk)
        # TODO: decide whether to override update() instead of using partial().
        instance_from_factory.save = partial(
            instance_from_factory.save, request=self.context["request"]
        )
        try:
            updated = self.update(instance_from_factory, validated_data)
        except:
            # Manually manage failures instead of using transaction.atomic(), see
            # https://github.com/archesproject/arches/issues/12318
            EditLog.objects.filter(resourceinstanceid=instance_from_factory.pk).delete()
            Resource.objects.filter(pk=instance_from_factory.pk).delete()
            raise
        return updated

    def get_graph_has_different_publication(self, obj):
        # arches_version==9.0.0
        if arches_version < (8, 0):
            return False
        return obj.graph_publication_id and (
            obj.graph_publication_id != obj.graph.publication_id
        )


class ArchesResourceTopNodegroupsSerializer(ArchesResourceSerializer):
    aliased_data = ResourceTopNodegroupsAliasedDataSerializer(
        required=False, allow_null=False
    )


# Workaround for I18n_string fields
renderers.JSONRenderer.encoder_class = JSONSerializer
renderers.JSONOpenAPIRenderer.encoder_class = JSONSerializer
