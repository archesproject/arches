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
from arches.app.models.models import (CardXNodeXWidget, NodeGroup, DDataType, Widget,
                                      ReportTemplate, Function, Ontology, OntologyClass)
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.models.models import GraphXMapping
from django.db import transaction


class GraphImportReporter:
    def __init__(self, graphs):
        self.name = ''
        self.resource_model = False
        self.graphs = len(graphs)
        self.graphs_saved = 0
        self.graph_id = ''

    def update_graphs_saved(self, count=1):
        self.graphs_saved += count

    def report_results(self):
        if self.resource_model is True:
            result = "Saved Resource Model: {0}"
        else:
            result = "Saved Branch: {0}"

        print result.format(self.name)


class GraphImportException(Exception):
    pass


def import_graph(graphs, overwrite_graphs=True):
    reporter = GraphImportReporter(graphs)

    def check_default_configs(default_configs, configs):
        if default_configs is not None:
            if configs is None:
                configs = {}
            else:
                try:
                    '' in configs  # Checking if configs is a dict-like object
                except AttributeError:
                    configs = JSONDeserializer().deserialize(configs)
            for default_key in default_configs:
                if default_key not in configs:
                    configs[default_key] = default_configs[default_key]
        return configs

    with transaction.atomic():
        errors = []
        for resource in graphs:
            try:
                if resource['ontology_id'] is not None:
                    if resource['ontology_id'] not in [str(f['ontologyid']) for f in Ontology.objects.all().values('ontologyid')]:
                        errors.append('The ontologyid of the graph you\'re trying to load does not exist in Arches.')

                reporter.name = resource['name']
                reporter.resource_model = resource['isresource']
                reporter.graph_id = resource['graphid']
                graph = Graph(resource)
                ontology_classes = [str(f['source']) for f in OntologyClass.objects.all().values('source')]

                for node in list(graph.nodes.values()):
                    if resource['ontology_id'] is not None:
                        if node.ontologyclass not in ontology_classes:
                            errors.append('The ontology class of this node does not exist in the indicated ontology scheme.')
                    node_config = node.config
                    default_config = DDataType.objects.get(datatype=node.datatype).defaultconfig
                    node.config = check_default_configs(default_config, node_config)

                if not hasattr(graph, 'cards'):
                    errors.append('{0} graph has no attribute cards'.format(graph.name))
                else:
                    if len(Graph.objects.filter(pk=graph.graphid)) == 0 or overwrite_graphs is True:
                        if hasattr(graph, 'reports'):
                            for report in graph.reports:
                                if report['active']:
                                    report_config = report['config']
                                    default_config = ReportTemplate.objects.get(
                                        templateid=report['template_id']
                                    ).defaultconfig
                                    graph.config = check_default_configs(default_config, report_config)
                                    graph.template_id = report['template_id']
                        graph.save()
                        reporter.update_graphs_saved()
                    else:
                        overwrite_input = raw_input('Overwrite {0} (Y/N) ? '.format(graph.name))
                        if overwrite_input.lower() in ('t', 'true', 'y', 'yes'):
                            graph.save()
                        else:
                            raise GraphImportException('{0} - already exists. Skipping import.'.format(graph.name))

                if not hasattr(graph, 'cards_x_nodes_x_widgets'):
                    errors.append('{0} graph has no attribute cards_x_nodes_x_widgets'.format(graph.name))
                else:
                    for card_x_node_x_widget in graph.cards_x_nodes_x_widgets:
                        card_x_node_x_widget_config = card_x_node_x_widget['config']
                        default_config = Widget.objects.get(widgetid=card_x_node_x_widget['widget_id']).defaultconfig
                        card_x_node_x_widget['config'] = check_default_configs(default_config, card_x_node_x_widget_config)
                        cardxnodexwidget = CardXNodeXWidget.objects.update_or_create(**card_x_node_x_widget)

                # try/except block here until all graphs have a resource_2_resource_constraints object.
                try:
                    if not hasattr(graph, 'resource_2_resource_constraints'):
                        errors.append('{0} graph has no attribute resource_2_resource_constraints'.format(graph.resource_2_resource_constraints))
                    else:
                        for resource_2_resource_constraint in graph.resource_2_resource_constraints:
                            resource2resourceconstraint = Resource2ResourceConstraint.objects.update_or_create(**resource_2_resource_constraint)
                except:
                    pass
            except Exception as e:
                print e

        return errors, reporter


def import_mapping_file(mapping_file):
    resource_model_id = mapping_file['resource_model_id']
    mapping = mapping_file

    GraphXMapping.objects.update_or_create(
        graph_id=uuid.UUID(str(resource_model_id)),
        mapping=mapping)
