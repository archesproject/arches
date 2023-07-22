import json
import logging
from django.http import HttpResponse
from django.db import connection
from django.utils.translation import ugettext as _
from arches.app.models.models import GraphModel, Node
from arches.app.models.system_settings import settings
from arches.management.commands.etl_template import create_workbook
from openpyxl.writer.excel import save_virtual_workbook
from arches.app.etl_modules.branch_csv_importer import BranchCsvImporter

logger = logging.getLogger(__name__)

details = {
    "etlmoduleid": "357d11c8-ca38-40ec-926f-1946ccfceb92",
    "name": "Branch Excel Exporter",
    "description": "Export a Branch Excel file from Arches",
    "etl_type": "export",
    "component": "views/components/etl_modules/branch-excel-exporter",
    "componentname": "branch-excel-exporter",
    "modulename": "branch_excel_exporter.py",
    "classname": "BranchExcelExporter",
    "config": {"bgColor": "#f5c60a", "circleColor": "#f9dd6c"},
    "icon": "fa fa-upload",
    "slug": "branch-excel-exporter",
    "helpsortorder": 6,
    "helptemplate": "branch-excel-exporter-help"
}

class BranchExcelExporter(BranchCsvImporter):
    def __init__(self, request):
        self.request = request if request else None
        self.userid = request.user.id if request else None
        self.moduleid = request.POST.get("module") if request else None

    def get_graphs(self, request):
        graph_name_i18n = "name__" + settings.LANGUAGE_CODE
        graphs = (
            GraphModel.objects.all()
            .exclude(pk=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
            .exclude(isresource=False)
            .exclude(publication_id__isnull=True)
            .order_by(graph_name_i18n)
        )
        return {"success": True, "data": graphs}

    def get_node_lookup_by_id(self, nodes):
        lookup = {}
        for node in nodes:
            lookup[str(node.nodeid)] = {"alias": str(node.alias), "datatype": node.datatype, "config": node.config}
        return lookup

    def dictfetchall(self, cursor): 
        desc = cursor.description 
        return [
            dict(zip([col[0] for col in desc], row)) 
            for row in cursor.fetchall() 
        ]

    def export(self, request):
        load_id = request.POST.get("load_id")
        graph_id = request.POST.get("graph_id", None)
        resource_ids = request.POST.get("resource_ids", None)

        if resource_ids is None:
            with connection.cursor() as cursor:
                cursor.execute("""SELECT resourceinstanceid FROM resource_instances WHERE graphid = (%s)""", [graph_id])
                rows = cursor.fetchall()
                resource_ids = [ row[0] for row in rows ]

        with connection.cursor() as cursor:
            cursor.execute("""SELECT * FROM __get_nodegroup_tree_by_graph(%s)""", (graph_id,))
            nodegroup_lookup = self.dictfetchall(cursor)

            nodes = Node.objects.filter(graph_id=graph_id)
            node_lookup_by_id = self.get_node_lookup_by_id(nodes)
            tile_collection = dict()

            tile_tree_query = """
                WITH RECURSIVE tile_tree(tileid, parenttileid, tiledata, nodegroupid, depth) AS (
                    SELECT
                        t.tileid,
                        t.parenttileid,
                        t.tiledata,
                        t.nodegroupid,
                        0
                    FROM
                        tiles t
                    WHERE tileid = (%s)
                    UNION
                        SELECT
                            t.tileid,
                            t.parenttileid,
                            t.tiledata,
                            t.nodegroupid,
                            tt.depth + 1
                        FROM
                            tile_tree tt, tiles t
                        WHERE
                            t.parenttileid = tt.tileid
                )
                SEARCH DEPTH FIRST BY tileid SET ordercol
                SELECT * FROM tile_tree ORDER BY ordercol;
            """

            for resource_id in resource_ids:
                cursor.execute("""SELECT * FROM tiles WHERE parenttileid IS null AND resourceinstanceid = (%s)""", [resource_id])
                root_tiles = self.dictfetchall(cursor)
                for root_tile in root_tiles:
                    cursor.execute(tile_tree_query, [root_tile["tileid"]])
                    tile_tree = self.dictfetchall(cursor)
                    for tile in tile_tree:
                        root_nodegroup, nodegroup_alias = [
                            (ng["root_nodegroup"], ng["alias"]) for ng in nodegroup_lookup if ng["nodegroupid"] == tile["nodegroupid"]
                        ][0]
                        root_alias = [ng["alias"] for ng in nodegroup_lookup if ng["root_nodegroup"] == root_nodegroup][0]
                        tile["alias"] = nodegroup_alias
                        tile["resourceinstanceid"] = resource_id
                        tile_data = json.loads(tile['tiledata'])
                        for key, value in tile_data.items():
                            alias = node_lookup_by_id[key]["alias"]
                            tile[alias] = value
                        tile_collection.setdefault(root_alias, []).append(tile)

        wb = create_workbook(graph_id, tile_collection)
        response = HttpResponse(save_virtual_workbook(wb), content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = "attachment"
        return {"success": True, "raw": response}
