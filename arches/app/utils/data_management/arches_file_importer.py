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
from arches.app.utils.data_management.concepts.importer import import_reference_data as conceptImporter
from arches.app.utils.data_management.resources.importer import import_business_data as businessDataImporter


class ArchesFileImporter(object):

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
						if 'graph' in archesfile.keys():
							self.graphs = archesfile['graph']
						if 'reference_data' in archesfile.keys():
							self.reference_data = archesfile['reference_data']
						if 'business_data' in archesfile.keys():
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

	def import_reference_data(self):
		"""
		Wrapper around arches.app.utils.data_management.concepts.importer method.
		"""
		conceptImporter(self.reference_data)

	def import_business_data(self):
		"""
		Wrapper around arches.app.utils.data_management.resources.importer method.
		"""
		businessDataImporter(self.business_data)

	def import_all(self):
		pass
