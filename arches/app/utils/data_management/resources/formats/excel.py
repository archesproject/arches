import os
import sys
from io import BytesIO
from openpyxl import Workbook
from .csvfile import TileCsvWriter
from .format import Writer


class ExcelWriter(TileCsvWriter):
    def __init__(self, **kwargs):
        super(TileCsvWriter, self).__init__(**kwargs)

    def write_resources(self, graph_id=None, resourceinstanceids=None, **kwargs):
        super(TileCsvWriter, self).write_resources(graph_id=graph_id, resourceinstanceids=resourceinstanceids, **kwargs)

        csvs = TileCsvWriter().write_resources(graph_id=graph_id)
        wb = Workbook()

        for csv in csvs:
            # create a tab/worksheet for every csv file
            ws = wb.create_sheet(title=csv["name"].split(".csv")[0])
            for row in csv["outputfile"].getvalue().split("\r\n"):
                ws.append(row.split(","))
        # delete default blank first sheet in workbook
        del wb["Sheet"]

        # save virtual workbook so
        virtual_workbook = BytesIO()
        wb.save(virtual_workbook)

        excel_file_for_export = []
        excel_file_for_export.append({"name": self.file_name + ".xlsx", "outputfile": wb})

        return excel_file_for_export
