from copy import deepcopy

from rest_framework import renderers
from rest_framework import serializers

from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models.models import Node
from arches.app.utils.betterJSONSerializer import JSONSerializer


# Workaround for I18n_string fields
renderers.JSONRenderer.encoder_class = JSONSerializer
renderers.JSONOpenAPIRenderer.encoder_class = JSONSerializer


class ArchesTileSerializer(serializers.ModelSerializer):
    tileid = serializers.UUIDField(validators=[])

    def get_default_field_names(self, declared_fields, model_info):
        field_names = super().get_default_field_names(declared_fields, model_info)
        try:
            field_names.remove("data")
        except ValueError:
            pass
        aliases = self.__class__.Meta.fields
        if aliases == "__all__":
            # TODO: latest graph
            root_node = (
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
                root_node.nodegroup.node_set.exclude(nodegroup=None)
                .exclude(datatype="semantic")
                .values_list("alias", flat=True)
            )
        field_names.extend(aliases)
        return field_names

    def build_unknown_field(self, field_name, model_class):
        graph_slug = self.__class__.Meta.graph_slug
        node = (
            Node.objects.filter(
                graph__slug=graph_slug,
                graph__source_identifier=None,
                alias=field_name,
            )
            .select_related()
            .get()
        )
        datatype = DataTypeFactory().get_instance(node.datatype)
        model_field = deepcopy(datatype._rest_framework_model_field)
        if model_field is None:
            raise NotImplementedError(f"Field missing for datatype: {node.datatype}")
        model_field.model = model_class
        model_field.blank = not node.isrequired

        return self.build_standard_field(field_name, model_field)


class ArchesModelSerializer(serializers.ModelSerializer):
    def get_default_field_names(self, declared_fields, model_info):
        field_names = super().get_default_field_names(declared_fields, model_info)
        aliases = self.__class__.Meta.fields
        if aliases != "__all__":
            raise NotImplementedError  # TODO...
        field_names.extend(self.__class__.Meta.nodegroups)
        return field_names
