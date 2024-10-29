from copy import deepcopy

from django.contrib.postgres.fields import ArrayField
from django.db.models import fields
from rest_framework import renderers
from rest_framework import serializers

from arches.app.models.models import Node
from arches.app.utils.betterJSONSerializer import JSONSerializer


# Workaround for I18n_string fields
renderers.JSONRenderer.encoder_class = JSONSerializer
renderers.JSONOpenAPIRenderer.encoder_class = JSONSerializer


class ArchesTileSerializer(serializers.ModelSerializer):
    DATATYPE_FIELD_MAPPING = {
        "string": fields.CharField(null=True),  # XXX
        "number": fields.FloatField(null=True),
        "concept": fields.UUIDField(null=True),
        "concept-list": ArrayField(base_field=fields.UUIDField(), null=True),
        "date": fields.CharField(null=True),  # XXX
        "node-value": fields.CharField(null=True),  # XXX
        "edtf": fields.CharField(null=True),  # XXX
        "annotation": fields.CharField(null=True),  # XXX
        "url": fields.URLField(null=True),
        "resource-instance": fields.UUIDField(null=True),
        "resource-instance-list": ArrayField(base_field=fields.UUIDField(), null=True),
        "boolean": fields.BooleanField(null=True),
        "domain-value": ArrayField(base_field=fields.UUIDField(), null=True),
        "domain-value-list": ArrayField(base_field=fields.UUIDField(), null=True),
        "non-localized-string": fields.CharField(null=True),
        "geojson-feature-collection": fields.CharField(null=True),  # XXX
        "file-list": ArrayField(base_field=fields.CharField(), null=True),  # XXX
        # "reference"
    }

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
        model_field = deepcopy(self.DATATYPE_FIELD_MAPPING[node.datatype])
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
