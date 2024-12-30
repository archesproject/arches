from functools import partial
from itertools import chain

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
            raise ValidationError(
                detail=self.flatten_validation_errors(django_error)
            ) from django_error
        # The backend hydrates additional data, so make sure to use it.
        # We could avoid this by only validating data during clean(),
        # not save(), but we do graph/node queries during each phase.
        # Having to fight so hard against DRF here is a good encouragement
        # to separate clean() and save() in a performant way when working on:
        # https://github.com/archesproject/arches/issues/10851#issuecomment-2427305853
        serializer._data = self.get_serializer(serializer.instance).data

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
