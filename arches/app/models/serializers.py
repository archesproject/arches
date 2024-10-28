from copy import deepcopy

from django.contrib.postgres.fields import ArrayField
from django.db.models import fields
from rest_framework import renderers
from rest_framework import serializers

# from rest_framework.utils import model_meta

from arches.app.models.models import Node, ResourceInstance, TileModel
from arches.app.utils.betterJSONSerializer import JSONSerializer


# Workaround for I18n_string fields
renderers.JSONRenderer.encoder_class = JSONSerializer
renderers.JSONOpenAPIRenderer.encoder_class = JSONSerializer


class ArchesTileSerializer(serializers.ModelSerializer):
    DATATYPE_FIELD_MAPPING = {
        "string": fields.CharField(null=True),  # XXX
        "number": fields.FloatField(null=True),
        "concept": fields.CharField(null=True),
        "concept-list": ArrayField(base_field=fields.CharField(), null=True),
        "date": fields.CharField(null=True),  # XXX
        "node-value": fields.CharField(null=True),  # XXX
        "edtf": fields.CharField(null=True),  # XXX
        "annotation": fields.CharField(null=True),  # XXX
        "url": fields.URLField(null=True),
        # "resource-instance": ForeignKey(to="self", on_delete=DO_NOTHING, null=True),
        "resource-instance": fields.UUIDField(null=True),
        "resource-instance-list": ArrayField(base_field=fields.UUIDField(), null=True),
        "boolean": fields.BooleanField(null=True),
        "domain-value": ArrayField(base_field=fields.CharField(), null=True),
        "domain-value-list": ArrayField(base_field=fields.CharField(), null=True),
        "non-localized-string": fields.CharField(null=True),
        "geojson-feature-collection": fields.CharField(null=True),  # XXX
        "file-list": ArrayField(base_field=fields.CharField(), null=True),  # XXX
        # "reference"
    }

    def get_default_field_names(self, declared_fields, model_info):
        field_names = super().get_default_field_names(declared_fields, model_info)
        aliases = self.__class__.Meta.fields
        if aliases == "__all__":
            aliases = (
                Node.objects.filter(
                    graph__slug=self.__class__.Meta.graph_slug,
                    graph__source_identifier=None,
                )
                .exclude(nodegroup=None)
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
        model_field.model = ResourceInstance
        model_field.blank = not node.isrequired

        # if isinstance(model_field, ForeignKey) and node.nodegroup.cardinality == "1":
        #     relation_info = model_meta.RelationInfo(
        #         model_field=ForeignKey(
        #             "ResourceInstance", on_delete=DO_NOTHING, blank=model_field.blank, null=True
        #         ),
        #         related_model=ResourceInstance,
        #         to_many=node.datatype == "resource-instance-list",
        #         to_field=None,
        #         has_through_model=False,
        #         reverse=False,
        #     )
        #     return self.build_relational_field(field_name, relation_info)

        if node.nodegroup.cardinality == "n":
            model_field = ArrayField(
                base_field=model_field, null=True, blank=model_field.blank
            )
            model_field.model = ResourceInstance

        return self.build_standard_field(field_name, model_field)


class ArchesModelSerializer(serializers.ModelSerializer):
    def get_default_field_names(self, declared_fields, model_info):
        field_names = super().get_default_field_names(declared_fields, model_info)
        aliases = self.__class__.Meta.fields
        if aliases == "__all__":
            aliases = (
                Node.objects.filter(
                    graph__slug=self.__class__.Meta.graph_slug,
                    # TODO: latest
                    graph__source_identifier=None,
                )
                .exclude(nodegroup=None)
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
                # TODO: latest
                graph__source_identifier=None,
                alias=field_name,
            )
            .select_related()
            .get()
        )
        model_field = deepcopy(self.DATATYPE_FIELD_MAPPING[node.datatype])
        model_field.model = TileModel

        if node.nodegroup.cardinality == "n":
            model_field = ArrayField(
                base_field=model_field, null=True, blank=model_field.blank
            )
            model_field.model = ResourceInstance

        return self.build_standard_field(field_name, model_field)
