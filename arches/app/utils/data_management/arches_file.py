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
from arches.app.utils.data_management.resource_graphs.importer import import_graph as resourceGraphImporter
from arches.app.utils.data_management.concepts.importer import import_concepts as conceptImporter
from arches.app.utils.data_management.resource_graphs.exporter import export_graph as resourceGraphExporter

class ArchesFile(object):

	def __init__(self, file=None):
		self.graphs = ''
		self.reference_data = ''
		self.business_data = ''

		if not file:
			file = settings.RESOURCE_GRAPH_LOCATIONS
		else:
			file = [file]

		for path in file:
			if os.path.exists(path):
				if isfile(join(path)):
					with open(file[0], 'rU') as f:
						archesfile = JSONDeserializer().deserialize(f)
						self.graphs = archesfile['graph'][0]
						self.reference_data = archesfile['reference_data']
						self.business_data = archesfile['business_data']
				else:
					print file + ' is not a valid file'
			else:
				print path + ' is not a valid path'

	def import_graphs(self):
		"""
		Wrapper around arches.app.utils.data_management.resource_graphs.importer method.
		"""
		resourceGraphImporter(self.graphs)

	def import_concepts(self):
		"""
		Wrapper around arches.app.utils.data_management.concepts.importer method.
		"""
		conceptImporter(self.reference_data)

	def import_business_data(self):
		pass

	def import_all(self):
		pass


	def export_graphs(self, data_dir):
		"""
		Wrapper around arches.app.utils.data_management.resource_graphs.exporter method
		"""
		resourceGraphExporter(data_dir)

	def export_concepts(self):
		pass

	def export_business_data(self):
		pass

	def export_all(self):
		pass

# ArchesFile(path).import_graph