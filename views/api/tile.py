from rest_framework.generics import (
    RetrieveUpdateDestroyAPIView,
)

from arches_querysets.rest_framework.serializers import ArchesResourceSerializer
from arches_querysets.rest_framework.view_mixins import ArchesModelAPIMixin


# TODO: Update with appropriate permission classes
class TileView(ArchesModelAPIMixin, RetrieveUpdateDestroyAPIView):
    permission_classes = []
    serializer_class = ArchesResourceSerializer
