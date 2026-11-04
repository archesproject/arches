from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.parsers import JSONParser

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
from arches.extensions.querysets.utils.permissions import filter_readable_resources


class ArchesResourceListCreateView(ArchesModelAPIMixin, ListCreateAPIView):
    permission_classes = [ResourceEditor | ReadOnly]
    serializer_class = ArchesResourceSerializer
    parser_classes = [JSONParser, MultiPartJSONParser]
    pagination_class = ArchesLimitOffsetPagination

    def get_queryset(self):
        return filter_readable_resources(self.request.user, super().get_queryset())


class ArchesResourceDetailView(ArchesModelAPIMixin, RetrieveUpdateDestroyAPIView):
    permission_classes = [ResourceEditor | ReadOnly]
    serializer_class = ArchesResourceSerializer
    parser_classes = [JSONParser, MultiPartJSONParser]


class ArchesTileListCreateView(ArchesModelAPIMixin, ListCreateAPIView):
    permission_classes = [ResourceEditor | ReadOnly]
    serializer_class = ArchesTileSerializer
    parser_classes = [JSONParser, MultiPartJSONParser]
    pagination_class = ArchesLimitOffsetPagination

    def get_queryset(self):
        return filter_readable_resources(
            self.request.user,
            super().get_queryset(),
            resourceinstance_field="resourceinstance_id",
            graph_field="resourceinstance__graph_id",
        )


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
