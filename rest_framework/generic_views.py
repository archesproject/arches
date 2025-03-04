from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from arches_querysets.rest_framework.permissions import Guest, ResourceEditor
from arches_querysets.rest_framework.serializers import (
    ArchesResourceSerializer,
    ArchesTileSerializer,
)
from arches_querysets.rest_framework.view_mixins import ArchesModelAPIMixin


class ArchesResourceListCreateView(ArchesModelAPIMixin, ListCreateAPIView):
    permission_classes = [Guest]
    serializer_class = ArchesResourceSerializer


class ArchesResourceDetailView(ArchesModelAPIMixin, RetrieveUpdateDestroyAPIView):
    permission_classes = [ResourceEditor]
    serializer_class = ArchesResourceSerializer


class ArchesTileListCreateView(ArchesModelAPIMixin, ListCreateAPIView):
    permission_classes = [Guest]
    serializer_class = ArchesTileSerializer


class ArchesTileDetailView(ArchesModelAPIMixin, RetrieveUpdateDestroyAPIView):
    permission_classes = [ResourceEditor]
    serializer_class = ArchesTileSerializer
