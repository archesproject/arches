import json
from contextlib import contextmanager

from django.db import connection
from django.utils.translation import ngettext
from rest_framework import status
from rest_framework.generics import (
    GenericAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from arches.app.utils.permission_backend import user_can_edit_resource
from arches.extensions.querysets.rest_framework.change_sets import (
    ResourceChangeSet,
    parse_changes,
)

from arches.extensions.querysets.rest_framework.multipart_json_parser import (
    MultiPartJSONParser,
)
from arches.extensions.querysets.rest_framework.pagination import (
    ArchesLimitOffsetPagination,
)
from arches.extensions.querysets.rest_framework.permissions import (
    ReadOnly,
    ResourceEditor,
)
from arches.extensions.querysets.rest_framework.serializers import (
    ArchesResourceSerializer,
    ArchesResourceTopNodegroupsSerializer,
    ArchesSingleNodegroupSerializer,
    ArchesTileSerializer,
)
from arches.extensions.querysets.rest_framework.view_mixins import ArchesModelAPIMixin


@contextmanager
def resource_lock(resource_id):
    # Session-level advisory lock, not select_for_update: the tile save
    # opens a durable atomic block, which can't nest inside a transaction.
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT pg_advisory_lock(hashtextextended(%s, 0))", [str(resource_id)]
        )
    try:
        yield
    finally:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT pg_advisory_unlock(hashtextextended(%s, 0))",
                [str(resource_id)],
            )


class ArchesResourceListCreateView(ArchesModelAPIMixin, ListCreateAPIView):
    permission_classes = [ResourceEditor | ReadOnly]
    serializer_class = ArchesResourceSerializer
    parser_classes = [JSONParser, MultiPartJSONParser]
    pagination_class = ArchesLimitOffsetPagination


class ArchesResourceDetailView(ArchesModelAPIMixin, RetrieveUpdateDestroyAPIView):
    permission_classes = [ResourceEditor | ReadOnly]
    serializer_class = ArchesResourceSerializer
    parser_classes = [JSONParser, MultiPartJSONParser]


class ArchesResourceChangesView(ArchesModelAPIMixin, GenericAPIView):
    """Apply a list of tile changes, or return 409 if any conflict with the
    current resource. Saves through the same serializer path as PUT."""

    permission_classes = [ResourceEditor]
    serializer_class = ArchesResourceSerializer
    parser_classes = [JSONParser, MultiPartJSONParser]

    def post(self, request, *args, **kwargs):
        changes = parse_changes(request.data)
        with resource_lock(kwargs["pk"]):
            instance = self.get_object(
                permission_callable=user_can_edit_resource,
                fill_blanks=self.fill_blanks,
            )
            current = json.loads(
                JSONRenderer().render(self.get_serializer(instance).data)
            )
            if not changes:
                return Response(current)

            change_set = ResourceChangeSet(
                changes,
                current,
                graph_nodes=instance.graph.node_set.select_related("nodegroup"),
                resource_id=instance.pk,
                user=request.user,
            )
            change_set.validate()
            if conflicts := change_set.find_conflicts():
                message = ngettext(
                    "%(count)d change conflicts with edits saved by someone else "
                    "since you loaded this resource. Nothing was saved.",
                    "%(count)d changes conflict with edits saved by someone else "
                    "since you loaded this resource. Nothing was saved.",
                    len(conflicts),
                ) % {"count": len(conflicts)}
                return Response(
                    {"message": message, "conflicts": conflicts, "resource": current},
                    status=status.HTTP_409_CONFLICT,
                )

            serializer = self.get_serializer(instance, data=change_set.apply())
            serializer.is_valid(raise_exception=True)
            self.validate_tile_data_and_save(serializer)
        return Response(serializer.data)


class ArchesTileListCreateView(ArchesModelAPIMixin, ListCreateAPIView):
    permission_classes = [ResourceEditor | ReadOnly]
    serializer_class = ArchesTileSerializer
    parser_classes = [JSONParser, MultiPartJSONParser]
    pagination_class = ArchesLimitOffsetPagination


class ArchesTileDetailView(ArchesModelAPIMixin, RetrieveUpdateDestroyAPIView):
    permission_classes = [ResourceEditor | ReadOnly]
    serializer_class = ArchesTileSerializer
    parser_classes = [JSONParser, MultiPartJSONParser]


### Views for returning blank resource & tile templates


class ArchesResourceBlankView(ArchesModelAPIMixin, RetrieveAPIView):
    permission_classes = [ReadOnly]
    serializer_class = ArchesResourceSerializer

    def get_serializer_class(self):
        if self.request.GET.get("exclude_children", "").lower() == "true":
            return ArchesResourceTopNodegroupsSerializer
        return self.serializer_class

    def get_serializer_context(self):
        serializer_context = super().get_serializer_context()
        fill_blanks = self.request.GET.get("fill_blanks", "true").lower() == "true"
        serializer_context["fill_blanks"] = fill_blanks
        return serializer_context

    def get_object(self, *args, **kwargs):
        return None


class ArchesTileBlankView(ArchesModelAPIMixin, RetrieveAPIView):
    permission_classes = [ReadOnly]
    serializer_class = ArchesTileSerializer

    def get_serializer_class(self):
        if self.request.GET.get("exclude_children", "").lower() == "true":
            return ArchesSingleNodegroupSerializer
        return self.serializer_class

    def get_serializer_context(self):
        serializer_context = super().get_serializer_context()
        fill_blanks = self.request.GET.get("fill_blanks", "true").lower() == "true"
        serializer_context["fill_blanks"] = fill_blanks
        return serializer_context

    def get_object(self, *args, **kwargs):
        return None
