"""
ARCHES - a program developed to inventory and manage immovable cultural heritage.
Copyright (C) 2013 J. Paul Getty Trust and World Monuments Fund

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

"""This module contains commands for building Arches."""

from operator import index
from typing import Any, Optional
from django.core.management.base import BaseCommand
from arches.app.models.resource import Resource
from arches.app.models.system_settings import settings
from arches.app.search.base_index import get_index
from arches.app.search.elasticsearch_dsl_builder import Query, Term
from arches.app.search.mappings import (
    RESOURCE_RELATIONS_INDEX,
    RESOURCES_INDEX,
    TERMS_INDEX,
    prepare_terms_index,
    prepare_concepts_index,
    delete_terms_index,
    delete_concepts_index,
    prepare_search_index,
    delete_search_index,
    prepare_resource_relations_index,
    delete_resource_relations_index,
)
import arches.app.utils.index_database as index_database_util

from arches.app.models.models import BulkIndexQueue, ResourceInstance, TileModel


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("-operation", action="store", dest="operation", default="")

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        bulk_index_queue = BulkIndexQueue.objects.all()
        queued_ids = bulk_index_queue.values_list("resourceinstanceid", flat=True)
        resources = Resource.objects.filter(resourceinstanceid__in=queued_ids)
        delete_ids = queued_ids.difference(
            resources.values_list("resourceinstanceid", flat=True)
        )

        # This is for testing delete operations; it deletes a random resource (the first inside the bulk index queue)
        # without indexing the delete.  Do not use this on production systems.
        if options["operation"] == "test_delete":
            instances = ResourceInstance.objects.filter(
                resourceinstanceid__in=queued_ids
            )
            print(instances[0].resourceinstanceid)
            instances[0].delete()
            return

        if len(delete_ids) > 0:
            from arches.app.search.search_engine_factory import (
                SearchEngineInstance as _se,
            )

            deleteq = Query(se=_se)
            for resource_id in delete_ids:
                term = Term(field="resourceinstanceid", term=str(resource_id))
                deleteq.add_query(term)
            deleteq.delete(index=TERMS_INDEX, refresh=True)
            deleteq.delete(index=RESOURCES_INDEX, refresh=True)
            deleteq.delete(index=RESOURCE_RELATIONS_INDEX, refresh=True)
            bulk_index_queue.filter(resourceinstanceid__in=delete_ids).delete()

        index_database_util.index_resources_using_singleprocessing(
            resources, title="Processing Indexing Queue"
        )
        bulk_index_queue.delete()
