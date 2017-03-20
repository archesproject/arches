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
import uuid
from arches.app.models.graph import Graph
from arches.app.models.models import CardXNodeXWidget, Form, FormXCard, Report, NodeGroup, DDataType, Widget, ReportTemplate, Function
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.models.models import GraphXMapping
from django.db import transaction

class GraphImportReporter:
    def __init__(self, graphs):
        self.name = ''
        self.resource_model = False
        self.graphs = len(graphs)
        self.graphs_saved = 0
        self.reports_saved = 0
        self.forms_saved = 0

    def update_graphs_saved(self, count=1):
        self.graphs_saved += count

    def update_forms_saved(self, count=1):
        self.forms_saved += count

    def update_reports_saved(self, count=1):
        self.reports_saved += count

    def report_results(self):
        if self.resource_model == True:
            result = "Saved Resource Model: {0}, Forms: {1}, Reports: {2}"
        else:
            result = "Saved Branch: {0}"

        print result.format(self.name, self.forms_saved, self.reports_saved)

def import_graph(graphs):
    reporter = GraphImportReporter(graphs)
    def check_default_configs(default_configs, configs):
        if default_configs != None:
            if configs == None:
                configs = {}
            else:
                try:
                    configs.has_key('') #Checking if configs is a dict-like object
                except AttributeError:
                    configs = JSONDeserializer().deserialize(configs)
            for default_key in default_configs:
                if default_key not in configs:
                    configs[default_key] = default_configs[default_key]
        return configs


    with transaction.atomic():
        errors = []
        for resource in graphs:
            reporter.name = resource['name']
            reporter.resource_model = resource['isresource']
            graph = Graph(resource)

            for node in graph.nodes.values():
                node_config = node.config
                default_config = DDataType.objects.get(datatype=node.datatype).defaultconfig
                node.config = check_default_configs(default_config, node_config)

            if not hasattr(graph, 'cards'):
                errors.append('{0} graph has no attribute cards'.format(graph.name))
            else:
                if graph.cards == [] or graph.cards == {}:
                    errors.append('{0} graph has no cards'.format(graph.name))
                else:
                    graph.save()
                    reporter.update_graphs_saved()

            if not hasattr(graph, 'cards_x_nodes_x_widgets'):
                errors.append('{0} graph has no attribute cards_x_nodes_x_widgets'.format(graph.name))
            else:
                for card_x_node_x_widget in graph.cards_x_nodes_x_widgets:
                    card_x_node_x_widget_config = card_x_node_x_widget['config']
                    default_config = Widget.objects.get(widgetid=card_x_node_x_widget['widget_id']).defaultconfig
                    card_x_node_x_widget['config'] = check_default_configs(default_config, card_x_node_x_widget_config)
                    cardxnodexwidget = CardXNodeXWidget.objects.update_or_create(**card_x_node_x_widget)

            if not hasattr(graph, 'forms'):
                errors.append('{0} graph has no attribute forms'.format)
            else:
                for form in graph.forms:
                    form = Form.objects.update_or_create(**form)
                    reporter.update_forms_saved()

            if not hasattr(graph, 'forms_x_cards'):
                errors.append('{0} graph has no attribute forms_x_cards'.format(graph.name))
            else:
                for form_x_card in graph.forms_x_cards:
                    formxcard = FormXCard.objects.update_or_create(**form_x_card)

            if not hasattr(graph, 'reports'):
                errors.append('{0} graph has no attribute reports'.format(graph.name))
            else:
                for report in graph.reports:
                    report_config = report['config']
                    default_config = ReportTemplate.objects.get(templateid=report['template_id']).defaultconfig
                    report['config'] = check_default_configs(default_config, report_config)
                    report = Report.objects.update_or_create(**report)
                    reporter.update_reports_saved()

            # try/except block here until all graphs have a resource_2_resource_constraints object.
            try:
                if not hasattr(graph, 'resource_2_resource_constraints'):
                    errors.append('{0} graph has no attribute resource_2_resource_constraints'.format(graph.resource_2_resource_constraints))
                else:
                    for resource_2_resource_constraint in graph.resource_2_resource_constraints:
                        resource2resourceconstraint = Resource2ResourceConstraint.objects.update_or_create(**resource_2_resource_constraint)
            except:
                pass

        return errors, reporter

def import_mapping_file(mapping_file):
    resource_model_id = mapping_file['resource_model_id']
    mapping = mapping_file

    GraphXMapping.objects.update_or_create(
        graph_id=uuid.UUID(str(resource_model_id)),
        mapping=mapping)
