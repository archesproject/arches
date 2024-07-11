details = {
    "etlmoduleid": "",
    "name": "Bulk Replace Concept",
    "description": "Replace concept",
    "etl_type": "edit",
    "component": "views/components/etl_modules/bulk_edit_concept",
    "componentname": "bulk_edit_concept",
    "modulename": "bulk_edit_concept.py",
    "classname": "BulkConceptEditor",
    "config": {"bgColor": "#f5c60a", "circleColor": "#f9dd6c"},
    "reversible": True,
    "icon": "fa fa-edit",
    "slug": "bulk_edit_concept",
    "helpsortorder": 9,
    "helptemplate": "bulk_edit_concept-help",
}

from datetime import datetime
import json
import logging
import uuid
from urllib.parse import urlsplit, parse_qs
from django.db import connection
from django.http import HttpRequest
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.contrib.auth.models import User
from django.utils.translation import get_language, gettext as _
from arches.app.etl_modules.base_data_editor import BaseBulkEditor
from arches.app.etl_modules.decorators import load_data_async
from arches.app.models.system_settings import settings
from arches.app.models.models import Value, Language
from arches.app.models.concept import Concept
from arches.app.utils.db_utils import dictfetchall
from arches.app.utils.index_database import index_resources_by_transaction
from arches.app.views.search import search_results
from arches.app.tasks import edit_bulk_concept_data

logger = logging.getLogger(__name__)


def log_event_details(cursor, loadid, details):
    cursor.execute(
        """UPDATE load_event SET load_description = concat(load_description, %s) WHERE loadid = %s""",
        (details, loadid),
    )


def perth_items(items):
    id_name_pairs = []
    if len(items) % 2 == 0:
        id_name_pairs = [[items[i], items[i + 1]] for i in range(0, len(items), 2)]
    else:
        count = 0
        help_var = ""
        extra = ""

        for i in range(len(items)):

            if count == 0:
                extra = ""  # Reset extra for each iteration
                count += 1
                help_var = items[i]
            else:
                if i + 1 <= len(items):
                    try:
                        uuid.UUID(items[i + 1])
                        count = 0
                        extra = extra + items[i]
                        id_name_pairs.append([help_var, extra])
                    except:
                        extra = items[i] + ","
    return id_name_pairs


class BulkConceptEditor(BaseBulkEditor):
    def editor_log(self, cursor, tile, node_id, resourceid, old_value):
        id = uuid.uuid4()
        cursor.execute(
            """INSERT INTO edit_log (editlogid, resourceinstanceid, nodegroupid, tileinstanceid, oldvalue, edittype, transactionid) VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (id, resourceid, node_id, tile, old_value, "tile edit", str(self.loadid)),
        )

    def save_tiles(
        self,
        cursor,
        loadid,
        userid,
        tileids,
        newids,
        tiledatas,
        nodeids,
        newresources,
        oldid,
    ):
        log_event_details(cursor, loadid, "done|Saving the tiles...")
        log_event_details(cursor, loadid, "done|Getting the statistics...")

        cursor.execute(
            """SELECT g.name graph, COUNT(DISTINCT l.resourceid)
                        FROM load_staging l, resource_instances r, graphs g
                        WHERE l.loadid = %s
                        AND r.resourceinstanceid = l.resourceid
                        AND g.graphid = r.graphid
                        GROUP BY g.name""",
            [loadid],
        )
        resources = cursor.fetchall()
        number_of_resources = {}

        for resource in resources:
            graph = json.loads(resource[0])[settings.LANGUAGE_CODE]
            number_of_resources.update({graph: {"total": resource[1]}})

        cursor.execute(
            """SELECT g.name graph, n.name, COUNT(*)
                        FROM load_staging l, nodes n, graphs g
                        WHERE l.loadid = %s
                        AND n.nodeid = l.nodegroupid
                        AND n.graphid = g.graphid
                        GROUP BY n.name, g.name;""",
            [loadid],
        )
        tiles = cursor.fetchall()

        for tile in tiles:
            graph = json.loads(tile[0])[settings.LANGUAGE_CODE]
            number_of_resources[graph].setdefault("tiles", []).append(
                {"tile": tile[1], "count": tile[2]}
            )

        number_of_import = json.dumps(
            {
                "number_of_import": [
                    {"name": k, "total": v["total"], "tiles": v["tiles"]}
                    for k, v in number_of_resources.items()
                ]
            }
        )

        cursor.execute(
            """UPDATE load_event SET (status, load_end_time, load_details) = (%s, %s, load_details || %s::JSONB) WHERE loadid = %s""",
            ("completed", datetime.now(), number_of_import, loadid),
        )

        log_event_details(cursor, loadid, "done|Indexing...")
        index_resources_by_transaction(
            loadid, quiet=True, use_multiprocessing=False, recalculate_descriptors=True
        )
        user = User.objects.get(id=userid)
        user_email = getattr(user, "email", "")
        user_firstname = getattr(user, "first_name", "")
        user_lastname = getattr(user, "last_name", "")
        user_username = getattr(user, "username", "")
        log_event_details(cursor, loadid, "done|Updating the edit log...")
        new_tiledata = []
        match_tileid = []
        match_resourceid = []
        for tileid, tiledata, newresource in zip(tileids, tiledatas, newresources):

            if str(oldid) in tiledata.get(str(nodeids), []):
                if isinstance(tiledata[str(nodeids)], list):
                    tiledata[str(nodeids)][tiledata[str(nodeids)].index(str(oldid))] = (
                        str(newids)
                    )
                else:
                    tiledata[str(nodeids)] = str(newids)
                new_tiledata.append(tiledata)
                match_tileid.append(tileid)
                match_resourceid.append(newresource)

        update_data = [
            (json.dumps(data_json), str(resource_id), str(tile_id))
            for data_json, resource_id, tile_id in zip(
                new_tiledata, match_resourceid, match_tileid
            )
        ]
        update_query = "UPDATE tiles SET tiledata = %s WHERE resourceinstanceid = %s AND tileid = %s;"
        try:

            cursor.executemany(update_query, update_data)

        except Exception as e:
            cursor.execute(
                """UPDATE load_event SET status = %s, load_end_time = %s WHERE loadid = %s""",
                ("failed", datetime.now(), self.loadid),
            )

            print("Error:", e)
            return None

        for tiledata in new_tiledata:
            json_data = json.dumps(tiledata)
            cursor.execute(
                """
                UPDATE edit_log e
                SET (resourcedisplayname, userid, user_firstname, user_lastname, user_email, user_username, newvalue, timestamp) = (r.name ->> %s, %s, %s, %s, %s, %s, %s, %s)
                FROM resource_instances r
                WHERE e.resourceinstanceid::uuid = r.resourceinstanceid
                AND transactionid = %s
                """,
                (
                    settings.LANGUAGE_CODE,
                    userid,
                    user_firstname,
                    user_lastname,
                    user_email,
                    user_username,
                    json_data,
                    datetime.now(),
                    loadid,
                ),
            )

        log_event_details(cursor, loadid, "done")

        cursor.execute(
            """UPDATE load_event SET (status, indexed_time, complete, successful) = (%s, %s, %s, %s) WHERE loadid = %s""",
            ("indexed", datetime.now(), True, True, loadid),
        )

    def return_value(self, cursor, resource_ids, node_id, old_id, new_id):
        select_query = "SELECT tileid, tiledata  FROM tiles WHERE resourceinstanceid = %s AND Not tiledata -> %s @> %s;"

        tiles_data = []
        tile_ids = []
        resources = []
        for resource_id in resource_ids:

            newid_json = f'["{str(new_id)}"]'
            cursor.execute(select_query, [resource_id, str(node_id), newid_json])
            rows = cursor.fetchall()

            for row in rows:
                tile_id = str(row[0])
                data = json.loads(row[1])
                if data and tile_id not in tile_ids:
                    key = str(node_id)
                else:
                    continue
                if key in data and isinstance(data[key], list):
                    for see_data in data[key]:
                        if len(see_data) == 36 and str(see_data) == str(old_id):
                            tiles_data.append(data)
                            tile_ids.append(tile_id)
                            resources.append(resource_id)
                elif key in data:
                    tiles_data.append(data)
                    tile_ids.append(tile_id)
                    resources.append(str(resource_id))

        return tile_ids, tiles_data, resources

    def edit_staged_data(
        self,
        cursor,
        graphid,
        nodeid,
        operation,
        languageold,
        resource_ids,
        language_new,
        oldid,
        newid,
        tiles,
        tile_datas,
    ):

        for resourceid, tile, tiledata in zip(resource_ids, tiles, tile_datas):
            result = {"success": False}
            value = {
                "graph": str(graphid),
                "node": str(nodeid),
                "new": str(newid),
                "old": tiledata,
                "languageold": languageold,
                "languagenew": language_new,
            }
            operation = "update"
            sql_query = "SELECT nodegroupid FROM public.nodes WHERE nodeid = %s"
            cursor.execute(sql_query, [str(nodeid)])
            node_group = cursor.fetchone()
            try:
                cursor.execute(
                    """INSERT INTO load_staging (nodegroupid, resourceid, tileid, value, loadid, nodegroup_depth, source_description, passes_validation, operation) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (
                        str(node_group[0]),
                        str(resourceid),
                        str(tile),
                        json.dumps(value),
                        str(self.loadid),
                        0,
                        "bulk_edit",
                        True,
                        operation,
                    ),
                )

                result["success"] = True
            except Exception as e:
                logger.error(e)
                result["message"] = _("Unable to edit staged data: {}").format(str(e))
                return result  # Exit early if an exception occurs
        for resourceid, tile, tile_data in zip(resource_ids, tiles, tile_datas):
            self.editor_log(
                cursor, str(tile), str(nodeid), str(resourceid), json.dumps(tile_data)
            )
        return result

    def all_node_by_conept(self, request):

        with connection.cursor() as cursor:
            select_nodes = "SELECT name, config, nodeid FROM nodes Where (datatype = 'concept-list' or datatype = 'concept') ORDER BY name ASC ;"
            # cursor.execute(select_nodes,[select_value[0]])
            cursor.execute(select_nodes)
            nodes = cursor.fetchall()
            all_node = []
            for node in nodes:
                name = json.loads(node[1])
                if name["rdmCollection"]:
                    all_node.append([node[0], name["rdmCollection"], node[2]])
        return {"success": True, "data": all_node}

    def get_graphs_node(self, request):
        graphid = request.POST.get("selectedgrapgh", None)
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

    def list_concepts(self, request):
        selected_node_info = request.POST.get("selectednode", None)
        if not selected_node_info:
            return {}

        selected_rdmCollection = json.loads(selected_node_info)["rdmCollection"]
        with connection.cursor() as cursor:
            select_nodes = """
                SELECT relations.conceptidto as conceptid, values_table.value as label, values_table.valueid as valueid
                FROM relations
                INNER JOIN (
                    SELECT conceptid, value, valueid
                    FROM public."values" 
                    WHERE valuetype = 'prefLabel'
                ) AS values_table ON relations.conceptidto = values_table.conceptid
                WHERE relations.conceptidfrom = %s;
            """
            cursor.execute(select_nodes, [selected_rdmCollection])
            conceptall = dictfetchall(cursor)
        return {
            "success": True,
            "data": conceptall,
        }

    def get_resourceids_from_search_url(self, search_url):
        request = HttpRequest()
        request.user = self.request.user
        request.method = "GET"
        request.GET["export"] = True
        validate = URLValidator()
        try:
            validate(search_url)
        except:
            raise
        params = parse_qs(urlsplit(search_url).query)
        for k, v in params.items():
            request.GET.__setitem__(k, v[0])
        response = search_results(request)
        results = json.loads(response.content)["results"]["hits"]["hits"]
        return [result["_source"]["resourceinstanceid"] for result in results]

    def replaceConcept(self, request):
        old = request.POST.get("conceptOld", None)
        new = request.POST.get("conceptNew", None)
        # all_child_concept = request.POST.get("allchildconcept", None)
        language_old = request.POST.get("vaoldlanguage", None)
        language_new = request.POST.get("vanewlanguage", None)
        # nodeid = request.POST.get("nodeid", None)
        selected_node_info = request.POST.get("selectednode", None)
        if not selected_node_info:
            return {}
        # selected_node = json.loads(selected_node_info)["nodeid"]
        nodeid = json.loads(selected_node_info)["nodeid"]

        search_url = request.POST.get("search_url", None)
        resourceids = None
        # items = all_child_concept.split(",")
        # id_name_pairs = []
        # if len(items) % 2 == 0:
        #     id_name_pairs = [[items[i], items[i + 1]] for i in range(0, len(items), 2)]
        # else:
        #     id_name_pairs = perth_items(items)
        # oldid = next((pair for pair in id_name_pairs if pair[1] == old), None)
        # newid = next((pair for pair in id_name_pairs if pair[1] == new), None)
        if search_url:
            try:
                resourceids = self.get_resourceids_from_search_url(search_url)
            except ValidationError:
                return {
                    "success": False,
                    "data": {
                        "title": _("Invalid Search Url"),
                        "message": _("Please, enter a valid search url"),
                    },
                }

        with connection.cursor() as cursor:
            # select_query = "SELECT valueid FROM values Where conceptid = %s and languageid = %s and value= %s;"
            # cursor.execute(select_query, [oldid[0], language_old, old])
            # valueid = cursor.fetchall()
            # oldid = valueid[0][0]
            # select_query = "SELECT valueid FROM values Where conceptid = %s and languageid = %s and value= %s;"
            # cursor.execute(select_query, [newid[0], language_new, new])
            # valueid = cursor.fetchall()
            # newid = valueid[0][0]

            oldid = old
            newid = new

            if resourceids:
                resources_id = tuple(resourceids)
                oldid_json = f'["{str(oldid)}"]'
                newid_json = f'["{str(newid)}"]'
                select_resource = "SELECT resourceinstanceid, tiledata, tileid FROM tiles WHERE tiledata -> %s @>%s AND resourceinstanceid in %s AND Not tiledata -> %s @> %s;"
                cursor.execute(
                    select_resource,
                    [str(nodeid), oldid_json, resources_id, str(nodeid), newid_json],
                )
                rows = cursor.fetchall()
                if len(rows) == 0:
                    select_resource = "SELECT resourceinstanceid, tiledata, tileid FROM tiles WHERE tiledata ->> %s = %s;"

                    cursor.execute(select_resource, [str(nodeid), str(oldid)])
                    rows = cursor.fetchall()
            else:
                oldid_json = f'["{str(oldid)}"]'
                newid_json = f'["{str(newid)}"]'
                select_resource = "SELECT resourceinstanceid, tiledata, tileid FROM tiles WHERE tiledata -> %s @>%s AND Not tiledata -> %s @> %s;"
                cursor.execute(
                    select_resource, [str(nodeid), oldid_json, str(nodeid), newid_json]
                )
                rows = cursor.fetchall()
                if len(rows) == 0:
                    select_resource = "SELECT resourceinstanceid, tiledata, tileid FROM tiles WHERE tiledata ->> %s = %s;"

                    cursor.execute(select_resource, [str(nodeid), str(oldid)])
                    rows = cursor.fetchall()

            information = []
            for row in rows:
                data = json.loads(row[1])
                if data:
                    key = str(nodeid)
                else:
                    break

                if key in data and isinstance(data[key], list):

                    for item in data[key]:
                        if len(item) == 36 and str(item) == str(oldid):
                            select_name = "SELECT name FROM resource_instances WHERE resourceinstanceid = %s;"
                            cursor.execute(select_name, [row[0]])
                            name = cursor.fetchone()
                            if name:
                                fulname = json.loads(name[0])
                                information.append(
                                    [
                                        str(row[0]),
                                        str(fulname.get("en", "")),
                                        f"{old}({language_old})",
                                        f"{new}({language_new})",
                                    ]
                                )
                elif key in data:
                    item = data[key]
                    if len(item) == 36 and str(item) == str(oldid):
                        select_name = "SELECT name FROM resource_instances WHERE resourceinstanceid = %s;"
                        cursor.execute(select_name, [row[0]])
                        name = cursor.fetchone()
                        if name:
                            fulname = json.loads(name[0])
                            information.append(
                                [
                                    str(row[0]),
                                    str(fulname.get("en", "")),
                                    f"{old}({language_old})",
                                    f"{new}({language_new})",
                                ]
                            )

        return {
            "success": True,
            "data": information,
        }

    def select_language(self, request):
        # import ipdb; ipdb.sset_trace()

        selected_conceptid = request.POST.get("selected_conceptid", None)
        langs = Value.objects.values_list("language_id", flat=True).filter(
            valueid=selected_conceptid
        )
        return {
            "success": True,
            "data": langs,
        }

    def get_default_language(self, request):
        return {"userLang": get_language()}

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
        selected_grapgh = request.POST.get("selectedgrapgh", None)
        select_node = request.POST.get("selectednode", None)
        new = request.POST.get("conceptNew", None)
        old = request.POST.get("conceptOld", None)
        language_old = request.POST.get("vaoldlanguage", None)
        language_new = request.POST.get("vanewlanguage", None)
        table = request.POST.get("table", None)
        load_details = {
            "graph": selected_grapgh,
            "node": select_node,
            "new": new,
            "old": old,
            "languageold": language_old,
            "languagenew": language_new,
        }
        resourcesid = []
        for resource in table.split(","):
            try:
                uuid.UUID(resource)
                resourcesid.append(resource)
            except ValueError:
                pass

        with connection.cursor() as cursor:
            event_created = self.create_load_event(cursor, load_details)
            if not event_created["success"]:
                self.log_event(cursor, "failed")
                return {"success": False, "data": event_created["message"]}
        use_celery_bulk_edit = True
        if use_celery_bulk_edit:
            response = self.run_load_task_async(request, self.loadid)
        return response

    @load_data_async
    def run_load_task_async(self, request):
        graphid = request.POST.get("selectedgrapgh", None)
        new = request.POST.get("conceptNew", None)
        old = request.POST.get("conceptOld", None)
        language_old = request.POST.get("vaoldlanguage", None)
        language_new = request.POST.get("vanewlanguage", None)
        table = request.POST.get("table", None)
        nodeid = request.POST.get("nodeid", None)
        all_child_concept = request.POST.get("allchildconcept", None)
        # saveid = request.POST.get("saveid", None)
        items = all_child_concept.split(",")
        id_name_pairs = []
        if len(items) % 2 == 0:
            id_name_pairs = [[items[i], items[i + 1]] for i in range(0, len(items), 2)]
        else:
            id_name_pairs = perth_items(items)
        oldid = next((pair for pair in id_name_pairs if pair[1] == old), None)
        newid = next((pair for pair in id_name_pairs if pair[1] == new), None)
        # items = saveid.split(",")
        id_name_pairs = []
        id_name_pairs = [[items[i], items[i + 1]] for i in range(0, len(items), 2)]
        graphid = next(
            (pair for pair in id_name_pairs if pair[1] == selected_grapgh), None
        )
        resourcesid = []
        for resource in table.split(","):
            try:
                uuid.UUID(resource)
                resourcesid.append(resource)
            except ValueError:
                pass
        if resourcesid:
            resourceids_json_string = json.dumps(resourcesid)
            resourceids = json.loads(resourceids_json_string)
        pattern = old
        operation = "replace"
        edit_task = edit_bulk_concept_data.apply_async(
            (
                self.userid,
                self.loadid,
                self.moduleid,
                graphid,
                nodeid,
                operation,
                language_old,
                pattern,
                new,
                resourceids,
                language_new,
                oldid,
                newid,
            ),
        )
        with connection.cursor() as cursor:
            cursor.execute(
                """UPDATE load_event SET taskid = %s WHERE loadid = %s""",
                (edit_task.task_id, self.loadid),
            )

    def run_load_task(
        self,
        userid,
        loadid,
        module_id,
        graphid,
        nodeid,
        operation,
        languageold,
        pattern,
        new_text,
        resourceids,
        language_new,
        oldid,
        newid,
    ):

        with connection.cursor() as cursor:
            self.log_event_details(cursor, "done|Staging the data for edit...")
            select_query = "SELECT valueid FROM values Where conceptid = %s and languageid = %s and valuetype = 'prefLabel';"
            cursor.execute(select_query, [oldid[0], languageold])
            valueid = cursor.fetchall()
            oldid = valueid[0][0]
            select_query = "SELECT valueid FROM values Where conceptid = %s and languageid = %s and valuetype = 'prefLabel';"
            cursor.execute(select_query, [newid[0], language_new])
            valueid = cursor.fetchall()
            newid = valueid[0][0]
            self.log_event_details(cursor, "done|Editing the data...")
            tile = self.return_value(cursor, resourceids, nodeid, oldid, newid)
            self.log_event_details(cursor, "done|returm data...")
            data_updated = self.edit_staged_data(
                cursor,
                graphid[0],
                nodeid,
                operation,
                languageold,
                tile[2],
                language_new,
                oldid,
                newid,
                tile[0],
                tile[1],
            )
            if data_updated["success"]:
                self.loadid = loadid  # currently redundant, but be certain
                # for resource in resourceids:
                tile = self.return_value(cursor, resourceids, nodeid, oldid, newid)
                self.save_tiles(
                    cursor,
                    loadid,
                    userid,
                    tile[0],
                    newid,
                    tile[1],
                    nodeid,
                    tile[2],
                    oldid,
                )
                return {"success": True, "data": "done"}
            else:
                self.log_event(cursor, "failed")
                return {
                    "success": False,
                    "data": {"title": _("Error"), "message": data_updated["message"]},
                }
