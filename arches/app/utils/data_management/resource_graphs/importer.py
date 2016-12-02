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
from arches.app.models.models import CardXNodeXWidget, Form, FormXCard, Report, NodeGroup
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from django.db import transaction

def import_graph(graphs):
	with transaction.atomic():
		errors = []
		for resource in graphs:
			graph = Graph(resource)

			if not hasattr(graph, 'cards'):
				errors.append('{0} graph has no attribute cards'.format(graph.name))
			else:
				if graph.cards == [] or graph.cards == {}:
					errors.append('{0} graph has no cards'.format(graph.name))
				else:
					graph.save()

			if not hasattr(graph, 'cards_x_nodes_x_widgets'):
				errors.append('{0} graph has no attribute cards_x_nodes_x_widgets'.format(graph.name))
			else:
				for	card_x_node_x_widget in graph.cards_x_nodes_x_widgets:
					cardxnodexwidget = CardXNodeXWidget.objects.create(**card_x_node_x_widget)
					cardxnodexwidget.save()

			if not hasattr(graph, 'forms'):
				errors.append('{0} graph has no attribute forms'.format)
			else:
				for form in graph.forms:
					form = Form.objects.create(**form)
					form.save()

			if not hasattr(graph, 'forms_x_cards'):
				errors.append('{0} graph has no attribute forms_x_cards'.format(graph.name))
			else:
				for form_x_card in graph.forms_x_cards:
					formxcard = FormXCard.objects.create(**form_x_card)
					formxcard.save()

			if not hasattr(graph, 'reports'):
				errors.append('{0} graph has no attribute reports'.format(graph.name))
			else:
				for report in graph.reports:
					report = Report.objects.create(**report)
					report.save()

		return errors
