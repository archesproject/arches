from copy import deepcopy

from django.db.models import F
from rest_framework import fields
from rest_framework import renderers
from rest_framework import serializers

from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models.models import Node, TileModel
from arches.app.utils.betterJSONSerializer import JSONSerializer


# Workaround for I18n_string fields
renderers.JSONRenderer.encoder_class = JSONSerializer
renderers.JSONOpenAPIRenderer.encoder_class = JSONSerializer


class ArchesTileSerializer(serializers.ModelSerializer):
    tileid = serializers.UUIDField(validators=[], required=False)

    def __init__(self, instance=None, data=fields.empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        self._nodes = Node.objects.none()
        self._root_node = None

    def get_default_field_names(self, declared_fields, model_info):
        field_names = super().get_default_field_names(declared_fields, model_info)
        try:
            field_names.remove("data")
        except ValueError:
            pass
        aliases = self.__class__.Meta.fields
        if aliases == "__all__":
            self._root_node = (
                Node.objects.filter(
                    graph__slug=self.__class__.Meta.graph_slug,
                    alias=self.__class__.Meta.root_node,
                    graph__source_identifier=None,
                )
                .select_related("nodegroup")
                .prefetch_related("nodegroup__node_set")
                .get()
            )
            aliases = (
                self._root_node.nodegroup.node_set.exclude(nodegroup=None)
                .exclude(datatype="semantic")
                .values_list("alias", flat=True)
            )
        field_names.extend(aliases)
        return field_names

    def build_unknown_field(self, field_name, model_class):
        graph_slug = self.__class__.Meta.graph_slug
        if not self._nodes:
            self._nodes = Node.objects.filter(
                graph__slug=graph_slug,
                graph__source_identifier=None,
            )

        for node in self._nodes:
            if node.alias == field_name:
                break
        else:
            raise Node.DoesNotExist(
                f"Node with alias {field_name} not found in graph {graph_slug}"
            )

        datatype = DataTypeFactory().get_instance(node.datatype)
        model_field = deepcopy(datatype.rest_framework_model_field)
        if model_field is None:
            raise NotImplementedError(f"Field missing for datatype: {node.datatype}")
        model_field.model = model_class
        model_field.blank = not node.isrequired

        return self.build_standard_field(field_name, model_field)

    def build_relational_field(self, field_name, relation_info):
        ret = super().build_relational_field(field_name, relation_info)
        if field_name == "parenttile":
            ret[1]["queryset"] = ret[1]["queryset"].filter(
                nodegroup_id=self._root_node.nodegroup.parentnodegroup_id
            )
        return ret


class ArchesModelSerializer(serializers.ModelSerializer):
    legacyid = serializers.CharField(max_length=255, required=False, allow_null=True)

    _root_nodes = Node.objects.none()

    def get_fields(self):
        graph_slug = self.__class__.Meta.graph_slug

        if self.__class__.Meta.nodegroups == "__all__":
            self._root_nodes = Node.objects.filter(
                graph__slug=graph_slug,
                graph__source_identifier=None,
                nodegroup_id=F("nodeid"),
            ).select_related("nodegroup")
        else:
            self._root_nodes = Node.objects.filter(
                graph__slug=graph_slug,
                graph__source_identifier=None,
                nodegroup_id=F("nodeid"),
                node__alias__in=self.__class__.Meta.nodegroups,
            ).select_related("nodegroup")
        for root in self._root_nodes:
            if root.alias not in self._declared_fields:
                self._make_tile_serializer(root)
        return super().get_fields()

    def get_default_field_names(self, declared_fields, model_info):
        field_names = super().get_default_field_names(declared_fields, model_info)
        aliases = self.__class__.Meta.fields
        if aliases != "__all__":
            raise NotImplementedError  # TODO...
        nodegroups = self.__class__.Meta.nodegroups
        if nodegroups == "__all__":
            field_names.extend(self._root_nodes.values_list("alias", flat=True))
        else:
            field_names.extend(self.__class__.Meta.nodegroups)
        return field_names

    def build_relational_field(self, field_name, relation_info):
        ret = super().build_relational_field(field_name, relation_info)
        if field_name == "graph":
            ret[1]["queryset"] = ret[1]["queryset"].filter(
                graphmodel__slug=self.__class__.Meta.graph_slug
            )
        return ret

    def _make_tile_serializer(self, root):
        class DynamicTileSerializer(ArchesTileSerializer):
            class Meta:
                model = TileModel
                graph_slug = self.__class__.Meta.graph_slug
                root_node = root.alias
                fields = self.__class__.Meta.fields

        self._declared_fields[root.alias] = DynamicTileSerializer(
            many=root.nodegroup.cardinality == "n",
            required=False,
            allow_null=True,
        )

    def create(self, validated_data):
        meta = self.__class__.Meta
        instance_without_tile_data = super().create(validated_data)
        instance_from_factory = meta.model.as_model(
            graph_slug=self.__class__.Meta.graph_slug,
            only=None if meta.nodegroups == "__all__" else meta.nodegroups,
        ).get(pk=instance_without_tile_data.pk)
        # TODO: fullest/hydrated version of tile data not yet appearing?
        return self.update(instance_from_factory, validated_data)
