from functools import partial

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import PermissionDenied, ValidationError

from arches.app.models.models import ResourceInstance, TileModel
from arches.app.utils.permission_backend import (
    user_can_delete_resource,
    user_can_edit_resource,
    user_can_read_resource,
)


class ArchesModelAPIMixin:
    def get_queryset(self):
        fields = self.serializer_class.Meta.fields
        if fields == "__all__":
            fields = None
        else:
            raise NotImplementedError
        meta = self.serializer_class.Meta
        if ResourceInstance in meta.model.mro():
            only = None if meta.nodegroups == "__all__" else meta.nodegroups
            return meta.model.as_model(
                meta.graph_slug, only=only, as_representation=True
            )
        elif TileModel in meta.model.mro():
            return meta.model.as_nodegroup(
                meta.root_node,
                graph_slug=meta.graph_slug,
                only=fields,
                as_representation=True,
            )
        raise NotImplementedError

    def get_object(self, user=None, permission_callable=None):
        ret = super().get_object()
        if permission_callable and not permission_callable(user=user, resource=ret):
            # Not 404, see https://github.com/archesproject/arches/issues/11563
            raise PermissionDenied
        ret.save = partial(ret.save, user=user)
        return ret

    def create(self, request, *args, **kwargs):
        self.get_object = partial(
            self.get_object,
            user=request.user,
            permission_callable=user_can_edit_resource,
        )
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.get_object = partial(
            self.get_object,
            user=request.user,
            permission_callable=user_can_read_resource,
        )
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.get_object = partial(
            self.get_object,
            user=request.user,
            permission_callable=user_can_edit_resource,
        )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self.get_object = partial(
            self.get_object,
            user=request.user,
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
            # TODO: doesn't handle well inner lists, stringifies them
            raise ValidationError(detail=django_error.error_dict) from django_error

    def perform_create(self, serializer):
        self.validate_tile_data_and_save(serializer)

    def perform_update(self, serializer):
        self.validate_tile_data_and_save(serializer)
