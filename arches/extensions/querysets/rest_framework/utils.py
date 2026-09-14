from django.db import models

from arches import __version__ as _arches_version_str
from packaging.version import Version

arches_version = Version(_arches_version_str)
from arches.app.models.models import Node


def get_nodegroup_alias_lookup(graph_slug):
    filters = models.Q(pk=models.F("nodegroup_id"), graph__slug=graph_slug)
    # arches_version==9.0.0
    if arches_version >= Version("8.0"):
        filters &= models.Q(source_identifier=None)
    return {node.pk: node.alias for node in Node.objects.filter(filters).only("alias")}
