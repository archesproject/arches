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
import platform
import sys
import json
import subprocess
from os.path import isfile, join
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from django.conf import settings
from django.db import connection, transaction
from arches.app.utils.data_management.resource_graphs.exporter import get_graphs_for_export as resourceGraphExporter
from arches.app.utils.data_management.concepts.exporter import get_reference_data_for_export as referenceDataExporter
from arches.app.utils.data_management.resources.exporter import ResourceExporter as resourceDataExporter

class ArchesFileExporter(object):

	def __init__(self, file=None):
		pass

	def export_graphs(self, data_dir, graphids):
		"""
		Wrapper around arches.app.utils.data_management.resource_graphs.exporter method
		"""
		graph_data = resourceGraphExporter(graphids)
		self.write_to_file(graph_data, data_dir)

	def export_business_data(self, data_dir, resourceids):
		resource_exporter = resourceDataExporter('json')
		resource_data = resource_exporter.get_resources_for_export(resourceids)
		self.write_to_file(resource_data, data_dir)

	def export_metadata(self):
		os_type = platform.system()
		os_release = platform.release()
		cursor = connection.cursor()
		sql = "SELECT version()"

		try:
			cursor.execute(sql)
			db = cursor.fetchall()[0][0]
		except:
			db = 'No DB version found.'

		try:
			full_tag = subprocess.Popen("git log --pretty=format:'%h %ai' --abbrev-commit --date=short -1", cwd=settings.PACKAGE_ROOT,
			shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			tag = full_tag.stdout.readline().strip()
			print tag
		except:
			tag = 'git not found.'

		metadata = {'os': os_type, 'os version': os_release, 'db': db, 'git hash': tag}
		return metadata

	def export_all(self, data_dir, graphids, resourceids):
		"""
		Creates arches json export of resource graphs, concepts, and business data.
		"""
		data = {}
		data['graph'] = []
		data['business_data'] = []

		if graphids != False:
			graphs_for_export = resourceGraphExporter(graphids)['graph']
			data['graph'] = graphs_for_export

		if resourceids != False:
			resource_exporter = resourceDataExporter('json')
			resource_data_for_export = resource_exporter.get_resources_for_export(resourceids)['business_data']
			data['business_data'] = resource_data_for_export

		self.write_to_file(data, data_dir)


	def write_to_file(self, data, data_dir):
		data['metadata'] = self.export_metadata

		with open(os.path.join(data_dir), 'w') as export_json:
			json.dump(JSONDeserializer().deserialize(JSONSerializer().serialize(data)), export_json, sort_keys=True, indent=4)
