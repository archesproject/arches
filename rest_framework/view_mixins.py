from functools import partial
from itertools import chain

from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext as _
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.metadata import SimpleMetadata

from arches import VERSION as arches_version
from arches.app.models.models import ResourceInstance, TileModel
from arches.app.utils.permission_backend import (
    user_can_delete_resource,
    user_can_edit_resource,
    user_can_read_resource,
)


class MetadataWithWidgetConfig(SimpleMetadata):
    def get_field_info(self, field):
        return {
            **super().get_field_info(field),
            "key": field.style.get("alias"),
            "initial": (
                None if field.initial is field.default_empty_html else field.initial
            ),
            "visible": field.style.get("visible", True),
            "datatype": field.style.get("datatype"),
            "widget_config": field.style.get("widget_config", {}),
            "sortorder": field.style.get("sortorder", 0),
        }


class ArchesModelAPIMixin:
    metadata_class = MetadataWithWidgetConfig

    def setup(self, request, *args, **kwargs):
        options = self.serializer_class.Meta
        self.graph_slug = options.graph_slug or kwargs.get("graph")
        # Future: accept list via GET query param
        self.nodegroup_alias = kwargs.get("nodegroup_alias")

        if issubclass(options.model, TileModel):
            self.nodegroup_alias = options.root_node or self.nodegroup_alias

        if resource_ids := request.GET.get("resource_ids"):
            self.resource_ids = resource_ids.split(",")
        elif issubclass(options.model, ResourceInstance) and (pk := kwargs.get("pk")):
            self.resource_ids = [pk]
        else:
            self.resource_ids = None
        self.fill_blanks = request.GET.get("fill_blanks", "f").lower().startswith("t")

        # Initialize a variable to hold the permitted nodes nodes materialized
        # by the underlying queryset (populated by get_object() for detail
        # views or filter_queryset() for list views).
        self.permitted_nodes = []

        return super().setup(request, *args, **kwargs)

    def get_queryset(self):
        options = self.serializer_class.Meta
        if options.fields == "__all__":
            fields = None
        else:
            fields = options.fields

        if issubclass(options.model, ResourceInstance):
            if options.nodegroups == "__all__":
                if self.nodegroup_alias:
                    only = [self.nodegroup_alias]
                else:
                    only = None
            else:
                only = options.nodegroups
            return options.model.get_tiles(
                self.graph_slug,
                only=only,
                resource_ids=self.resource_ids,
                as_representation=True,
                user=self.request.user,
            ).select_related("graph")
        if issubclass(options.model, TileModel):
            qs = options.model.get_tiles(
                self.graph_slug,
                self.nodegroup_alias,
                only=fields,
                as_representation=True,
                resource_ids=self.resource_ids,
                user=self.request.user,
            ).select_related("nodegroup", "resourceinstance__graph")
            if self.resource_ids:
                return qs.filter(resourceinstance__in=self.resource_ids)
            return qs

        raise NotImplementedError

    def get_serializer_context(self):
        return {
            **super().get_serializer_context(),
            "graph_slug": self.graph_slug,
            "permitted_nodes": self.permitted_nodes,
            "nodegroup_alias": self.nodegroup_alias,
        }

    def get_object(self, permission_callable=None, fill_blanks=False):
        ret = super().get_object()
        options = self.serializer_class.Meta
        if issubclass(options.model, ResourceInstance):
            if arches_version >= (8, 0):
                permission_kwargs = {"user": self.request.user, "resource": ret}
            else:
                permission_kwargs = {"user": self.request.user, "resourceid": ret.pk}
            if not self.graph_slug:
                # Resource results for heterogenous graphs are not supported.
                self.graph_slug = ret.graph.slug
        else:
            permission_kwargs = {
                "user": self.request.user,
                "resourceid": ret.resourceinstance_id,
            }
            if not self.graph_slug:
                self.graph_slug = ret.resourceinstance.graph.slug
        if permission_callable and not permission_callable(**permission_kwargs):
            # Not 404, see https://github.com/archesproject/arches/issues/11563
            raise PermissionDenied
        ret.save = partial(ret.save, request=self.request)
        self.permitted_nodes = ret._permitted_nodes

        if fill_blanks:
            ret.fill_blanks()

        return ret

    def filter_queryset(self, queryset):
        self.permitted_nodes = queryset._permitted_nodes
        return super().filter_queryset(queryset)

    def create(self, request, *args, **kwargs):
        self.get_object = partial(
            self.get_object,
            permission_callable=user_can_edit_resource,
            fill_blanks=self.fill_blanks,
        )
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.get_object = partial(
            self.get_object,
            permission_callable=user_can_read_resource,
            fill_blanks=self.fill_blanks,
        )
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.get_object = partial(
            self.get_object,
            permission_callable=user_can_edit_resource,
            fill_blanks=self.fill_blanks,
        )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self.get_object = partial(
            self.get_object,
            permission_callable=user_can_delete_resource,
        )
        return super().destroy(request, *args, **kwargs)

    def validate_tile_data_and_save(self, serializer):
        """Re-raise ValidationError as DRF ValidationError.

        In 3.0 (2014), DRF decided to stop full_clean()'ing before save(),
        which divorces DRF validation needs from model logic needing to
        support the Django admin or similar ModelFormish patterns.
        The stated reasons were:
            - to avoid calling into big & scary full_clean().
            - to force expressing validation logic outside of models.
        but adhering to that second point would be difficult in light of
        how dynamically these fields are constructed.

        Discussion:
        https://github.com/encode/django-rest-framework/discussions/7850
        """
        try:
            serializer.save()
        except DjangoValidationError as django_error:
            flattened_errors = self.flatten_validation_errors(django_error)
            raise ValidationError(flattened_errors) from django_error

    def perform_create(self, serializer):
        self.validate_tile_data_and_save(serializer)

    def perform_update(self, serializer):
        self.validate_tile_data_and_save(serializer)

    @staticmethod
    def flatten_validation_errors(error):
        """DRF's ValidationError doesn't really handle nesting, so unpack
        one level."""
        if hasattr(error, "error_dict"):
            return {
                k: (
                    list(chain.from_iterable(inner.messages for inner in v))
                    if all(isinstance(inner, DjangoValidationError) for inner in v)
                    else v
                )
                for k, v in error.error_dict.items()
            }
        return error
