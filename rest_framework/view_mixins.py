from functools import partial
from itertools import chain

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from django.utils.translation import gettext as _
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.metadata import SimpleMetadata
from rest_framework.settings import api_settings

from arches import VERSION as arches_version
from arches.app.models.models import Node, ResourceInstance, TileModel
from arches.app.utils.permission_backend import (
    user_can_delete_resource,
    user_can_edit_resource,
    user_can_read_resource,
)
from arches.app.utils.string_utils import str_to_bool

from arches_querysets.models import TileTree
from arches_querysets.utils.models import ensure_request


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
        self.nodegroup_alias = kwargs.get("nodegroup_alias")
        self.nodegroup_alias_lookup = {}

        if issubclass(options.model, TileModel):
            self.nodegroup_alias = options.root_node or self.nodegroup_alias

        if resource_ids := request.GET.get("resource_ids"):
            self.resource_ids = resource_ids.split(",")
        elif issubclass(options.model, ResourceInstance) and (pk := kwargs.get("pk")):
            self.resource_ids = [pk]
        else:
            self.resource_ids = None
        self.fill_blanks = request.GET.get("fill_blanks", "f").lower().startswith("t")

        # Graph nodes are supplied by the underlying queryset, either by
        # get_object() for detail views or filter_queryset() for list views.
        # creates don't have to worry about getting the same graph objects
        # from the retrieval operation: falls back to NodeFetcherMixin._find_graph_nodes()
        self.graph_nodes = Node.objects.none()

        return super().setup(request, *args, **kwargs)

    def get_queryset(self):
        options = self.serializer_class.Meta
        try:
            if issubclass(options.model, ResourceInstance):
                qs = options.model.get_tiles(
                    self.graph_slug,
                    resource_ids=self.resource_ids,
                    as_representation=True,
                ).select_related("graph")
                if arches_version >= (8, 0):
                    qs = qs.select_related("resource_instance_lifecycle_state")
            elif issubclass(options.model, TileModel):
                qs = options.model.get_tiles(
                    self.graph_slug,
                    self.nodegroup_alias,
                    as_representation=True,
                    resource_ids=self.resource_ids,
                ).select_related("nodegroup", "resourceinstance__graph")
                if self.resource_ids:
                    qs = qs.filter(resourceinstance__in=self.resource_ids)
            else:  # pragma: no cover
                raise NotImplementedError
        except ValueError:
            msg = _("No nodes found for graph slug: %s") % self.graph_slug
            raise ValidationError({api_settings.NON_FIELD_ERRORS_KEY: msg})

        return qs

    def get_serializer_context(self):
        context = super().get_serializer_context()
        ret = {
            **context,
            "request": ensure_request(context["request"]),
            "graph_slug": self.graph_slug,
            "graph_nodes": self.graph_nodes or self._find_graph_nodes(),
            "nodegroup_alias": self.nodegroup_alias,
        }
        if not ret.get("nodegroup_alias_lookup"):
            ret["nodegroup_alias_lookup"] = {
                node.pk: node.alias
                for node in ret["graph_nodes"]
                if node.pk == node.nodegroup_id
            }
        return ret

    def _find_graph_nodes(self):
        node_filters = Q(graph__slug=self.graph_slug, nodegroup__isnull=False)
        children = "nodegroup_set"
        # arches_version==9.0.0
        if arches_version >= (8, 0):
            node_filters &= Q(source_identifier=None)
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

    def get_object(self, permission_callable=None, fill_blanks=False):
        ret = super().get_object()
        if isinstance(ret, TileTree):
            self.graph_nodes = ret.resourceinstance.graph.node_set.all()
        else:
            self.graph_nodes = ret.graph.node_set.all()
        self.nodegroup_alias_lookup = {
            node.pk: node.alias
            for node in self.graph_nodes
            if node.pk == node.nodegroup_id
        }

        options = self.serializer_class.Meta
        if issubclass(options.model, ResourceInstance):
            # arches_version==9.0.0
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

        # Freeze some keyword arguments to the model save() method.
        is_partial_update = self.request.method == "PATCH"
        ret.save = partial(ret.save, request=self.request, partial=is_partial_update)

        if fill_blanks:
            ret.fill_blanks()

        return ret

    def filter_queryset(self, queryset):
        if queryset._hints.get("graph_query") is not None:
            self.graph_nodes = next(
                iter(queryset._hints.get("graph_query"))
            ).node_set.all()
            self.nodegroup_alias_lookup = {
                node.pk: node.alias
                for node in self.graph_nodes
                if node.pk == node.nodegroup_id
            }

        # Parse ORM lookpus from query params starting with "aliased_data__"
        # This is a quick-n-dirty riff on https://github.com/miki725/django-url-filter
        # minus some features like negation (`!=`)
        if data_filters := {
            param.split("aliased_data__", maxsplit=1)[1]: (
                str_to_bool(value) if param.endswith("__isnull") else value
            )
            for param, value in self.request.GET.items()
            if param.startswith("aliased_data__")
        }:
            queryset = queryset.filter(**data_filters)

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
            if isinstance(flattened_errors, dict):
                errors = flattened_errors
            else:
                errors = {api_settings.NON_FIELD_ERRORS_KEY: flattened_errors}
            raise ValidationError(errors) from django_error

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
        else:
            return error.messages
