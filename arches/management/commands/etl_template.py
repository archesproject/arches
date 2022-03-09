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

from django.core.management.base import BaseCommand
from openpyxl import Workbook
from django.db import connection
from arches.app.models.graph import Graph
from arches.app.models.models import Node


class Command(BaseCommand):
    """
    Commands creating data templates

    """

    def add_arguments(self, parser):
        parser.add_argument(
            "-t", "--template", action="store", dest="template", default="branchcsv", help="Type of template you would like to create."
        )
        parser.add_argument(
            "-d", "--dest", action="store", dest="dest", default="", help="Directory where template should be saved"
        )
        parser.add_argument(
            "-g", "--graph", action="store", dest="graph", default="", help="Graph for which you would like an import template"
        )

    def handle(self, *args, **options):
        self.create_template(template=options["template"], dest=options["dest"], graphid=options["graph"])

    def create_template(self, template, dest, graphid):
        wb = Workbook()
        columns = ("root_nodegroupid", "nodegroupid", "parent_nodegroupid", "alias", "name", "depth", "path", "cardinality")
        with connection.cursor() as cursor:
            cursor.execute("""SELECT * FROM __get_nodegroup_tree_by_graph(%s)""", (graphid,))
            rows = cursor.fetchall()
            first_sheet = True
            for row in rows:
                details = dict(zip(columns, row))
                tab = '    ' * details["depth"]
                nodes = Node.objects.filter(nodegroup_id=details['nodegroupid']).values('datatype', 'alias')
                data_collecting_nodes = [node['alias'] for node in nodes if node['datatype'] != 'semantic']
                if details["depth"] == 0:
                    if first_sheet == True:
                        sheet = wb.active
                        sheet.title = details["name"]
                        first_sheet = False
                    else:
                        sheet = wb.create_sheet(title=details["name"])
                    row_number = 2
                    sheet[f"A1"] = "resource_id"
                    sheet[f"B1"] = "node group"
                    sheet[f"B2"] = f'{tab}{details["alias"]}  ({details["cardinality"]})'
                    for i, node_alias in enumerate(data_collecting_nodes):
                        sheet.cell(column=i + 3, row=row_number, value=f"{node_alias}")
                else:
                    row_number += 1
                    sheet[f"B{row_number}"]	= f'{tab}{details["alias"]}  ({details["cardinality"]})'
                    for i, node_alias in enumerate(data_collecting_nodes):
                        sheet.cell(column=i + 3, row=row_number, value=f"{node_alias}")
                dest_filename = dest
                wb.save(filename = dest_filename)
