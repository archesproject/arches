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

import sys
from arches.app.models.graph import Graph
from arches.app.models.models import CardXNodeXWidget
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from django.db import transaction

def import_graph(graphs):
	with transaction.atomic():
		for resource in graphs:
			graph = Graph(resource)
			graph.save()

			if not hasattr(graph, 'cards_x_nodes_x_widgets'):
				print '*********This graph has no attribute cards_x_nodes_x_widgets*********'
				sys.exit()
			else:
				for	card_x_node_x_widget in graph.cards_x_nodes_x_widgets:
					functions = card_x_node_x_widget['functions']
					card_x_node_x_widget.pop('functions', None)
					cardxnodexwidget = CardXNodeXWidget.objects.create(**card_x_node_x_widget)
					cardxnodexwidget.save()
					cardxnodexwidget.functions.set(functions)

			return Graph
