import json
import logging
import uuid
from urllib.parse import urlsplit, parse_qs
from django.db import connection
from django.http import HttpRequest
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils.translation import get_language, gettext as _
from arches.app.etl_modules.base_data_editor import BaseBulkEditor
from arches.app.etl_modules.decorators import load_data_async
from arches.app.etl_modules.save import get_resourceids_from_search_url, save_to_tiles
from arches.app.models.models import Value, Language, Node, ETLModule, GraphModel
from arches.app.models.concept import Concept
from arches.app.utils.db_utils import dictfetchall
from arches.app.views.search import search_results
from arches.app.tasks import edit_bulk_concept_data
from arches.app.search.mappings import RESOURCES_INDEX
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import (
    Bool,
    FiltersAgg,
    Match,
    Nested,
    NestedAgg,
    Query,
)

logger = logging.getLogger(__name__)


class MissingRequiredInputError(Exception):
    pass


def log_event_details(cursor, loadid, details):
    cursor.execute(
        """UPDATE load_event SET load_description = concat(load_description, %s) WHERE loadid = %s""",
        (details, loadid),
    )


class BulkConceptEditor(BaseBulkEditor):
    def validate_inputs(self, request):
        pass

    def get_graphs_node(self, request):
        graphid = request.POST.get("selectedGraph", None)
        with connection.cursor() as cursor:
            select_nodes = """
                SELECT c.name as card_name, n.config, n.nodeid, w.label as widget_label
                FROM cards c, nodes n, cards_x_nodes_x_widgets w
                WHERE n.nodeid = w.nodeid
                AND w.cardid = c.cardid
                AND (n.datatype = 'concept-list' or n.datatype = 'concept')
                AND n.graphid = %s
                ORDER BY c.name;
            """
            cursor.execute(select_nodes, [graphid])
            nodes = dictfetchall(cursor)
            return {"success": True, "data": nodes}

    def get_preview_data(
        self,
        node_id,
        search_url,
        old_concept,
        new_concept,
        preview_limit,
        page_index,
    ):
        request = HttpRequest()
        request.user = self.request.user
        request.method = "GET"
        request.GET["paging-filter"] = 1
        request.GET["tiles"] = True

        if search_url:
            params = parse_qs(urlsplit(search_url).query)
            for k, v in params.items():
                request.GET.__setitem__(k, v[0])

        search_url_query = search_results(request, returnDsl=True).dsl["query"]

        search_query = Match(
            field="tiles.data.%s" % (str(node_id)),
            type="phrase",
            query=old_concept,
        )
        search_bool_agg = Bool()
        search_bool_agg.must(search_query)

        concept_search_nested = Nested(path="tiles", query=search_query)
        inner_hits_query = {
            "inner_hits": {
                "_source": False,
                "docvalue_fields": [f"tiles.data.{node_id}.keyword", "tiles.tileid"],
            }
        }
        concept_search_nested.dsl["nested"].update(inner_hits_query)

        search_bool_query = Bool()
        search_bool_query.must(concept_search_nested)

        search_url_query["bool"]["must"].append(search_bool_query.dsl)

        search_filter_agg = FiltersAgg(name="string_search")
        search_filter_agg.add_filter(search_bool_agg)

        nested_agg = NestedAgg(path="tiles", name="tile_agg")
        nested_agg.add_aggregation(search_filter_agg)

        se = SearchEngineFactory().create()
        query = Query(se, limit=preview_limit)

        query.add_query(search_url_query)
        query.add_aggregation(nested_agg)

        start = preview_limit * int(page_index - 1)

        results = query.search(index=RESOURCES_INDEX, start=start, limit=preview_limit)
        values = []
        for hit in results["hits"]["hits"]:
            resourceid = hit["_id"]
            displayname = ""
            for name in hit["_source"]["displayname"]:
                if name["language"] == get_language():
                    displayname = name["value"]
            for tile in hit["inner_hits"]["tiles"]["hits"]["hits"]:
                original_valueids = tile["fields"][f"tiles.data.{node_id}.keyword"]
                new_valueids = set(
                    map(
                        lambda x: x.replace(old_concept, new_concept), original_valueids
                    )
                )

                original_preflabels = []
                for concept_value in Value.objects.filter(pk__in=original_valueids):
                    original_preflabels.append(concept_value.value)

                new_preflabels = []
                for concept_value in Value.objects.filter(pk__in=new_valueids):
                    new_preflabels.append(concept_value.value)

                values.append(
                    {
                        "displayname": displayname,
                        "resourceid": resourceid,
                        "tileid": tile["fields"][f"tiles.tileid"][0],
                        "original_preflabels": str(original_preflabels)
                        .replace("[", "")
                        .replace("]", ""),
                        "new_preflabels": str(new_preflabels)
                        .replace("[", "")
                        .replace("]", ""),
                    }
                )

        number_of_resources = results["hits"]["total"]["value"]
        number_of_tiles = results["aggregations"]["tile_agg"]["string_search"][
            "buckets"
        ][0]["doc_count"]

        return values[:preview_limit], number_of_tiles, number_of_resources

    def preview(self, request):
        return_list = []
        preview_limit = ETLModule.objects.get(pk=self.moduleid).config.get(
            "previewLimit", 5
        )

        page_index = int(request.POST.get("currentPageIndex", 0))
        page_index += 1
        search_url = request.POST.get("search_url", None)
        old_concept = request.POST.get("conceptOld", None)
        new_concept = request.POST.get("conceptNew", None)
        selected_node_info = request.POST.get("selectedNode", None)
        if not selected_node_info:
            return {}
        nodeid = json.loads(selected_node_info)["node"]

        try:
            self.validate_inputs(request)
        except MissingRequiredInputError as e:
            return {
                "success": False,
                "data": {"title": _("Missing input error"), "message": str(e)},
            }

        if search_url:
            try:
                validate = URLValidator()
                validate.max_length = 1000000
                validate(search_url)
            except ValidationError:
                return {
                    "success": False,
                    "data": {
                        "title": _("Invalid Search Url"),
                        "message": _("Please, enter a valid search url"),
                    },
                }

        try:
            return_list, number_of_tiles, number_of_resources = self.get_preview_data(
                nodeid,
                search_url,
                old_concept,
                new_concept,
                preview_limit,
                page_index,
            )
        except TypeError:
            return {
                "success": False,
                "data": {
                    "title": _("Invalid Search Url"),
                    "message": _("Please, enter a valid search url"),
                },
            }

        return {
            "success": True,
            "data": {
                "values": return_list,
                "number_of_tiles": number_of_tiles,
                "number_of_resources": number_of_resources,
                "preview_limit": preview_limit,
            },
        }

    def get_collection_languages(self, request):
        from arches.app.utils.i18n import rank_label

        collection_languages = []
        rdm_collection = request.POST.get("rdmCollection", None)
        language_codes = list(
            map(
                (lambda x: x[0]),
                Concept().get_child_collections(rdm_collection, columns="languageto"),
            )
        )
        for lang in Language.objects.filter(code__in=language_codes).values(
            "code", "name"
        ):
            collection_languages.append(
                {
                    "id": lang["code"],
                    "text": f"{lang['name']} ({lang['code']})",
                    "rank": rank_label(source_lang=lang["code"]),
                }
            )

        collection_languages.sort(key=lambda lang: lang["rank"], reverse=True)
        collection_languages[0]["selected"] = True

        return {
            "success": True,
            "data": collection_languages,
        }

    def write(self, request):
        graphid = request.POST.get("selectedGraph", None)
        selected_node_info = request.POST.get("selectedNode", None)
        node_info = json.loads(selected_node_info)
        nodeid = node_info["node"]
        node_label = node_info["label"]
        new = request.POST.get("conceptNew", None)
        old = request.POST.get("conceptOld", None)
        tiles_to_remove = request.POST.get("tilesToRemove", None)
        search_url = request.POST.get("search_url", None)

        old_prefLabel = Value.objects.values_list("value", flat=True).get(
            pk=old, valuetype__valuetype="prefLabel"
        )
        new_prefLabel = Value.objects.values_list("value", flat=True).get(
            pk=new, valuetype__valuetype="prefLabel"
        )

        unselected_tiles = ()
        resource_ids = ()
        if tiles_to_remove:
            unselected_tiles = [uuid.UUID(id) for id in tiles_to_remove.split(",")]
        if search_url:
            with connection.cursor() as cursor:
                self.log_event_details(
                    cursor, "done|Getting resources from search url..."
                )
            resource_ids = [
                uuid.UUID(id)
                for id in get_resourceids_from_search_url(search_url, request.user)
            ]

        graph_name = str(GraphModel.objects.get(pk=graphid).name)
        load_details = {
            "graph": graph_name,
            "node": node_label,
            "new": new_prefLabel,
            "old": old_prefLabel,
        }

        with connection.cursor() as cursor:
            event_created = self.create_load_event(cursor, load_details)
            if not event_created["success"]:
                self.log_event(cursor, "failed")
                return {"success": False, "data": event_created["message"]}

        use_celery_bulk_edit = True
        if use_celery_bulk_edit:
            response = self.run_load_task_async(request, self.loadid)
        else:
            response = self.run_load_task(
                self.userid,
                self.loadid,
                self.moduleid,
                graphid,
                nodeid,
                resource_ids,
                unselected_tiles,
                old,
                new,
            )
        return response

    @load_data_async
    def run_load_task_async(self, request):
        graph_id = request.POST.get("selectedGraph", None)
        selected_node_info = request.POST.get("selectedNode", None)
        node_id = json.loads(selected_node_info)["node"]
        new_id = request.POST.get("conceptNew", None)
        old_id = request.POST.get("conceptOld", None)
        tiles_to_remove = request.POST.get("tilesToRemove", None)
        search_url = request.POST.get("search_url", None)

        unselected_tiles = ()
        resource_ids = ()
        if tiles_to_remove:
            unselected_tiles = [uuid.UUID(id) for id in tiles_to_remove.split(",")]

        if search_url:
            with connection.cursor() as cursor:
                self.log_event_details(
                    cursor, "done|Getting resources from search url..."
                )
            resource_ids = [
                uuid.UUID(id)
                for id in get_resourceids_from_search_url(search_url, request.user)
            ]

        edit_task = edit_bulk_concept_data.apply_async(
            (
                self.userid,
                self.loadid,
                self.moduleid,
                graph_id,
                node_id,
                resource_ids,
                unselected_tiles,
                old_id,
                new_id,
            ),
        )
        with connection.cursor() as cursor:
            cursor.execute(
                """UPDATE load_event SET taskid = %s WHERE loadid = %s""",
                (edit_task.task_id, self.loadid),
            )

    def stage_data(
        self,
        cursor,
        nodeid,
        module_id,
        resource_ids,
        unselected_tiles,
        oldid,
        newid,
    ):
        result = {"success": False}
        update_limit = ETLModule.objects.get(pk=module_id).config.get(
            "updateLimit", 5000
        )

        tile_selection_query = (
            " AND NOT (tileid = ANY(%(tile_ids)s))" if unselected_tiles else ""
        )

        resourceids_query = (
            " AND resourceinstanceid = ANY(%(resource_ids)s)" if resource_ids else ""
        )

        limit_query = " LIMIT %(update_limit)s)"
        try:
            sql = (
                """
                INSERT INTO load_staging (value, tileid, nodegroupid, parenttileid, resourceid, loadid, nodegroup_depth, source_description, operation, passes_validation)
                    (SELECT tiledata, tileid, nodegroupid, parenttileid, resourceinstanceid, %(load_id)s, 0, 'bulk_edit', 'update', true
                    FROM tiles
                    WHERE nodegroupid in (SELECT nodegroupid FROM nodes WHERE nodeid = %(node_id)s)
                    AND tiledata -> %(node_id)s ? %(old_id)s
                """
                + tile_selection_query
                + resourceids_query
                + limit_query
            )

            cursor.execute(
                sql,
                {
                    "node_id_path": [nodeid],
                    "node_id": nodeid,
                    "old_id": oldid,
                    "new_id": newid,
                    "load_id": self.loadid,
                    "tile_ids": unselected_tiles,
                    "update_limit": update_limit,
                    "resource_ids": resource_ids,
                },
            )
            result["success"] = True

        except Exception as e:
            logger.error(e)
            result["message"] = _("Unable to edit staged data: {}").format(str(e))

        return result

    def edit_staged_data(self, cursor, node_id, old_id, new_id):
        result = {"success": False}
        try:
            cursor.execute(
                """SELECT * FROM __arches_edit_staged_concept(%s, %s, %s, %s)""",
                (self.loadid, node_id, old_id, new_id),
            )
            result["success"] = True
        except Exception as e:
            logger.error(e)
            result["message"] = _("Unable to edit staged data: {}").format(str(e))
        return result

    def run_load_task(
        self,
        userid,
        loadid,
        module_id,
        graph_id,
        node_id,
        resource_ids,
        unselected_tiles,
        old_id,
        new_id,
    ):
        with connection.cursor() as cursor:
            self.log_event_details(cursor, "done|Staging the data for edit...")
            data_staged = self.stage_data(
                cursor,
                node_id,
                module_id,
                resource_ids,
                unselected_tiles,
                old_id,
                new_id,
            )

            if data_staged["success"]:
                self.log_event_details(cursor, "done|Editing the data...")
                data_updated = self.edit_staged_data(cursor, node_id, old_id, new_id)
            else:
                self.log_event(cursor, "failed")
                return {
                    "success": False,
                    "data": {"title": _("Error"), "message": data_staged["message"]},
                }

            if data_updated["success"]:
                self.loadid = loadid  # currently redundant, but be certain
                save_to_tiles(userid, loadid)
                return {"success": True, "data": "done"}
            else:
                self.log_event(cursor, "failed")
                return {
                    "success": False,
                    "data": {"title": _("Error"), "message": data_updated["message"]},
                }
