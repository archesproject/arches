import os
import sys
import csv
from io import BytesIO
from openpyxl import Workbook
from .csvfile import TileCsvWriter
from .format import Writer


class ExcelWriter(TileCsvWriter):
    def __init__(self, **kwargs):
        super(TileCsvWriter, self).__init__(**kwargs)

    def write_resources(self, graph_id=None, resourceinstanceids=None, **kwargs):
        writer = TileCsvWriter()
        csv_files = writer.write_resources(
            graph_id=graph_id, resourceinstanceids=resourceinstanceids, **kwargs
        )
        writer.set_file_name()

        wb = Workbook()

        for csv_file in csv_files:
            # create a tab/worksheet for every csv file
            csv_file_name, extension = os.path.splitext(csv_file["name"])
            ws = wb.create_sheet(title=csv_file_name)
            for row in csv.reader(csv_file["outputfile"].getvalue().split("\r\n")):
                ws.append(row)
        # delete default blank first sheet in workbook
        del wb["Sheet"]

        virtual_workbook = BytesIO()
        wb.save(virtual_workbook)

        excel_file_for_export = []
        excel_file_for_export.append(
            {"name": writer.file_name + ".xlsx", "outputfile": wb}
        )

        return excel_file_for_export
