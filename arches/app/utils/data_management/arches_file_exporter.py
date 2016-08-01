'''
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
'''

import os
import sys
import json
from os.path import isfile, join
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from django.conf import settings
from arches.app.utils.data_management.resource_graphs.exporter import write_graph as resourceGraphExporter

class ArchesFileExporter(object):

	def __init__(self, file=None):
		pass

	def export_graphs(self, data_dir, resource_list):
		"""
		Wrapper around arches.app.utils.data_management.resource_graphs.exporter method
		"""
		resourceGraphExporter(data_dir, resource_list)

	def export_concepts(self):
		pass

	def export_business_data(self):
		pass

	def export_all(self):
		pass

# ArchesFile(path).import_graph