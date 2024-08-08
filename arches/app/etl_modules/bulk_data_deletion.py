from datetime import datetime
import json
import logging
import pyprind
import uuid
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import connection
from django.http import HttpRequest
from django.utils.translation import gettext as _
from arches.app.etl_modules.base_data_editor import BaseBulkEditor
from arches.app.etl_modules.decorators import load_data_async
from arches.app.etl_modules.save import get_resourceids_from_search_url
from arches.app.models.models import TileModel
from arches.app.models.resource import Resource
from arches.app.models.system_settings import settings
from arches.app.models.tile import Tile
import arches.app.tasks as tasks
from arches.app.utils.index_database import index_resources_by_transaction
from arches.app.utils.label_based_graph_v2 import LabelBasedGraph as LabelBasedGraphV2

logger = logging.getLogger(__name__)


class BulkDataDeletion(BaseBulkEditor):
    def get_number_of_deletions(self, graph_id, nodegroup_id, resourceids):
        params = {
            "nodegroup_id": nodegroup_id,
            "graph_id": graph_id,
            "resourceids": resourceids,
            "language_code": settings.LANGUAGE_CODE,
        }

        resourceids_query = (
            "AND resourceinstanceid IN %(resourceids)s" if resourceids else ""
        )
        tile_deletion_count = (
            """
            SELECT COUNT(DISTINCT resourceinstanceid), COUNT(tileid)
            FROM tiles
            WHERE nodegroupid = %(nodegroup_id)s
        """
            + resourceids_query
        )

        resource_deletion_count = """
            SELECT g.name ->> %(language_code)s, COUNT(r.resourceinstanceid)
            FROM resource_instances r, graphs g
            WHERE g.graphid = %(graph_id)s
            AND r.graphid = g.graphid
            GROUP BY g.name
        """

        search_url_deletion_count = """
            SELECT g.name ->> %(language_code)s, COUNT(r.resourceinstanceid)
            FROM resource_instances r, graphs g
            WHERE r.graphid = g.graphid
            AND r.resourceinstanceid IN %(resourceids)s
            GROUP BY g.name
        """

        if nodegroup_id:
            with connection.cursor() as cursor:
                cursor.execute(tile_deletion_count, params)
                row = cursor.fetchone()
            number_of_resource, number_of_tiles = row
        elif resourceids:
            with connection.cursor() as cursor:
                cursor.execute(search_url_deletion_count, params)
                rows = cursor.fetchall()
            number_of_resource = [{"name": i[0], "count": i[1]} for i in rows]
            number_of_tiles = 0
        else:
            with connection.cursor() as cursor:
                cursor.execute(resource_deletion_count, params)
                rows = cursor.fetchall()
            number_of_resource = [{"name": i[0], "count": i[1]} for i in rows]
            number_of_tiles = 0

        return number_of_resource, number_of_tiles

    def get_sample_data(self, nodegroup_id, resourceids):
        params = {
            "nodegroup_id": nodegroup_id,
            "resourceids": resourceids,
        }

        resourceids_query = (
            "AND resourceinstanceid IN %(resourceids)s" if resourceids else ""
        )
        get_sample_resource_ids = (
            """
            SELECT DISTINCT resourceinstanceid
            FROM tiles
            WHERE nodegroupid = %(nodegroup_id)s
        """
            + resourceids_query
            + """
            LIMIT 5
        """
        )

        get_sample_tiledata = (
            """
            SELECT tiledata
            FROM tiles
            WHERE nodegroupid = %(nodegroup_id)s
        """
            + resourceids_query
            + """
            LIMIT 5
        """
        )

        with connection.cursor() as cursor:
            cursor.execute(get_sample_resource_ids, params)
            rows = cursor.fetchall()
        sample_resource_ids = [row[0] for row in rows]
        sample_data = []
        for resourceid in sample_resource_ids:
            resource = Resource.objects.get(pk=resourceid)
            resource.tiles = list(
                TileModel.objects.filter(resourceinstance=resourceid).filter(
                    nodegroup_id=nodegroup_id
                )
            )
            lbg = LabelBasedGraphV2.from_resource(
                resource=resource,
                compact=True,
                hide_empty_nodes=True,
                hide_hidden_nodes=True,
            )
            for data in lbg["resource"].values():
                if type(data) == dict:  # cardinality-1 card
                    try:
                        samples = [data["@display_value"]]  # 1-node nodegroup
                    except KeyError:
                        samples = [
                            {k: v["@display_value"] for k, v in data.items()}
                        ]  # multi-node nodegroup
                elif type(data) == list:  # cardinality-n card
                    samples = []
                    for datum in data:
                        try:
                            tile_values = datum["@display_value"]  # 1-node nodegroup
                        except KeyError:
                            tile_values = {
                                k: v["@display_value"] for k, v in datum.items()
                            }  # multi-node nodegroup
                        samples.append(tile_values)
                sample_data.extend(samples)
            if len(sample_data) >= 5:
                break

        return sample_data[0:5]

    def delete_resources(
        self, userid, loadid, graphid=None, resourceids=None, verbose=False
    ):
        result = {"success": False}
        deleted_count = 0
        user = User.objects.get(id=userid) if userid else {}
        try:
            if resourceids:
                resources = Resource.objects.filter(pk__in=resourceids)
            elif graphid:
                resources = Resource.objects.filter(graph_id=graphid)
            else:
                result["message"] = _(
                    "Unable to bulk delete resources as no graphid or resourceids specified."
                )
                result["deleted_count"] = 0
                return result

            deleted_count = resources.count()

            if verbose is True:
                bar = pyprind.ProgBar(deleted_count)
            for resource in resources.iterator(chunk_size=2000):
                resource.delete(user=user, index=False, transaction_id=loadid)
                if verbose is True:
                    bar.update()

            if verbose is True:
                print(bar)
            result["success"] = True
            result["deleted_count"] = deleted_count
            result["message"] = _("Successfully deleted {} resources").format(
                str(deleted_count)
            )
        except Exception as e:
            logger.exception(e)
            result["message"] = _("Unable to delete resources: {}").format(str(e))

        return result

    def delete_tiles(self, userid, loadid, nodegroupid, resourceids):
        result = {"success": False}
        user = User.objects.get(id=userid)

        try:
            if resourceids:
                tiles = Tile.objects.filter(nodegroup_id=nodegroupid).filter(
                    resourceinstance_id__in=resourceids
                )
            else:
                tiles = Tile.objects.filter(nodegroup_id=nodegroupid)
            for tile in tiles.iterator(chunk_size=2000):
                request = HttpRequest()
                request.user = user
                tile.delete(request=request, index=False, transaction_id=loadid)
            result["success"] = True
        except Exception as e:
            logger.exception(e)
            result["message"] = _("Unable to delete tiles: {}").format(str(e))

        return result

    def index_resource_deletion(self, loadid, resourceids=None):
        if not resourceids:
            with connection.cursor() as cursor:
                cursor.execute(
                    """SELECT DISTINCT resourceinstanceid
                        FROM edit_log
                        WHERE transactionid = %s::uuid;
                    """,
                    [loadid],
                )
                rows = cursor.fetchall()
                resourceids = [row[0] for row in rows]

        resource = Resource()
        for resourceid in resourceids:
            resource.delete_index(resourceid)

    def index_tile_deletion(self, loadid):
        index_resources_by_transaction(
            loadid, quiet=True, use_multiprocessing=False, recalculate_descriptors=True
        )

    def preview(self, request):
        graph_id = request.POST.get("graph_id", None)
        nodegroup_id = request.POST.get("nodegroup_id", None)
        resourceids = request.POST.get("resourceids", None)
        search_url = request.POST.get("search_url", None)

        if resourceids:
            resourceids = json.loads(resourceids)
        if search_url:
            try:
                resourceids = get_resourceids_from_search_url(
                    search_url, self.request.user
                )
            except ValidationError:
                return {
                    "success": False,
                    "data": {
                        "title": _("Invalid Search Url"),
                        "message": _("Please, enter a valid search url"),
                    },
                }
        if resourceids:
            resourceids = tuple(resourceids)

        number_of_resource, number_of_tiles = self.get_number_of_deletions(
            graph_id, nodegroup_id, resourceids
        )
        result = {"resource": number_of_resource, "tile": number_of_tiles}

        if nodegroup_id:
            try:
                sample_data = self.get_sample_data(nodegroup_id, resourceids)
                result["preview"] = sample_data
            except Exception as e:
                logger.exception(e)

        return {"success": True, "data": result}

    def delete(self, request):
        graph_id = request.POST.get("graph_id", None)
        graph_name = request.POST.get("graph_name", None)
        nodegroup_id = request.POST.get("nodegroup_id", None)
        nodegroup_name = request.POST.get("nodegroup_name", None)
        resourceids = request.POST.get("resourceids", None)
        search_url = request.POST.get("search_url", None)

        if resourceids:
            resourceids = json.loads(resourceids)
        if resourceids:
            resourceids = tuple(resourceids)
        if search_url:
            try:
                resourceids = get_resourceids_from_search_url(
                    search_url, self.request.user
                )
            except ValidationError:
                return {
                    "success": False,
                    "data": {
                        "title": _("Invalid Search Url"),
                        "message": _("Please, enter a valid search url"),
                    },
                }

        use_celery_bulk_delete = True

        load_details = {
            "graph": graph_name,
            "nodegroup": nodegroup_name,
            "search_url": search_url,
        }

        with connection.cursor() as cursor:
            event_created = self.create_load_event(cursor, load_details)
            if event_created["success"]:
                if use_celery_bulk_delete:
                    response = self.run_bulk_task_async(request, self.loadid)
                else:
                    response = self.run_bulk_task(
                        self.userid, self.loadid, graph_id, nodegroup_id, resourceids
                    )
            else:
                self.log_event(cursor, "failed")
                return {"success": False, "data": event_created["message"]}

        return response

    @load_data_async
    def run_bulk_task_async(self, request):
        graph_id = request.POST.get("graph_id", None)
        nodegroup_id = request.POST.get("nodegroup_id", None)
        resourceids = request.POST.get("resourceids", None)
        search_url = request.POST.get("search_url", None)

        if resourceids:
            resourceids = json.loads(resourceids)
        if search_url:
            resourceids = get_resourceids_from_search_url(search_url, self.request.user)

        edit_task = tasks.bulk_data_deletion.apply_async(
            (self.userid, self.loadid, graph_id, nodegroup_id, resourceids),
        )
        with connection.cursor() as cursor:
            cursor.execute(
                """UPDATE load_event SET taskid = %s WHERE loadid = %s""",
                (edit_task.task_id, self.loadid),
            )

    def run_bulk_task(self, userid, loadid, graph_id, nodegroup_id, resourceids):
        if resourceids:
            resourceids = [uuid.UUID(id) for id in resourceids]

        if nodegroup_id:
            deleted = self.delete_tiles(userid, loadid, nodegroup_id, resourceids)
        elif graph_id or resourceids:
            deleted = self.delete_resources(
                userid, loadid, graphid=graph_id, resourceids=resourceids
            )

        with connection.cursor() as cursor:
            if deleted["success"]:
                self.log_event(cursor, "completed")
            else:
                self.log_event(cursor, "failed")
                return {
                    "success": False,
                    "data": {"title": _("Error"), "message": deleted["message"]},
                }

            # count the numbers of deleted resource / tiles
            cursor.execute(
                """SELECT g.name, COUNT(DISTINCT e.resourceinstanceid)
                    FROM edit_log e, graphs g
                    WHERE g.graphid = e.resourceclassid::uuid
                    AND e.transactionid = %s::uuid
                    AND e.edittype = 'delete'
                    GROUP BY g.name;
                """,
                [loadid],
            )
            resources = cursor.fetchall()
            number_of_data = {}
            for resource in resources:
                graph = json.loads(resource[0])[settings.LANGUAGE_CODE]
                number_of_data.update({graph: {"total": resource[1]}})
            cursor.execute(
                """SELECT g.name, n.name, COUNT(DISTINCT e.tileinstanceid)
                    FROM edit_log e, nodes n, graphs g
                    WHERE n.nodeid = e.nodegroupid::uuid
                    AND g.graphid = e.resourceclassid::uuid
                    AND e.transactionid = %s::uuid
                    AND e.edittype = 'tile delete'
                    GROUP BY g.name, n.name;
                """,
                [loadid],
            )
            tiles = cursor.fetchall()
            for tile in tiles:
                graph = json.loads(tile[0])[settings.LANGUAGE_CODE]
                number_of_data.setdefault(graph, {"total": 0}).setdefault(
                    "tiles", []
                ).append({"tile": tile[1], "count": tile[2]})

            number_of_delete = json.dumps(
                {
                    "number_of_delete": [
                        {
                            "name": k,
                            "total": v["total"],
                            "tiles": v.setdefault("tiles", {}),
                        }
                        for k, v in number_of_data.items()
                    ]
                }
            )
            cursor.execute(
                """UPDATE load_event SET load_details = load_details || %s::JSONB WHERE loadid = %s""",
                (number_of_delete, loadid),
            )

        try:
            if nodegroup_id:
                self.index_tile_deletion(loadid)
            else:
                self.index_resource_deletion(loadid, resourceids=resourceids)
        except Exception as e:
            logger.exception(e)
            with connection.cursor() as cursor:
                self.log_event(cursor, "unindexed")

            return {
                "success": False,
                "data": {
                    "title": _("Indexing Error"),
                    "message": _(
                        "The database may need to be reindexed. Please contact your administrator."
                    ),
                },
            }

        with connection.cursor() as cursor:
            cursor.execute(
                """UPDATE load_event SET (status, indexed_time, complete, successful) = (%s, %s, %s, %s) WHERE loadid = %s""",
                ("indexed", datetime.now(), True, True, loadid),
            )
        return {"success": True, "data": "indexed"}
